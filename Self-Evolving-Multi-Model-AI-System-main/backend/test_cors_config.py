import pytest

from cors_config import DEFAULT_CORS_ORIGINS, parse_cors_origins


def test_uses_local_development_origins_when_unconfigured():
    assert parse_cors_origins("") == list(DEFAULT_CORS_ORIGINS)


def test_parses_and_deduplicates_explicit_origins():
    assert parse_cors_origins(
        " https://app.example.com,https://admin.example.com,https://app.example.com/ "
    ) == ["https://app.example.com", "https://admin.example.com"]


@pytest.mark.parametrize(
    "value",
    [
        "*",
        "https://app.example.com/path",
        "https://user:pass@app.example.com",
        "ftp://app.example.com",
        "https://app.example.com?debug=1",
        "https://",
    ],
)
def test_rejects_wildcard_or_non_origin_values(value):
    with pytest.raises(ValueError):
        parse_cors_origins(value)


def test_rejects_empty_list_after_parsing():
    with pytest.raises(ValueError):
        parse_cors_origins(" , , ")
