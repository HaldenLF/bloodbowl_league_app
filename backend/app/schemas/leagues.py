from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.base import ORMModel

class LeagueCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class LeagueOut(ORMModel):
    id: int
    name: str
    created_at: datetime