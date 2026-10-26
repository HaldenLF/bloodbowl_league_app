import jwt
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from tests.conftest import TEST_PASSWORD

NEW_USER = {"email": "New.Coach@Example.com", "display_name": "New Coach", "password": "long-enough-pw", "account_type": "coach"}


def test_register_returns_user_without_password(client):
    response = client.post("/auth/register", json=NEW_USER)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new.coach@example.com"
    assert "password" not in body and "password_hash" not in body


def test_register_same_email_any_case_conflicts(client):
    client.post("/auth/register", json=NEW_USER)
    response = client.post("/auth/register", json={**NEW_USER, "email": "NEW.COACH@example.com"})
    assert response.status_code == 409


def test_register_cannot_choose_super_admin(client):
    response = client.post("/auth/register", json={**NEW_USER, "account_type": "super_admin"})
    assert response.status_code == 422


def test_login_then_me(client, coach):
    login = client.post("/auth/login", data={"username": coach.email, "password": TEST_PASSWORD})
    assert login.status_code == 200
    token = login.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["id"] == coach.id


def test_wrong_password_and_unknown_email_look_identical(client, coach):
    wrong_password = client.post("/auth/login", data={"username": coach.email, "password": "not-the-password"})
    unknown_email = client.post("/auth/login", data={"username": "nobody@example.com", "password": "not-the-password"})
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_disabled_account_cannot_log_in(client, make_user):
    disabled = make_user(is_active=False)
    response = client.post("/auth/login", data={"username": disabled.email, "password": TEST_PASSWORD})
    assert response.status_code == 403


def test_me_without_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_me_with_tampered_token(client, coach, auth):
    headers = auth(coach)
    headers["Authorization"] += "x"
    assert client.get("/auth/me", headers=headers).status_code == 401


def test_me_with_expired_token(client, coach):
    past = datetime.now(timezone.utc) - timedelta(minutes=5)
    token = jwt.encode(
        {"sub": str(coach.id), "iat": past, "exp": past},
        settings.jwt_secret.get_secret_value(),
        algorithm="HS256",
    )
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_token_of_disabled_account_stops_working(client, coach, auth, db):
    headers = auth(coach)
    coach.is_active = False
    db.flush()
    assert client.get("/auth/me", headers=headers).status_code == 401
