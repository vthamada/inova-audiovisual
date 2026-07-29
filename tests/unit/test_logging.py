import io
import json

from inova_av.observability.logging import configure_logging


def test_json_log_is_structured_and_redacts_secrets() -> None:
    stream = io.StringIO()
    logger = configure_logging(output_format="json", stream=stream)
    logger.info(
        {"event": "provider_check", "api_key": "segredo"},
        extra={"run_id": "RUN-1", "project_id": "VID-2026-0001"},
    )
    payload = json.loads(stream.getvalue())
    assert payload["run_id"] == "RUN-1"
    assert payload["project_id"] == "VID-2026-0001"
    assert "segredo" not in payload["message"]
    assert "[REDACTED]" in payload["message"]


def test_unknown_log_format_is_rejected() -> None:
    try:
        configure_logging(output_format="xml")
    except ValueError as exc:
        assert "xml" in str(exc)
    else:
        raise AssertionError("Formato desconhecido deveria falhar")


def test_mapping_log_arguments_keep_formatting_and_are_redacted() -> None:
    stream = io.StringIO()
    logger = configure_logging(output_format="json", stream=stream)
    logger.info("token=%(token)s", {"token": "segredo"})
    payload = json.loads(stream.getvalue())
    assert payload["message"] == "token=[REDACTED]"
