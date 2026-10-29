from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import can_manage_league, get_season_for_member, get_team_for_member, is_league_member
from app.core.pagination import PageParams
from app.models.races import Race
from app.models.teams import Team
from app.models.users import User
from app.schemas.teams import TeamCreate, TeamOut

router = APIRouter(tags=["teams"])
NAME_TAKEN = "This season already has a team with that name"
COACH_TAKEN = "This coach already has a team in this season"


@router.get("/seasons/{season_id}/teams", response_model=list[TeamOut])
def list_teams(season_id: int, page: PageParams, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_season_for_member(db, season_id, user)
    return db.scalars(
        select(Team).where(Team.season_id == season_id).options(selectinload(Team.coach)).order_by(Team.name)
        .limit(page.limit).offset(page.offset)).all()


@router.post("/seasons/{season_id}/teams", response_model=TeamOut, status_code=201)
def create_team(season_id: int, payload: TeamCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    season = get_season_for_member(db, season_id, user)

    coach_id = user.id if payload.coach_id is None else payload.coach_id
    if coach_id != user.id:
        if not can_manage_league(season.league, user):
            raise HTTPException(status_code=403, detail="Only the league's commissioner can create a team for someone else")
        coach = db.get(User, coach_id)
        if coach is None or not is_league_member(db, season.league, coach):
            raise HTTPException(status_code=422, detail="That coach is not a member of this league")
    if db.get(Race, payload.race_id) is None:
        raise HTTPException(status_code=422, detail=f"Race {payload.race_id} does not exist")
    if db.scalar(select(Team).where(Team.season_id == season_id, Team.coach_id == coach_id)) is not None:
        raise HTTPException(status_code=409, detail=COACH_TAKEN)
    if db.scalar(select(Team).where(Team.season_id == season_id, Team.name == payload.name)) is not None:
        raise HTTPException(status_code=409, detail=NAME_TAKEN)

    team = Team(
        season_id=season_id,
        coach_id=coach_id,
        race_id=payload.race_id,
        name=payload.name,
        treasury=season.starting_treasury,
    )
    db.add(team)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A team with that name or coach already exists in this season")
    db.refresh(team)
    return team


@router.get("/teams/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_team_for_member(db, team_id, user)
