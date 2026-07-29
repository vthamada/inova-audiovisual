from __future__ import annotations

import json
import os
import shutil
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, cast

import yaml

from inova_av.adapters.storage import LocalImmutableStorage
from inova_av.domain.hashing import sha256_file
from inova_av.domain.media import MediaProbe, ProxySettings
from inova_av.domain.states import ProjectState, require_transition
from inova_av.observability.audit import append_audit_event
from inova_av.ports.providers import StorageProvider
from inova_av.schemas.registry import load_document, validate_document


class MediaTools(Protocol):
    @property
    def ffmpeg_version(self) -> str: ...

    @property
    def ffprobe_version(self) -> str: ...

    def probe(self, path: Path) -> MediaProbe: ...

    def create_proxy(self, source: Path, destination: Path, profile: ProxySettings) -> None: ...


@dataclass(frozen=True, slots=True)
class IngestSettings:
    allowed_extensions: frozenset[str]
    max_source_bytes: int
    min_free_bytes: int
    copy_chunk_bytes: int
    probe_timeout_seconds: int
    proxy: ProxySettings

    def __post_init__(self) -> None:
        if not self.allowed_extensions or any(
            not extension.startswith(".") or extension != extension.lower()
            for extension in self.allowed_extensions
        ):
            raise ValueError("Extensões de ingestão devem ser minúsculas e iniciar com ponto")
        if (
            self.max_source_bytes <= 0
            or self.min_free_bytes < 0
            or self.probe_timeout_seconds <= 0
        ):
            raise ValueError("Limites de armazenamento inválidos")
        if self.copy_chunk_bytes < 64 * 1024:
            raise ValueError("Chunk de cópia deve ter pelo menos 64 KiB")

    @classmethod
    def from_config(cls, value: Mapping[str, Any]) -> IngestSettings:
        proxy = cast(Mapping[str, Any], value["proxy"])
        return cls(
            allowed_extensions=frozenset(str(item) for item in value["allowed_extensions"]),
            max_source_bytes=int(value["max_source_bytes"]),
            min_free_bytes=int(value["min_free_bytes"]),
            copy_chunk_bytes=int(value["copy_chunk_bytes"]),
            probe_timeout_seconds=int(value["probe_timeout_seconds"]),
            proxy=ProxySettings(
                width=int(proxy["width"]),
                height=int(proxy["height"]),
                fps=int(proxy["fps"]),
                video_codec=str(proxy["video_codec"]),
                audio_codec=str(proxy["audio_codec"]),
                crf=int(proxy["crf"]),
                preset=str(proxy["preset"]),
                audio_bitrate=str(proxy["audio_bitrate"]),
                timeout_seconds=int(proxy["timeout_seconds"]),
            ),
        )


@dataclass(frozen=True, slots=True)
class IngestResult:
    status: str
    project_id: str
    run_id: str
    manifest_file: str
    source_sha256: str | None
    source_file: str | None
    proxy_file: str | None
    reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "project_id": self.project_id,
            "run_id": self.run_id,
            "manifest_file": self.manifest_file,
            "source_sha256": self.source_sha256,
            "source_file": self.source_file,
            "proxy_file": self.proxy_file,
            "reason": self.reason,
        }


def ingest_project(
    *,
    workspace_root: Path,
    project_directory: Path,
    source: Path,
    authorized_by: str,
    settings: IngestSettings,
    media_tools: MediaTools,
    storage: StorageProvider | None = None,
    now: Callable[[], datetime] | None = None,
) -> IngestResult:
    clock = now or (lambda: datetime.now(UTC))
    started = _utc(clock())
    run_id = f"INGEST-{started.strftime('%Y%m%dT%H%M%S%fZ')}-{uuid.uuid4().hex[:8]}"
    actor = authorized_by.strip()
    if not actor:
        raise ValueError("Confirmação nominal de autorização é obrigatória")

    if project_directory.is_symlink():
        raise ValueError("Diretório do projeto não pode ser symlink")
    workspace = workspace_root.resolve(strict=True)
    project = project_directory.resolve(strict=True)
    if not project.is_relative_to(workspace):
        raise ValueError("Diretório do projeto está fora do workspace permitido")
    project_path = project / "project.yaml"
    project_document = _load_project(project_path)
    project_id = str(project_document["project_id"])
    if project_document["status"] != ProjectState.RECEIVED.value:
        raise ValueError("Projeto deve estar no estado received para ingestão")

    source_path = source.resolve(strict=True)
    if source.is_symlink() or not source_path.is_file():
        raise ValueError("Origem deve ser um arquivo regular e não pode ser symlink")

    source_size = source_path.stat().st_size
    extension = source_path.suffix.lower()
    source_sha256: str | None = None
    stage = "receive"
    staging = project / f".ingest-{run_id}"
    immutable_storage = storage or LocalImmutableStorage()

    try:
        if source_size <= 0:
            raise ValueError("Arquivo de origem está vazio")
        if source_size > settings.max_source_bytes:
            raise ValueError("Arquivo de origem excede o limite configurado")
        if extension not in settings.allowed_extensions:
            source_sha256 = sha256_file(source_path)
            raise ValueError(f"extensão não permitida: {extension or '<sem extensão>'}")
        required_free = source_size * 2 + settings.min_free_bytes
        if shutil.disk_usage(project).free < required_free:
            raise OSError("Espaço livre insuficiente para original, proxy e margem de segurança")
        if staging.exists():
            raise FileExistsError("Diretório temporário de ingestão já existe")
        staging.mkdir()

        stage = "copy"
        temporary_source = staging / f"source-upload{extension}"
        copy_result = immutable_storage.put_immutable(
            source_path, temporary_source, settings.copy_chunk_bytes
        )
        source_sha256 = copy_result.sha256
        stored_name = f"source-{source_sha256[:12]}{extension}"
        staged_source = staging / stored_name
        temporary_source.replace(staged_source)
        source_relative = f"01_inbox/{stored_name}"

        stage = "probe"
        probe = media_tools.probe(staged_source)
        if probe.size_bytes != copy_result.size_bytes:
            raise ValueError("Tamanho informado pelo FFprobe diverge da cópia")
        generated_at = _iso(_utc(clock()))
        technical_report = probe.to_document(
            source_file=source_relative,
            source_sha256=source_sha256,
            generated_at=generated_at,
            ffprobe_version=media_tools.ffprobe_version,
        )
        _write_validated_json(staging / "technical-report.json", "media-probe", technical_report)

        stage = "proxy"
        staged_proxy = staging / "proxy.mp4"
        media_tools.create_proxy(staged_source, staged_proxy, settings.proxy)
        proxy_sha256 = sha256_file(staged_proxy)
        proxy_probe = media_tools.probe(staged_proxy)
        tolerance = max(0.5, 2 / settings.proxy.fps)
        if abs(proxy_probe.duration_seconds - probe.duration_seconds) > tolerance:
            raise ValueError("Duração do proxy diverge da origem além da tolerância")
        proxy_report = proxy_probe.to_document(
            source_file="02_processing/proxy.mp4",
            source_sha256=proxy_sha256,
            generated_at=_iso(_utc(clock())),
            ffprobe_version=media_tools.ffprobe_version,
        )
        _write_validated_json(
            staging / "proxy-technical-report.json", "media-probe", proxy_report
        )

        stage = "commit"
        inbox = project / "01_inbox"
        processing = project / "02_processing"
        if inbox.exists() or processing.exists():
            raise FileExistsError("destino já existe; ingestão não sobrescreve artefatos")

        manifest = _validated_manifest(
            run_id=run_id,
            project_id=project_id,
            status="validated",
            started_at=_iso(started),
            finished_at=_iso(_utc(clock())),
            actor=actor,
            source_name=source_path.name,
            source_size=copy_result.size_bytes,
            source_sha256=source_sha256,
            source_file=source_relative,
            technical_report="02_processing/technical-report.json",
            proxy={
                "path": "02_processing/proxy.mp4",
                "sha256": proxy_sha256,
                "technical_report": "02_processing/proxy-technical-report.json",
            },
            quarantine=None,
            media_tools=media_tools,
        )
        _write_validated_json(
            staging / "ingest-manifest.json", "ingest-manifest", manifest
        )
    except (FileExistsError, OSError, RuntimeError, ValueError) as exc:
        reason = _safe_reason(str(exc), source_path=source_path, project=project)
        return _quarantine(
            project=project,
            project_document=project_document,
            project_id=project_id,
            run_id=run_id,
            actor=actor,
            started_at=started,
            finished_at=_utc(clock()),
            source_name=source_path.name,
            source_size=source_size,
            source_sha256=source_sha256,
            staging=staging,
            stage=stage,
            reason=reason,
            media_tools=media_tools,
        )

    staged_inbox = staging / "01_inbox"
    staged_processing = staging / "02_processing"
    staged_inbox.mkdir()
    staged_processing.mkdir()
    staged_source.replace(staged_inbox / staged_source.name)
    for name in (
        "technical-report.json",
        "proxy.mp4",
        "proxy-technical-report.json",
        "ingest-manifest.json",
    ):
        (staging / name).replace(staged_processing / name)

    staged_inbox.replace(project / "01_inbox")
    try:
        staged_processing.replace(project / "02_processing")
    except Exception:
        (project / "01_inbox").replace(staged_inbox)
        raise
    staging.rmdir()

    _update_project(
        project_path,
        project_document,
        status=ProjectState.VALIDATED,
        source_name=source_path.name,
        source_sha256=source_sha256,
        operator=actor,
    )
    manifest_path = project / "02_processing" / "ingest-manifest.json"
    artifact_hashes = {
        "source": source_sha256,
        "proxy": proxy_sha256,
        "technical_report": sha256_file(project / "02_processing" / "technical-report.json"),
        "proxy_report": sha256_file(
            project / "02_processing" / "proxy-technical-report.json"
        ),
        "manifest": sha256_file(manifest_path),
    }
    _append_transition_event(
        project=project,
        project_id=project_id,
        run_id=run_id,
        actor=actor,
        occurred_at=_utc(clock()),
        target=ProjectState.VALIDATED,
        reason=None,
        artifact_hashes=artifact_hashes,
    )
    return IngestResult(
        status="validated",
        project_id=project_id,
        run_id=run_id,
        manifest_file="02_processing/ingest-manifest.json",
        source_sha256=source_sha256,
        source_file=source_relative,
        proxy_file="02_processing/proxy.mp4",
        reason=None,
    )


def _quarantine(
    *,
    project: Path,
    project_document: dict[str, Any],
    project_id: str,
    run_id: str,
    actor: str,
    started_at: datetime,
    finished_at: datetime,
    source_name: str,
    source_size: int,
    source_sha256: str | None,
    staging: Path,
    stage: str,
    reason: str,
    media_tools: MediaTools,
) -> IngestResult:
    quarantine_root = project / "99_quarantine"
    if quarantine_root.exists() and (
        not quarantine_root.is_dir() or quarantine_root.is_symlink()
    ):
        raise OSError("Diretório de quarentena é inseguro")
    quarantine_root.mkdir(exist_ok=True)
    quarantine_dir = quarantine_root / run_id
    if quarantine_dir.exists():
        raise FileExistsError("Destino de quarentena já existe")
    if staging.exists():
        staging.replace(quarantine_dir)
    else:
        quarantine_dir.mkdir()

    copied_sources = sorted(quarantine_dir.glob("source-*"))
    stored_path = (
        f"99_quarantine/{run_id}/{copied_sources[0].name}" if copied_sources else None
    )
    technical_name = "technical-report.json"
    technical_path = (
        f"99_quarantine/{run_id}/{technical_name}"
        if (quarantine_dir / technical_name).is_file()
        else None
    )
    proxy_path = quarantine_dir / "proxy.mp4"
    proxy_report_path = quarantine_dir / "proxy-technical-report.json"
    proxy: dict[str, str] | None = None
    if proxy_path.is_file() and proxy_report_path.is_file():
        proxy = {
            "path": f"99_quarantine/{run_id}/proxy.mp4",
            "sha256": sha256_file(proxy_path),
            "technical_report": f"99_quarantine/{run_id}/proxy-technical-report.json",
        }

    manifest = _validated_manifest(
        run_id=run_id,
        project_id=project_id,
        status="quarantined",
        started_at=_iso(started_at),
        finished_at=_iso(finished_at),
        actor=actor,
        source_name=source_name,
        source_size=source_size,
        source_sha256=source_sha256,
        source_file=stored_path,
        technical_report=technical_path,
        proxy=proxy,
        quarantine={
            "path": f"99_quarantine/{run_id}",
            "stage": stage,
            "reason": reason,
        },
        media_tools=media_tools,
    )
    manifest_path = quarantine_dir / "ingest-manifest.json"
    _write_validated_json(manifest_path, "ingest-manifest", manifest)
    _update_project(
        project / "project.yaml",
        project_document,
        status=ProjectState.QUARANTINED,
        source_name=source_name,
        source_sha256=source_sha256,
        operator=actor,
    )
    artifacts = {"manifest": sha256_file(manifest_path)}
    if source_sha256 is not None:
        artifacts["source"] = source_sha256
    _append_transition_event(
        project=project,
        project_id=project_id,
        run_id=run_id,
        actor=actor,
        occurred_at=finished_at,
        target=ProjectState.QUARANTINED,
        reason=reason,
        artifact_hashes=artifacts,
    )
    return IngestResult(
        status="quarantined",
        project_id=project_id,
        run_id=run_id,
        manifest_file=f"99_quarantine/{run_id}/ingest-manifest.json",
        source_sha256=source_sha256,
        source_file=stored_path,
        proxy_file=proxy["path"] if proxy else None,
        reason=reason,
    )


def _validated_manifest(
    *,
    run_id: str,
    project_id: str,
    status: str,
    started_at: str,
    finished_at: str,
    actor: str,
    source_name: str,
    source_size: int,
    source_sha256: str | None,
    source_file: str | None,
    technical_report: str | None,
    proxy: dict[str, str] | None,
    quarantine: dict[str, str] | None,
    media_tools: MediaTools,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "project_id": project_id,
        "status": status,
        "started_at": started_at,
        "finished_at": finished_at,
        "authorization": {"confirmed_by": actor, "confirmed_at": started_at},
        "source": {
            "original_filename": source_name,
            "size_bytes": source_size,
            "sha256": source_sha256,
            "stored_path": source_file,
        },
        "technical_report": technical_report,
        "proxy": proxy,
        "quarantine": quarantine,
        "tool_versions": {
            "ffmpeg": _safe_version(lambda: media_tools.ffmpeg_version),
            "ffprobe": _safe_version(lambda: media_tools.ffprobe_version),
        },
        "warnings": [],
    }


def _safe_version(loader: Callable[[], str]) -> str | None:
    try:
        return loader()
    except (FileNotFoundError, OSError, RuntimeError, ValueError):
        return None


def _load_project(path: Path) -> dict[str, Any]:
    value = load_document(path)
    if not isinstance(value, dict):
        raise ValueError("project.yaml deve conter um objeto")
    document = cast(dict[str, Any], value)
    issues = validate_document("project", document)
    if issues:
        raise ValueError("Projeto inválido: " + "; ".join(issue.render() for issue in issues))
    return document


def _update_project(
    path: Path,
    document: dict[str, Any],
    *,
    status: ProjectState,
    source_name: str,
    source_sha256: str | None,
    operator: str,
) -> None:
    require_transition(ProjectState(str(document["status"])), status)
    updated = cast(dict[str, Any], json.loads(json.dumps(document)))
    updated["status"] = status.value
    source = cast(dict[str, Any], updated["source"])
    source["filename"] = source_name
    source["sha256"] = source_sha256
    source["operator"] = operator
    issues = validate_document("project", updated)
    if issues:
        raise ValueError("Projeto atualizado inválido: " + "; ".join(i.render() for i in issues))
    _write_yaml_atomic(path, updated)


def _write_validated_json(path: Path, schema: str, document: dict[str, Any]) -> None:
    issues = validate_document(schema, document)
    if issues:
        raise ValueError(
            f"Documento {schema} inválido: " + "; ".join(issue.render() for issue in issues)
        )
    _write_text_atomic(
        path, json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


def _write_yaml_atomic(path: Path, document: dict[str, Any]) -> None:
    _write_text_atomic(path, yaml.safe_dump(document, allow_unicode=True, sort_keys=False))


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _append_transition_event(
    *,
    project: Path,
    project_id: str,
    run_id: str,
    actor: str,
    occurred_at: datetime,
    target: ProjectState,
    reason: str | None,
    artifact_hashes: dict[str, str],
) -> None:
    append_audit_event(
        project / "audit.jsonl",
        {
            "schema_version": "1.0",
            "event_id": f"EVT-{uuid.uuid4()}",
            "occurred_at": _iso(occurred_at),
            "project_id": project_id,
            "run_id": run_id,
            "actor": actor,
            "event_type": (
                "ingest_completed" if target is ProjectState.VALIDATED else "ingest_failed"
            ),
            "previous_state": ProjectState.RECEIVED.value,
            "new_state": target.value,
            "reason": reason,
            "artifact_hashes": artifact_hashes,
        },
    )


def _safe_reason(message: str, *, source_path: Path, project: Path) -> str:
    sanitized = message.replace(str(source_path), source_path.name).replace(
        str(project), "<project>"
    )
    sanitized = " ".join(sanitized.split())[:1000]
    return sanitized or "Falha de ingestão não detalhada"


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("Clock de ingestão deve retornar datetime com timezone")
    return value.astimezone(UTC)


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")
