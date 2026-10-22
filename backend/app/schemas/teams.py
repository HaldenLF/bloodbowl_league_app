from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.base import ORMModel

class TeamCreate(BaseModel):
    race_id: int
    name: str = Field(min_length=1, max_length=150)
    coach_name: str = Field(min_length=1, max_length=100)
    re_rolls: int = Field(default=0, ge=0)
    assistant_coaches: int = Field(default=0, ge=0)
    cheerleaders: int = Field(default=0, ge=0)
    apothecary: int = Field(default=0, ge=0, le=1)
    dedicated_fans: int = Field(default=1, ge=1)
    
    
class TeamOut(ORMModel):
    id: int
    season_id: int
    race_id: int
    name: str
    coach_name: str
    treasury: int
    re_rolls: int
    assistant_coaches: int
    cheerleaders: int
    apothecary: int
    dedicated_fans: int
    created_at: datetime