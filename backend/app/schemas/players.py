from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints

from app.schemas.base import ORMModel
from app.schemas.races import PositionOut


class PlayerCreate(BaseModel):
    position_id: int
    number: int = Field(ge=1, le=99)
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)] | None = None


class PlayerOut(ORMModel):
    id: int
    team_id: int
    position_id: int
    number: int
    name: str | None
    completions: int
    touchdowns: int
    interceptions: int
    casualties: int
    mvps: int
    niggling_injuries: int
    missing_next_game: bool
    dead: bool
    created_at: datetime
    position: PositionOut