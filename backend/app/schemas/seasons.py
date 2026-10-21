from pydantic import BaseModel, Field
from app.schemas.base import ORMModel
from app.models.seasons import LeagueFormat

class SeasonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    format: LeagueFormat
    is_active: bool = True
    

class SeasonOut(ORMModel):
    id: int
    league_id: int
    name: str 
    format: LeagueFormat
    is_active: bool