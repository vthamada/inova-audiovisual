from __future__ import annotations

import json
import os
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from inova_av.domain.hashing import sha256_file
from inova_av.observability.audit import append_audit_event
from inova_av.schemas.registry import load_document, validate_document


def accept_transcript_review(
    *,
    project_directory: Path,
    reviewed_transcript: Mapping[str, Any],
    reviewer: str,
    now: datetime | None = None,
) -> str:
    """Persist a human-reviewed transcript without replacing the ASR draft."""

    actor = reviewer.strip()
    if not actor:
        raise ValueError("Identidade do revisor é obrigatória")
    project = project_directory.resolve(strict=True)
    if project_directory.is_symlink():
        raise ValueError("Diretório do projeto não pode ser symlink")
    project_path = project / "project.yaml"
    project_document = _project_document(project_path)
    if project_document["status"] != "transcribed":
        raise ValueError("Projeto deve estar em transcribed para aceitar revisão")
    if project_document["governance"]["transcript_reviewed"]:
        raise ValueError("Projeto já possui transcript revisado")

    draft_path = project / "02_processing" / "transcript.json"
    draft = _transcript_document(draft_path)
    candidate = dict(reviewed_transcript)
    _validate_review_candidate(draft, candidate, project_document, actor)

    destination = project / "03_review" / f"transcript.v{candidate['version']}.json"
    if destination.exists():
        raise FileExistsError("Destino de transcript revisado já existe; não será sobrescrito")
    _write_json_atomic(destination, candidate)
    transcript_sha256 = sha256_file(destination)
    _mark_project_transcript_reviewed(project_path, project_document)
    occurred_at = (now or datetime.now(UTC)).astimezone(UTC)
    append_audit_event(
        project / "audit.jsonl",
        {
            "schema_version": "1.0",
            "event_id": f"EVT-{uuid.uuid4()}",
            "occurred_at": occurred_at.isoformat().replace("+00:00", "Z"),
            "project_id": project_document["project_id"],
            "run_id": None,
            "actor": actor,
            "event_type": "transcript_review_completed",
            "previous_state": "transcribed",
            "new_state": "transcribed",
            "reason": None,
            "artifact_hashes": {
                "transcript_draft": sha256_file(draft_path),
                "transcript_reviewed": transcript_sha256,
            },
        },
    )
    return str(destination.relative_to(project).as_posix())


def _validate_review_candidate(
    draft: dict[str, Any],
    candidate: dict[str, Any],
    project: dict[str, Any],
    reviewer: str,
) -> None:
    issues = validate_document("transcript", candidate)
    if issues:
        raise ValueError("Transcript revisado inválido: " + "; ".join(i.render() for i in issues))
    if draft["review"]["status"] != "pending":
        raise ValueError("Transcript de origem deve estar pendente de revisão")
    if (
        candidate["project_id"] != project["project_id"]
        or candidate["project_id"] != draft["project_id"]
    ):
        raise ValueError("Transcript revisado pertence a outro projeto")
    if candidate["source_sha256"] != draft["source_sha256"]:
        raise ValueError("Transcript revisado diverge do SHA-256 da origem")
    if candidate["version"] != draft["version"] + 1:
        raise ValueError("Transcript revisado deve incrementar a versão em uma unidade")
    review = candidate["review"]
    if (
        review["status"] != "reviewed"
        or review["reviewed_by"] != reviewer
        or review["reviewed_at"] is None
    ):
        raise ValueError("Review exige status reviewed, revisor correspondente e data")


def _project_document(path: Path) -> dict[str, Any]:
    value = load_document(path)
    if not isinstance(value, dict):
        raise ValueError("project.yaml deve conter um objeto")
    document = cast(dict[str, Any], value)
    issues = validate_document("project", document)
    if issues:
        raise ValueError("Projeto inválido: " + "; ".join(issue.render() for issue in issues))
    return document


def _transcript_document(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ValueError("Transcript de origem não encontrado")
    value = load_document(path)
    if not isinstance(value, dict):
        raise ValueError("Transcript deve conter um objeto")
    document = cast(dict[str, Any], value)
    issues = validate_document("transcript", document)
    if issues:
        raise ValueError(
            "Transcript de origem inválido: " + "; ".join(issue.render() for issue in issues)
        )
    return document


def _mark_project_transcript_reviewed(path: Path, document: dict[str, Any]) -> None:
    updated = cast(dict[str, Any], json.loads(json.dumps(document)))
    governance = cast(dict[str, Any], updated["governance"])
    governance["transcript_reviewed"] = True
    issues = validate_document("project", updated)
    if issues:
        raise ValueError("Projeto atualizado inválido: " + "; ".join(i.render() for i in issues))
    content = yaml.safe_dump(updated, allow_unicode=True, sort_keys=False)
    _write_text_atomic(path, content)


def _write_json_atomic(path: Path, document: dict[str, Any]) -> None:
    content = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    _write_text_atomic(path, content)


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
