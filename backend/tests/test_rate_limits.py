import pytest

from app.core.rate_limit import limiter
from tests.conftest import TEST_PASSWORD


@pytest.fixture
def rate_limits():
    limiter.reset()
    limiter.enabled = True
    yield
    limiter.enabled = False
    limiter.reset()


def test_login_is_limited_per_client(client, coach, rate_limits):
    wrong = {"username": coach.email, "password": "not-the-password"}
    for _ in range(5):
        assert client.post("/auth/login", data=wrong).status_code == 401
    blocked = client.post("/auth/login", data={"username": coach.email, "password": TEST_PASSWORD})
    assert blocked.status_code == 429


def test_register_is_limited_per_client(client, rate_limits):
    for number in range(10):
        body = {"email": f"new{number}@example.com", "display_name": "New", "password": "long-enough-pw", "account_type": "coach"}
        assert client.post("/auth/register", json=body).status_code == 201
    body = {"email": "one-more@example.com", "display_name": "New", "password": "long-enough-pw", "account_type": "coach"}
    assert client.post("/auth/register", json=body).status_code == 429


def test_join_code_guessing_is_limited(client, auth, coach, rate_limits):
    for number in range(10):
        assert client.post("/leagues/join", json={"join_code": f"guess{number}"}, headers=auth(coach)).status_code == 404
    assert client.post("/leagues/join", json={"join_code": "guess-again"}, headers=auth(coach)).status_code == 429


def test_search_is_limited(client, auth, coach, rate_limits):
    for _ in range(30):
        assert client.get("/leagues/search", params={"q": "cup"}, headers=auth(coach)).status_code == 200
    assert client.get("/leagues/search", params={"q": "cup"}, headers=auth(coach)).status_code == 429
