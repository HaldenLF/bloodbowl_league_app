from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_commissioner
from app.routers.teams import get_team_or_404
from app.schemas.teams import TeamOut

router = APIRouter(
    prefix="/commissioner",
    tags=["commissioner"],
    dependencies=[Depends(require_commissioner)],
)


class TreasuryUpdate(BaseModel):
    treasury: int = Field(ge=0)


@router.patch("/teams/{team_id}/treasury", response_model=TeamOut)
def set_team_treasury(team_id: int, payload: TreasuryUpdate, db: Session = Depends(get_db)):
    team = get_team_or_404(db, team_id)
    team.treasury = payload.treasury
    db.commit()
    db.refresh(team)
    return team