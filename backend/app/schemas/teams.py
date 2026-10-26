from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, StringConstraints

from app.schemas.base import ORMModel
from app.schemas.users import UserPublicOut

class TeamCreate(BaseModel):
    race_id: int
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
    coach_id: int | None = None
    
    
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