"""Strict CORS origin configuration for the FastAPI service."""
from __future__ import annotations

import os
from urllib.parse import urlsplit


DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://localhost:5173",
)


def parse_cors_origins(raw: str | None = None) -> list[str]:
    """Parse explicit browser origins; wildcard and URL paths are rejected."""
    configured = raw if raw is not None else os.getenv("CORS_ORIGINS")
    if configured is None or not configured.strip():
        return list(DEFAULT_CORS_ORIGINS)

    origins: list[str] = []
    for item in configured.split(","):
        origin = item.strip().rstrip("/")
        if not origin:
            continue
        if origin == "*":
            raise ValueError(
                "CORS_ORIGINS cannot contain '*'; configure explicit trusted origins."
            )
        try:
            parsed = urlsplit(origin)
            _ = parsed.port
        except ValueError as exc:
            raise ValueError("CORS_ORIGINS contains a malformed origin.") from exc

        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                "Each CORS origin must be an http(s) scheme and hostname with no path, query, or credentials."
            )

        normalized = f"{parsed.scheme}://{parsed.netloc}"
        if normalized not in origins:
            origins.append(normalized)

    if not origins:
        raise ValueError("CORS_ORIGINS must contain at least one explicit origin.")
    return origins
