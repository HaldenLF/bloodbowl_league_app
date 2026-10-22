from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.users import AccountType, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def credentials_error() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_error()
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_error()
    return user


def require_account_type(*allowed: AccountType):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.account_type not in allowed:
            raise HTTPException(status_code=403, detail="Your account type cannot do this")
        return user
    return checker
