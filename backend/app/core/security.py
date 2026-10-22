import secrets
import jwt
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from app.core.config import Settings, settings
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

JWT_ALGORITHM = "HS256"

password_hasher = PasswordHash((Argon2Hasher(),))


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


DUMMY_HASH = hash_password(secrets.token_urlsafe(32))


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp", "iat"]},
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None

api_key_header = APIKeyHeader(name="X-Commissioner=Key", auto_error=False)

# temp
def require_commissioner(key: str | None = Security(api_key_header)) -> None:
    if key is None or not secrets.compare_digest(
        key.encode(), Settings.commissioner_key.encode()
    ):
        raise HTTPException(status_code=403, detail="Commissioner access required")


def generate_join_code() -> str:
    return secrets.token_urlsafe(8)