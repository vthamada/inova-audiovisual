from pathlib import Path

import yaml

from inova_av.domain.approval import REQUIRED_ARTIFACTS, validate_final_gate
from inova_av.domain.hashing import sha256_file


def _approved_project() -> dict:
    return {
        "project_id": "VID-2026-0001",
        "status": "approved",
        "people": [{"name": "Pessoa", "image_authorization_status": "approved"}],
        "branding": {"template_version": "1.0", "logo_asset": "logo-oficial"},
        "governance": {
            "transcript_reviewed": True,
            "legal_review_required": False,
            "approved_by": "Revisora",
            "approved_at": "2026-07-29T12:00:00-03:00",
        },
    }


def _artifacts(tmp_path: Path) -> tuple[dict[str, str], dict[str, str]]:
    paths: dict[str, str] = {}
    hashes: dict[str, str] = {}
    for name in REQUIRED_ARTIFACTS:
        suffix = ".yaml" if name == "assets_registry" else ".bin"
        path = tmp_path / f"{name}{suffix}"
        if name == "assets_registry":
            logo = tmp_path / "logo.svg"
            logo.write_bytes(b"logo-oficial")
            registry = {
                "schema_version": "1.0",
                "assets": [
                    {
                        "asset_id": "logo-oficial",
                        "version": "1.0",
                        "path": logo.name,
                        "sha256": sha256_file(logo),
                        "origin": "Inova Diamantina",
                        "license": "uso institucional aprovado",
                        "approved_by": "Gestora da marca",
                        "approved_at": "2026-07-29T12:00:00-03:00",
                        "expires_at": None,
                        "credit": None,
                        "restrictions": [],
                    }
                ],
            }
            path.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")
        else:
            path.write_bytes(f"conteúdo-{name}".encode())
        paths[name] = path.name
        hashes[name] = sha256_file(path)
    return paths, hashes


def test_final_gate_accepts_only_matching_approved_artifacts(tmp_path: Path) -> None:
    artifacts, hashes = _artifacts(tmp_path)
    approval = {
        "project_id": "VID-2026-0001", "decision": "approved", "reviewer": "Revisora",
        "legal_review_status": "not_required", "image_authorization_status": "approved",
        "artifact_hashes": hashes,
    }
    assert validate_final_gate(_approved_project(), approval, artifacts, tmp_path) == []


def test_final_gate_detects_change_after_approval(tmp_path: Path) -> None:
    artifacts, hashes = _artifacts(tmp_path)
    approval = {
        "project_id": "VID-2026-0001", "decision": "approved", "reviewer": "Revisora",
        "legal_review_status": "not_required", "image_authorization_status": "approved",
        "artifact_hashes": hashes,
    }
    (tmp_path / artifacts["preview"]).write_bytes(b"preview alterado")
    issues = validate_final_gate(_approved_project(), approval, artifacts, tmp_path)
    assert [(issue.code, issue.message) for issue in issues] == [
        ("artifact_hash_mismatch", "Hash divergente: preview")
    ]


def test_final_gate_blocks_pending_image_authorization(tmp_path: Path) -> None:
    artifacts, hashes = _artifacts(tmp_path)
    project = _approved_project()
    project["people"][0]["image_authorization_status"] = "pending"
    approval = {
        "project_id": "VID-2026-0001", "decision": "approved", "reviewer": "Revisora",
        "legal_review_status": "not_required", "image_authorization_status": "approved",
        "artifact_hashes": hashes,
    }
    issues = validate_final_gate(project, approval, artifacts, tmp_path)
    assert any(issue.code == "image_authorization_missing" for issue in issues)


def test_final_gate_blocks_unapproved_project_and_human_decision(tmp_path: Path) -> None:
    artifacts, hashes = _artifacts(tmp_path)
    project = _approved_project()
    project["status"] = "under_review"
    approval = {
        "project_id": "VID-2026-0001",
        "decision": "changes_requested",
        "reviewer": "Revisora",
        "legal_review_status": "not_required",
        "image_authorization_status": "approved",
        "artifact_hashes": hashes,
    }
    codes = {
        issue.code for issue in validate_final_gate(project, approval, artifacts, tmp_path)
    }
    assert {"project_not_approved", "decision_not_approved"}.issubset(codes)


def test_final_gate_requires_legal_review_when_configured(tmp_path: Path) -> None:
    artifacts, hashes = _artifacts(tmp_path)
    project = _approved_project()
    project["governance"]["legal_review_required"] = True
    approval = {
        "project_id": "VID-2026-0001",
        "decision": "approved",
        "reviewer": "Revisora",
        "legal_review_status": "not_required",
        "image_authorization_status": "approved",
        "artifact_hashes": hashes,
    }
    issues = validate_final_gate(project, approval, artifacts, tmp_path)
    assert any(issue.code == "legal_review_missing" for issue in issues)


def test_final_gate_reports_missing_artifact(tmp_path: Path) -> None:
    artifacts, hashes = _artifacts(tmp_path)
    del artifacts["captions"]
    approval = {
        "project_id": "VID-2026-0001",
        "decision": "approved",
        "reviewer": "Revisora",
        "legal_review_status": "not_required",
        "image_authorization_status": "approved",
        "artifact_hashes": hashes,
    }
    issues = validate_final_gate(_approved_project(), approval, artifacts, tmp_path)
    assert any(issue.code == "artifact_missing" for issue in issues)


def test_final_gate_detects_registered_asset_tampering(tmp_path: Path) -> None:
    artifacts, hashes = _artifacts(tmp_path)
    approval = {
        "project_id": "VID-2026-0001",
        "decision": "approved",
        "reviewer": "Revisora",
        "legal_review_status": "not_required",
        "image_authorization_status": "approved",
        "artifact_hashes": hashes,
    }
    (tmp_path / "logo.svg").write_bytes(b"logo-adulterado")
    issues = validate_final_gate(_approved_project(), approval, artifacts, tmp_path)
    assert any(issue.code == "asset_hash_mismatch" for issue in issues)
