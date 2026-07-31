from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from inova_av.common import find_repository_root
from inova_av.domain.paths import validate_relative_path

SCHEMA_FILES: dict[str, str] = {
    "pipeline-config": "pipeline-config.schema.json",
    "project": "project.schema.json",
    "transcript": "transcript.schema.json",
    "edit-plan": "edit-plan.schema.json",
    "render-manifest": "render-manifest.schema.json",
    "approval": "approval.schema.json",
    "audit-event": "audit-event.schema.json",
    "asset-registry": "asset-registry.schema.json",
    "render-request": "render-request.schema.json",
    "render-result": "render-result.schema.json",
    "media-probe": "media-probe.schema.json",
    "ingest-manifest": "ingest-manifest.schema.json",
}


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    path: str
    message: str

    def render(self) -> str:
        return f"{self.path}: {self.message}" if self.path else self.message


def load_document(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        if path.suffix.lower() == ".json":
            return json.load(stream)
        if path.suffix.lower() in {".yaml", ".yml"}:
            return yaml.safe_load(stream)
    raise ValueError(f"Formato não suportado: {path.suffix}")


def load_schema(name: str, root: Path | None = None) -> dict[str, Any]:
    try:
        filename = SCHEMA_FILES[name]
    except KeyError as exc:
        raise ValueError(f"Schema desconhecido: {name}") from exc
    repository = root or find_repository_root()
    with (repository / "schemas" / filename).open("r", encoding="utf-8") as stream:
        schema: dict[str, Any] = json.load(stream)
    Draft202012Validator.check_schema(schema)
    return schema


def validate_document(name: str, value: Any, root: Path | None = None) -> list[ValidationIssue]:
    schema = load_schema(name, root)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    issues = [
        ValidationIssue("/".join(str(part) for part in error.absolute_path), error.message)
        for error in sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))
    ]
    if not issues and isinstance(value, dict):
        issues.extend(_semantic_issues(name, value))
    return issues


def _semantic_issues(name: str, value: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if name == "transcript":
        previous_end = 0.0
        for index, segment in enumerate(value["segments"]):
            start, end = float(segment["start"]), float(segment["end"])
            if end <= start:
                issues.append(ValidationIssue(f"segments/{index}", "end deve ser maior que start"))
            if start < previous_end:
                issues.append(
                    ValidationIssue(f"segments/{index}/start", "segmentos devem ser monotônicos")
                )
            previous_end = max(previous_end, end)
            previous_word_end = start
            for word_index, word in enumerate(segment.get("words", [])):
                word_start, word_end = float(word["start"]), float(word["end"])
                issue_prefix = f"segments/{index}/words/{word_index}"
                if word_end <= word_start:
                    issues.append(ValidationIssue(issue_prefix, "end deve ser maior que start"))
                if word_start < start or word_end > end:
                    issues.append(
                        ValidationIssue(issue_prefix, "word deve permanecer dentro do segmento")
                    )
                if word_start < previous_word_end:
                    issues.append(
                        ValidationIssue(
                            f"{issue_prefix}/start", "palavras devem ser monotônicas"
                        )
                    )
                previous_word_end = max(previous_word_end, word_end)
    elif name == "edit-plan":
        total = 0.0
        for index, segment in enumerate(value["segments"]):
            start, end = float(segment["in"]), float(segment["out"])
            if end <= start:
                issues.append(ValidationIssue(f"segments/{index}", "out deve ser maior que in"))
            total += max(0.0, end - start)
            try:
                validate_relative_path(segment["source_file"])
            except ValueError as exc:
                issues.append(ValidationIssue(f"segments/{index}/source_file", str(exc)))
        target = float(value["target"]["duration_seconds"])
        if abs(total - target) > 0.050:
            issues.append(
                ValidationIssue("target/duration_seconds", "deve corresponder à soma dos segmentos")
            )
        for index, segment in enumerate(value.get("audio_segments", [])):
            source_start, source_end = float(segment["in"]), float(segment["out"])
            timeline_start, timeline_end = float(segment["timeline_in"]), float(
                segment["timeline_out"]
            )
            if source_end <= source_start:
                issues.append(
                    ValidationIssue(f"audio_segments/{index}", "out deve ser maior que in")
                )
            if timeline_end <= timeline_start:
                issues.append(
                    ValidationIssue(
                        f"audio_segments/{index}/timeline_out",
                        "deve ser maior que timeline_in",
                    )
                )
            elif abs((source_end - source_start) - (timeline_end - timeline_start)) > 0.050:
                issues.append(
                    ValidationIssue(
                        f"audio_segments/{index}/timeline_out",
                        "deve preservar a duração da origem",
                    )
                )
            if timeline_end > target:
                issues.append(
                    ValidationIssue(
                        f"audio_segments/{index}/timeline_out",
                        "não pode exceder a duração-alvo",
                    )
                )
            try:
                validate_relative_path(segment["source_file"])
            except ValueError as exc:
                issues.append(ValidationIssue(f"audio_segments/{index}/source_file", str(exc)))
    elif name == "project":
        status = value["status"]
        if status not in {"received", "quarantined"} and value["source"]["sha256"] is None:
            issues.append(
                ValidationIssue("source/sha256", "é obrigatório após validação da origem")
            )
        if status in {"approved", "final_rendered", "published"}:
            governance = value["governance"]
            if not governance["transcript_reviewed"]:
                issues.append(ValidationIssue("governance/transcript_reviewed", "deve ser true"))
            if not governance["approved_by"] or not governance["approved_at"]:
                issues.append(
                    ValidationIssue("governance", "aprovação humana completa é obrigatória")
                )
            for index, person in enumerate(value["people"]):
                if person["image_authorization_status"] not in {"approved", "not_required"}:
                    issues.append(
                        ValidationIssue(
                            f"people/{index}/image_authorization_status",
                            "deve estar aprovado antes do estado approved",
                        )
                    )
    elif name == "render-manifest":
        if value["render_kind"] == "final" and value["approval_sha256"] is None:
            issues.append(ValidationIssue("approval_sha256", "é obrigatório no render final"))
    elif name == "asset-registry":
        seen: set[str] = set()
        for index, asset in enumerate(value["assets"]):
            asset_id = asset["asset_id"]
            if asset_id in seen:
                issues.append(ValidationIssue(f"assets/{index}/asset_id", "asset_id duplicado"))
            seen.add(asset_id)
            try:
                validate_relative_path(asset["path"])
            except ValueError as exc:
                issues.append(ValidationIssue(f"assets/{index}/path", str(exc)))
    elif name == "media-probe":
        try:
            validate_relative_path(value["source_file"])
        except ValueError as exc:
            issues.append(ValidationIssue("source_file", str(exc)))
        try:
            if Fraction(value["video"]["avg_frame_rate"]) <= 0:
                raise ValueError("deve ser positivo")
        except (ValueError, ZeroDivisionError) as exc:
            issues.append(ValidationIssue("video/avg_frame_rate", f"frame rate inválido: {exc}"))
    elif name == "ingest-manifest":
        path_fields: list[tuple[str, str | None]] = [
            ("source/stored_path", value["source"]["stored_path"]),
            ("technical_report", value["technical_report"]),
        ]
        if value["proxy"] is not None:
            path_fields.extend(
                [
                    ("proxy/path", value["proxy"]["path"]),
                    ("proxy/technical_report", value["proxy"]["technical_report"]),
                ]
            )
        if value["quarantine"] is not None:
            path_fields.append(("quarantine/path", value["quarantine"]["path"]))
        for issue_path, candidate in path_fields:
            if candidate is None:
                continue
            try:
                validate_relative_path(candidate)
            except ValueError as exc:
                issues.append(ValidationIssue(issue_path, str(exc)))

        if value["status"] == "validated":
            if value["source"]["stored_path"] is None:
                issues.append(ValidationIssue("source/stored_path", "é obrigatório em validated"))
            if value["technical_report"] is None:
                issues.append(ValidationIssue("technical_report", "é obrigatório em validated"))
            if value["proxy"] is None:
                issues.append(ValidationIssue("proxy", "é obrigatório em validated"))
            if value["quarantine"] is not None:
                issues.append(ValidationIssue("quarantine", "deve ser null em validated"))
        elif value["quarantine"] is None:
            issues.append(ValidationIssue("quarantine", "é obrigatório em quarantined"))
    return issues
