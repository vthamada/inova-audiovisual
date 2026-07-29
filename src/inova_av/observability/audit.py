from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from inova_av.domain.hashing import canonical_json_bytes
from inova_av.schemas.registry import validate_document


def append_audit_event(path: Path, event: dict[str, Any]) -> None:
    issues = validate_document("audit-event", event)
    if issues:
        rendered = "; ".join(issue.render() for issue in issues)
        raise ValueError(f"Evento de auditoria inválido: {rendered}")
    if not path.parent.is_dir():
        raise FileNotFoundError(f"Diretório de auditoria não existe: {path.parent}")
    with path.open("ab") as stream:
        stream.write(canonical_json_bytes(event) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
