from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from inova_av.application.review import accept_transcript_review


def _project_with_draft(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    project = tmp_path / "workspace" / "projeto"
    (project / "02_processing").mkdir(parents=True)
    project_document = {
        "schema_version": "1.0",
        "project_id": "VID-2026-9010",
        "title": "Projeto de revisão sintética",
        "editorial": "vozes-do-ecossistema",
        "status": "transcribed",
        "source": {
            "filename": "source.mp4",
            "captured_at": None,
            "location": None,
            "operator": "Operador",
            "sha256": "a" * 64,
        },
        "people": [
            {
                "name": "Pessoa fictícia",
                "role": "Teste",
                "institution": "Instituição fictícia",
                "image_authorization_status": "pending",
            }
        ],
        "publication": {
            "channels": ["instagram_reels"],
            "target_duration_seconds": 60,
            "language": "pt-BR",
        },
        "branding": {"template_version": None, "logo_asset": None},
        "governance": {
            "institutional_review_required": True,
            "legal_review_required": False,
            "transcript_reviewed": False,
            "approved_by": None,
            "approved_at": None,
        },
    }
    draft: dict[str, object] = {
        "schema_version": "1.0",
        "project_id": "VID-2026-9010",
        "version": 1,
        "language": "pt-BR",
        "source_sha256": "a" * 64,
        "provider": {
            "name": "faster-whisper",
            "package_version": "1.2.1",
            "model": "small",
            "revision": "synthetic-test",
            "device": "cpu",
            "compute_type": "int8",
        },
        "review": {"status": "pending", "reviewed_by": None, "reviewed_at": None},
        "segments": [{"id": "s1", "start": 0, "end": 1, "text": "Fala original."}],
    }
    (project / "project.yaml").write_text(
        yaml.safe_dump(project_document, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    (project / "02_processing" / "transcript.json").write_text(
        json.dumps(draft), encoding="utf-8"
    )
    return project, draft


def test_accept_review_preserves_draft_and_marks_project_governance(tmp_path: Path) -> None:
    project, draft = _project_with_draft(tmp_path)
    reviewed = deepcopy(draft)
    reviewed["version"] = 2
    reviewed["review"] = {
        "status": "reviewed",
        "reviewed_by": "Revisora de teste",
        "reviewed_at": "2026-07-31T12:00:00Z",
    }
    reviewed["segments"] = [{"id": "s1", "start": 0, "end": 1, "text": "Fala revisada."}]

    result = accept_transcript_review(
        project_directory=project,
        reviewed_transcript=reviewed,
        reviewer="Revisora de teste",
        now=datetime(2026, 7, 31, 12, 1, tzinfo=UTC),
    )

    assert result == "03_review/transcript.v2.json"
    persisted_draft = json.loads(
        (project / "02_processing" / "transcript.json").read_text(encoding="utf-8")
    )
    assert persisted_draft == draft
    persisted = json.loads((project / result).read_text(encoding="utf-8"))
    assert persisted == reviewed
    updated = yaml.safe_load((project / "project.yaml").read_text(encoding="utf-8"))
    assert updated["status"] == "transcribed"
    assert updated["governance"]["transcript_reviewed"] is True
    event = json.loads((project / "audit.jsonl").read_text(encoding="utf-8"))
    assert event["event_type"] == "transcript_review_completed"


def test_review_rejects_wrong_reviewer_without_mutating_project(tmp_path: Path) -> None:
    project, draft = _project_with_draft(tmp_path)
    reviewed = deepcopy(draft)
    reviewed["version"] = 2
    reviewed["review"] = {
        "status": "reviewed",
        "reviewed_by": "Outra pessoa",
        "reviewed_at": "2026-07-31T12:00:00Z",
    }

    with pytest.raises(ValueError, match="Review exige"):
        accept_transcript_review(
            project_directory=project,
            reviewed_transcript=reviewed,
            reviewer="Revisora de teste",
        )

    assert not (project / "03_review").exists()
    updated = yaml.safe_load((project / "project.yaml").read_text(encoding="utf-8"))
    assert updated["governance"]["transcript_reviewed"] is False
