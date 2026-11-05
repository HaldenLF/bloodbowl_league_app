from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, StringConstraints, Field

from app.schemas.base import ORMModel
from app.schemas.users import UserPublicOut
from app.models.seasons import LeagueFormat
from app.rules.team_extras import TeamExtra

class TeamCreate(BaseModel):
    race_id: int
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
    coach_id: int | None = None


class PurchaseCreate(BaseModel):
    item: TeamExtra
    quantity: int = Field(default=1, ge=1, le=8)


class ShopItemOut(BaseModel):
    item: TeamExtra
    owned: int
    maximum: int
    price: int | None
    unavailable_reason: str | None


class TeamValueOut(BaseModel):
    players: int
    re_rolls: int
    staff: int
    total: int


class TreasuryUpdate(BaseModel):
    treasury: int = Field(ge=0)


class TeamOut(ORMModel):
    id: int
    season_id: int
    race_id: int
    name: str
    coach: UserPublicOut
    treasury: int
    re_rolls: int
    assistant_coaches: int
    cheerleaders: int
    apothecary: int
    dedicated_fans: int
    created_at: datetime


class NamedRef(ORMModel):
    id: int
    name: str


class MyTeamSeasonOut(ORMModel):
    id: int
    name: str
    format: LeagueFormat
    is_active: bool
    league: NamedRef


class MyTeamOut(ORMModel):
    id: int
    name: str
    race: NamedRef
    season: MyTeamSeasonOut
    treasury: int
    team_value: int
