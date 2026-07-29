from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

SENSITIVE_KEY = re.compile(r"(?:api[_-]?key|authorization|password|secret|token)", re.I)
BEARER = re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]+=*")


def redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): "[REDACTED]" if SENSITIVE_KEY.search(str(key)) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, str):
        return BEARER.sub("Bearer [REDACTED]", value)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [redact(item) for item in value]
    return value
