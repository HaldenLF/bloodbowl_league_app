from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import get_team_for_manager
from app.models.users import User
from app.schemas.teams import TeamOut, TreasuryUpdate

router = APIRouter(
    prefix="/commissioner",
    tags=["commissioner"]
    )


@router.patch("/teams/{team_id}/treasury", response_model=TeamOut)
def set_team_treasury(team_id: int, payload: TreasuryUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    team = get_team_for_manager(db, team_id, user)
    team.treasury = payload.treasury
    db.commit()
    db.refresh(team)
    return team