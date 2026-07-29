from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from inova_av.domain.hashing import sha256_file
from inova_av.domain.paths import resolve_under_root
from inova_av.schemas.registry import load_document, validate_document

REQUIRED_ARTIFACTS = frozenset(
    {"transcript", "edit_plan", "captions", "template_config", "assets_registry", "preview"}
)


@dataclass(frozen=True, slots=True)
class GateIssue:
    code: str
    message: str


def validate_final_gate(
    project: Mapping[str, Any],
    approval: Mapping[str, Any],
    artifacts: Mapping[str, str],
    project_root: Path,
) -> list[GateIssue]:
    issues: list[GateIssue] = []
    if project.get("status") != "approved":
        issues.append(GateIssue("project_not_approved", "Projeto deve estar em approved"))
    if approval.get("decision") != "approved":
        issues.append(GateIssue("decision_not_approved", "Decisão humana deve ser approved"))
    if project.get("project_id") != approval.get("project_id"):
        issues.append(GateIssue("project_mismatch", "Aprovação pertence a outro projeto"))

    governance = project.get("governance", {})
    if not governance.get("transcript_reviewed"):
        issues.append(GateIssue("transcript_not_reviewed", "Transcrição ainda não foi revisada"))
    if governance.get("approved_by") != approval.get("reviewer"):
        issues.append(GateIssue("reviewer_mismatch", "Revisor não coincide com project.yaml"))
    if not governance.get("approved_at"):
        issues.append(GateIssue("approval_time_missing", "Data da aprovação humana é obrigatória"))
    if (
        governance.get("legal_review_required")
        and approval.get("legal_review_status") != "approved"
    ):
        issues.append(GateIssue("legal_review_missing", "Revisão jurídica é obrigatória"))

    people = project.get("people", [])
    invalid_people = [
        person.get("name") or "pessoa sem nome"
        for person in people
        if person.get("image_authorization_status") not in {"approved", "not_required"}
    ]
    if invalid_people:
        issues.append(
            GateIssue(
                "image_authorization_missing",
                "Autorização pendente ou negada: " + ", ".join(invalid_people),
            )
        )

    if approval.get("image_authorization_status") not in {"approved", "not_required"}:
        issues.append(
            GateIssue("approval_image_status_invalid", "Aprovação não confirma direito de imagem")
        )

    branding = project.get("branding", {})
    if not branding.get("template_version"):
        issues.append(GateIssue("template_missing", "Template aprovado é obrigatório"))
    if not branding.get("logo_asset"):
        issues.append(GateIssue("logo_missing", "Logo oficial registrado é obrigatório"))

    expected_hashes = approval.get("artifact_hashes", {})
    registry_path: Path | None = None
    for name in sorted(REQUIRED_ARTIFACTS):
        relative = artifacts.get(name)
        expected = expected_hashes.get(name)
        if relative is None or expected is None:
            issues.append(GateIssue("artifact_missing", f"Artefato obrigatório ausente: {name}"))
            continue
        try:
            path = resolve_under_root(project_root, relative, must_exist=True)
        except (OSError, ValueError) as exc:
            issues.append(GateIssue("artifact_path_invalid", f"{name}: {exc}"))
            continue
        if not path.is_file():
            issues.append(GateIssue("artifact_not_file", f"{name} não é arquivo"))
            continue
        if sha256_file(path) != expected:
            issues.append(GateIssue("artifact_hash_mismatch", f"Hash divergente: {name}"))
        elif name == "assets_registry":
            registry_path = path

    if registry_path is not None:
        _validate_asset_registry(registry_path, project_root, branding, issues)
    return issues


def _validate_asset_registry(
    registry_path: Path,
    project_root: Path,
    branding: Mapping[str, Any],
    issues: list[GateIssue],
) -> None:
    try:
        registry = load_document(registry_path)
    except (OSError, ValueError) as exc:
        issues.append(GateIssue("asset_registry_unreadable", str(exc)))
        return
    schema_issues = validate_document("asset-registry", registry)
    if schema_issues:
        issues.append(
            GateIssue(
                "asset_registry_invalid",
                "; ".join(issue.render() for issue in schema_issues),
            )
        )
        return

    assets = {asset["asset_id"]: asset for asset in registry["assets"]}
    logo_asset = branding.get("logo_asset")
    if logo_asset and logo_asset not in assets:
        issues.append(GateIssue("logo_not_registered", "Logo não consta no registro de assets"))

    for asset_id, asset in assets.items():
        try:
            asset_path = resolve_under_root(project_root, asset["path"], must_exist=True)
        except (OSError, ValueError) as exc:
            issues.append(GateIssue("asset_path_invalid", f"{asset_id}: {exc}"))
            continue
        if not asset_path.is_file() or sha256_file(asset_path) != asset["sha256"]:
            issues.append(GateIssue("asset_hash_mismatch", f"Asset divergente: {asset_id}"))
