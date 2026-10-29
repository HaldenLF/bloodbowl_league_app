import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings, settings
from app.main import create_app

FRONTEND = "https://bloodbowl.example.com"


def make_client(**overrides) -> TestClient:
    return TestClient(create_app(settings.model_copy(update=overrides)))


@pytest.fixture
def production():
    return make_client(environment="production", cors_origins=[FRONTEND])


@pytest.fixture
def development():
    return make_client(environment="development", cors_origins=[])


def test_docs_available_in_development(development):
    assert development.get("/docs").status_code == 200
    assert development.get("/openapi.json").status_code == 200


def test_docs_hidden_in_production(production):
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert production.get(path).status_code == 404


def test_security_headers_everywhere(development, production):
    for client in (development, production):
        headers = client.get("/health").headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["Referrer-Policy"] == "no-referrer"


def test_https_and_csp_headers_only_in_production(development, production):
    assert "Strict-Transport-Security" not in development.get("/health").headers
    headers = production.get("/health").headers
    assert headers["Strict-Transport-Security"].startswith("max-age=")
    assert headers["Content-Security-Policy"] == "default-src 'none'; frame-ancestors 'none'"


def test_cors_allows_only_the_listed_frontend(production):
    preflight = {"Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "authorization"}
    allowed = production.options("/auth/login", headers={"Origin": FRONTEND, **preflight})
    assert allowed.headers.get("Access-Control-Allow-Origin") == FRONTEND
    blocked = production.options("/auth/login", headers={"Origin": "https://evil.example.com", **preflight})
    assert "Access-Control-Allow-Origin" not in blocked.headers


def test_production_refuses_wildcard_cors():
    with pytest.raises(ValidationError):
        Settings(environment="production", cors_origins=["*"])
