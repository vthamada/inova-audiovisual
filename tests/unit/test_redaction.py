from inova_av.observability.redaction import redact


def test_nested_secrets_and_bearer_tokens_are_redacted() -> None:
    value = {
        "api_key": "real-secret",
        "headers": {"Authorization": "Bearer abc.def.ghi"},
        "message": "request used Bearer xyz-123",
    }
    result = redact(value)
    assert result["api_key"] == "[REDACTED]"
    assert result["headers"]["Authorization"] == "[REDACTED]"
    assert result["message"] == "request used Bearer [REDACTED]"
