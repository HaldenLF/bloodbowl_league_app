from datetime import datetime
from pydantic import BaseModel, StringConstraints
from typing import Annotated
from app.schemas.base import ORMModel
from app.models.league import JoinPolicy
from app.models.league_members import MembershipStatus
from app.schemas.users import UserPublicOut

class LeagueCreate(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
    join_policy: JoinPolicy = JoinPolicy.INVITE_ONLY


class LeagueOut(ORMModel):
    id: int
    name: str
    join_policy: JoinPolicy
    owner: UserPublicOut
    created_at: datetime


class LeagueCreatedOut(LeagueOut):
    join_code: str


class JoinCodeOut(ORMModel):
    join_code: str


class JoinByCode(BaseModel):
    join_code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=32)]


class LeagueSearchOut(ORMModel):
    id: int
    name: str
    join_policy: JoinPolicy
    owner: UserPublicOut


class MembershipOut(ORMModel):
    league_id: int
    status: MembershipStatus
    joined_at: datetime


class MemberOut(ORMModel):
    user: UserPublicOut
    status: MembershipStatus
    joined_at: datetime