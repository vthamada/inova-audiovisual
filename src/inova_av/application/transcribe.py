from __future__ import annotations

import json
import os
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from inova_av.domain.hashing import sha256_file
from inova_av.domain.states import ProjectState, require_transition
from inova_av.observability.audit import append_audit_event
from inova_av.ports.providers import TranscriptionProvider, TranscriptionRequest
from inova_av.schemas.registry import load_document, validate_document


@dataclass(frozen=True, slots=True)
class TranscriptionSettings:
    provider: str
    provider_version: str
    model: str
    model_revision: str
    device: str
    compute_type: str
    language: str
    local_files_only: bool
    vad_filter: bool
    vad_min_silence_duration_ms: int

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (
                self.provider,
                self.provider_version,
                self.model,
                self.device,
                self.compute_type,
                self.language,
            )
        ):
            raise ValueError("Configura\u00e7\u00e3o de transcri\u00e7\u00e3o incompleta")
        if not self.model_revision.strip():
            raise ValueError(
                "Revis\u00e3o do modelo local deve ser registrada antes da transcri\u00e7\u00e3o"
            )
        if not self.local_files_only:
            raise ValueError("Transcri\u00e7\u00e3o requer local_files_only=true")
        if self.language != "pt":
            raise ValueError("A configura\u00e7\u00e3o inicial aceita somente idioma pt")
        if not self.vad_filter or self.vad_min_silence_duration_ms < 500:
            raise ValueError(
                "A configura\u00e7\u00e3o inicial requer VAD conservador de pelo menos 500 ms"
            )

    @classmethod
    def from_config(cls, value: Mapping[str, Any]) -> TranscriptionSettings:
        return cls(
            provider=str(value["provider"]),
            provider_version=str(value["provider_version"]),
            model=str(value["model"]),
            model_revision=(
                str(value["model_revision"])
                if isinstance(value["model_revision"], str)
                else ""
            ),
            device=str(value["device"]),
            compute_type=str(value["compute_type"]),
            language=str(value["language"]),
            local_files_only=bool(value["local_files_only"]),
            vad_filter=bool(value["vad_filter"]),
            vad_min_silence_duration_ms=int(value["vad_min_silence_duration_ms"]),
        )


@dataclass(frozen=True, slots=True)
class TranscriptionResult:
    project_id: str
    run_id: str
    transcript_file: str
    transcript_sha256: str

    def to_dict(self) -> dict[str, str]:
        return {
            "status": "transcribed",
            "project_id": self.project_id,
            "run_id": self.run_id,
            "transcript_file": self.transcript_file,
            "transcript_sha256": self.transcript_sha256,
        }


def transcribe_project(
    *,
    workspace_root: Path,
    project_directory: Path,
    actor: str,
    settings: TranscriptionSettings,
    provider: TranscriptionProvider,
    now: Callable[[], datetime] | None = None,
) -> TranscriptionResult:
    """Create the first review-pending transcript from an already ingested project.

    The provider is injected so this use case stays offline-capable and testable without
    installing a model. Provider errors leave the project in ``validated`` for an explicit
    retry; they are not treated as permission to change or publish any artifact.
    """

    clock = now or (lambda: datetime.now(UTC))
    started = _utc(clock())
    run_id = f"TRANSCRIBE-{started.strftime('%Y%m%dT%H%M%S%fZ')}-{uuid.uuid4().hex[:8]}"
    reviewer = actor.strip()
    if not reviewer:
        raise ValueError("Ator respons\u00e1vel pela transcri\u00e7\u00e3o \u00e9 obrigat\u00f3rio")
    if not provider.is_local:
        raise ValueError("Provider de transcri\u00e7\u00e3o deve executar localmente")
    if provider.provider_id != settings.provider:
        raise ValueError("Provider configurado diverge do provider selecionado")

    if project_directory.is_symlink():
        raise ValueError("Diret\u00f3rio do projeto n\u00e3o pode ser symlink")
    workspace = workspace_root.resolve(strict=True)
    project = project_directory.resolve(strict=True)
    if not project.is_relative_to(workspace):
        raise ValueError("Diret\u00f3rio do projeto est\u00e1 fora do workspace permitido")

    project_path = project / "project.yaml"
    project_document = _load_project(project_path)
    if project_document["status"] != ProjectState.VALIDATED.value:
        raise ValueError("Projeto deve estar no estado validated para transcri\u00e7\u00e3o")
    source_sha256 = project_document["source"]["sha256"]
    if not isinstance(source_sha256, str):
        raise ValueError("Projeto validado deve conter SHA-256 da origem")

    source = _source_media(project)
    if sha256_file(source) != source_sha256:
        raise ValueError("SHA-256 da origem diverge do project.yaml")
    source_duration_seconds = _source_duration(project, source_sha256)
    transcript_path = project / "02_processing" / "transcript.json"
    if transcript_path.exists():
        raise FileExistsError(
            "transcript.json j\u00e1 existe; o MVP n\u00e3o sobrescreve transcri\u00e7\u00f5es"
        )

    output = provider.transcribe(
        TranscriptionRequest(
            media_path=source,
            language=settings.language,
            model=settings.model,
            model_revision=settings.model_revision,
            device=settings.device,
            compute_type=settings.compute_type,
            local_files_only=settings.local_files_only,
            vad_filter=settings.vad_filter,
            vad_min_silence_duration_ms=settings.vad_min_silence_duration_ms,
        )
    )
    identity = output.provider
    if (
        identity.name != settings.provider
        or identity.package_version != settings.provider_version
        or identity.model != settings.model
        or identity.revision != settings.model_revision
        or identity.device != settings.device
        or identity.compute_type != settings.compute_type
    ):
        raise ValueError("Metadados retornados pelo provider divergem da configura\u00e7\u00e3o")

    document: dict[str, Any] = {
        "schema_version": "1.0",
        "project_id": project_document["project_id"],
        "version": 1,
        "language": "pt-BR",
        "source_sha256": source_sha256,
        "provider": identity.to_document(),
        "review": {"status": "pending", "reviewed_by": None, "reviewed_at": None},
        "segments": [dict(segment) for segment in output.segments],
    }
    _validate_duration_bounds(document, source_duration_seconds)
    _write_validated_json(transcript_path, "transcript", document)
    transcript_sha256 = sha256_file(transcript_path)
    finished = _utc(clock())
    _update_project(project_path, project_document, status=ProjectState.TRANSCRIBED)
    _append_transition_event(
        project=project,
        project_id=str(project_document["project_id"]),
        run_id=run_id,
        actor=reviewer,
        occurred_at=finished,
        artifact_hashes={"source": source_sha256, "transcript": transcript_sha256},
    )
    return TranscriptionResult(
        project_id=str(project_document["project_id"]),
        run_id=run_id,
        transcript_file="02_processing/transcript.json",
        transcript_sha256=transcript_sha256,
    )


def _source_media(project: Path) -> Path:
    inbox = project / "01_inbox"
    if not inbox.is_dir() or inbox.is_symlink():
        raise ValueError("Origem validada n\u00e3o encontrada em 01_inbox")
    candidates = [path for path in inbox.glob("source-*") if path.is_file()]
    if len(candidates) != 1:
        raise ValueError("Projeto deve conter exatamente uma origem validada")
    source = candidates[0]
    if source.is_symlink():
        raise ValueError("Origem validada n\u00e3o pode ser symlink")
    return source.resolve(strict=True)


def _source_duration(project: Path, source_sha256: str) -> float:
    report_path = project / "02_processing" / "technical-report.json"
    if not report_path.is_file() or report_path.is_symlink():
        raise ValueError("Relatório técnico da origem não encontrado")
    report = load_document(report_path)
    if not isinstance(report, dict):
        raise ValueError("Relatório técnico deve conter um objeto")
    issues = validate_document("media-probe", report)
    if issues:
        raise ValueError(
            "Relatório técnico inválido: " + "; ".join(issue.render() for issue in issues)
        )
    if report["source_sha256"] != source_sha256:
        raise ValueError("SHA-256 do relatório técnico diverge da origem")
    duration = float(report["format"]["duration_seconds"])
    if duration <= 0:
        raise ValueError("Duração da origem deve ser positiva")
    return duration


def _validate_duration_bounds(document: Mapping[str, Any], duration_seconds: float) -> None:
    for index, segment in enumerate(document["segments"]):
        if float(segment["end"]) > duration_seconds + 0.050:
            raise ValueError(
                f"Segmento {index} ultrapassa a duração validada da origem "
                f"({duration_seconds:.3f} s)"
            )


def _load_project(path: Path) -> dict[str, Any]:
    value = load_document(path)
    if not isinstance(value, dict):
        raise ValueError("project.yaml deve conter um objeto")
    document = cast(dict[str, Any], value)
    issues = validate_document("project", document)
    if issues:
        raise ValueError("Projeto inv\u00e1lido: " + "; ".join(issue.render() for issue in issues))
    return document


def _update_project(path: Path, document: dict[str, Any], *, status: ProjectState) -> None:
    require_transition(ProjectState(str(document["status"])), status)
    updated = cast(dict[str, Any], json.loads(json.dumps(document)))
    updated["status"] = status.value
    issues = validate_document("project", updated)
    if issues:
        raise ValueError(
            "Projeto atualizado inv\u00e1lido: " + "; ".join(i.render() for i in issues)
        )
    _write_yaml_atomic(path, updated)


def _write_validated_json(path: Path, schema: str, document: dict[str, Any]) -> None:
    issues = validate_document(schema, document)
    if issues:
        raise ValueError(
            f"Documento {schema} inv\u00e1lido: " + "; ".join(issue.render() for issue in issues)
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
            "event_type": "transcription_completed",
            "previous_state": ProjectState.VALIDATED.value,
            "new_state": ProjectState.TRANSCRIBED.value,
            "reason": None,
            "artifact_hashes": artifact_hashes,
        },
    )


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("Clock de transcri\u00e7\u00e3o deve retornar datetime com timezone")
    return value.astimezone(UTC)


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")
