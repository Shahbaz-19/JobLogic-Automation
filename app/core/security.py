"""Helpers that keep sensitive values out of log messages."""

SENSITIVE_HEADERS = {"authorization", "x-api-key", "api-key"}


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    """Return a copy with known credential headers redacted."""

    return {
        name: "***" if name.lower() in SENSITIVE_HEADERS else value
        for name, value in headers.items()
    }
