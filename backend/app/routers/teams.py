from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.races import Race
from app.models.teams import Team
from app.routers.seasons import get_season_or_404
from app.schemas.teams import TeamCreate, TeamOut

router = APIRouter(tags=["teams"])
NAME_TAKEN = "This season already has a team with that name"


def get_team_or_404(db: Session, team_id: int) -> Team:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/seasons/{season_id}/teams", response_model=list[TeamOut])
def list_teams(season_id: int, db: Session = Depends(get_db)):
    get_season_or_404(db, season_id)
    return db.scalars(
        select(Team).where(Team.season_id == season_id).order_by(Team.name)).all()


@router.post("/seasons/{season_id}/teams", response_model=TeamOut, status_code=201)
def create_team(season_id: int, payload: TeamCreate, db: Session = Depends(get_db)):
    season = get_season_or_404(db, season_id)

    if db.get(Race, payload.race_id) is None:
        raise HTTPException(status_code=422, detail=f"Race {payload.race_id} does not exist")

    clash = db.scalar(select(Team).where(Team.season_id == season_id, Team.name == payload.name))
    if clash is not None:
        raise HTTPException(status_code=409, detail=NAME_TAKEN)

    team = Team(season_id=season_id, treasury=season.starting_treasury, **payload.model_dump())
    db.add(team)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=NAME_TAKEN)
    db.refresh(team)
    return team


@router.get("/teams/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)):
    return get_team_or_404(db, team_id)
