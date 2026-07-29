from __future__ import annotations

import json
import logging
from collections.abc import Mapping, MutableMapping
from datetime import UTC, datetime
from typing import Any, TextIO

from inova_av.observability.redaction import redact


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.msg)
        if isinstance(record.args, Mapping):
            record.args = redact(record.args)
        elif record.args:
            record.args = tuple(redact(item) for item in record.args)
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: MutableMapping[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in ("run_id", "project_id", "stage", "event_type"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(redact(payload), ensure_ascii=False, sort_keys=True)


def configure_logging(
    *, level: str = "INFO", output_format: str = "human", stream: TextIO | None = None
) -> logging.Logger:
    logger = logging.getLogger("inova_av")
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(level.upper())

    handler = logging.StreamHandler(stream)
    handler.addFilter(RedactingFilter())
    if output_format == "json":
        handler.setFormatter(JsonFormatter())
    elif output_format == "human":
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    else:
        raise ValueError(f"Formato de log desconhecido: {output_format}")
    logger.addHandler(handler)
    return logger
