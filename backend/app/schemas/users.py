from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator

from app.models.users import AccountType
from app.schemas.base import ORMModel


class UserCreate(BaseModel):
    email: EmailStr
    display_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    password: str = Field(min_length=8, max_length=128, repr=False)
    account_type: Literal["coach", "commissioner"]

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return value.lower()


class UserOut(ORMModel):
    id: int
    email: str
    display_name: str
    account_type: AccountType
    is_active: bool
    created_at: datetime


class UserPublicOut(ORMModel):
    id: int
    display_name: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
