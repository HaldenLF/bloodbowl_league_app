
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.accounts import display_name_taken, email_taken
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password, DUMMY_HASH
from app.core.rate_limit import limiter
from app.models.users import AccountType, User
from app.schemas.users import TokenOut, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

EMAIL_TAKEN = "An account with that email already exists"
NAME_TAKEN = "That coach name is already taken"


@router.post("/register", response_model=UserOut, status_code=201)
@limiter.limit("10/hour")
def register(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    if email_taken(db, payload.email):
        raise HTTPException(status_code=409, detail=EMAIL_TAKEN)
    if display_name_taken(db, payload.display_name):
        raise HTTPException(status_code=409, detail=NAME_TAKEN)


    user = User(
        email=payload.email,
        display_name=payload.display_name,
        password_hash=hash_password(payload.password),
        account_type=AccountType(payload.account_type),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="That email or coach name is already in use")
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
@limiter.limit("5/minute")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == form.username.strip().lower()))
    password_ok = verify_password(form.password, user.password_hash if user else DUMMY_HASH)
    if user is None or not password_ok:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account is disabled")
    return TokenOut(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user