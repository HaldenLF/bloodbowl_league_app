from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.users import User


def email_taken(db: Session, email: str) -> bool:
    return db.scalar(select(User.id).where(User.email == email)) is not None


def display_name_taken(db: Session, display_name: str) -> bool:
    match = select(User.id).where(func.lower(User.display_name) == display_name.lower())
    return db.scalar(match) is not None
