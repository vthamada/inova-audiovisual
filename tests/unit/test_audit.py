import json
from pathlib import Path

import pytest

from inova_av.observability.audit import append_audit_event


def _event(event_id: str) -> dict:
    return {
        "schema_version": "1.0",
        "event_id": event_id,
        "occurred_at": "2026-07-29T12:00:00-03:00",
        "project_id": "VID-2026-0001",
        "run_id": None,
        "actor": "tester",
        "event_type": "state_changed",
        "previous_state": "received",
        "new_state": "validated",
        "reason": None,
        "artifact_hashes": {},
    }


def test_audit_events_are_appended_as_canonical_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    append_audit_event(path, _event("EVT-1"))
    append_audit_event(path, _event("EVT-2"))
    lines = path.read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["event_id"] for line in lines] == ["EVT-1", "EVT-2"]
    assert lines[0].startswith('{"actor":"tester"')


def test_invalid_audit_event_is_not_written(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    with pytest.raises(ValueError, match="Evento de auditoria inválido"):
        append_audit_event(path, {"schema_version": "1.0"})
    assert not path.exists()
