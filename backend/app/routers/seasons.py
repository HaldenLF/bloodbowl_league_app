from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import get_league_for_manager, get_league_for_member, get_season_for_member
from app.core.deps import get_current_user
from app.models.seasons import Season
from app.models.users import User
from app.schemas.seasons import SeasonCreate, SeasonOut

router = APIRouter(tags=["seasons"])
NAME_TAKEN = "This league already has a season with that name"

# temp. remove later
def get_season_or_404(db: Session, season_id: int) -> Season:
    season = db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return season


@router.get("/leagues/{league_id}/seasons", response_model=list[SeasonOut])
def list_seasons(league_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_league_for_member(db, league_id, user)
    return db.scalars(
        select(Season).where(Season.league_id == league_id).order_by(Season.id)
    ).all()


@router.post("/leagues/{league_id}/seasons", response_model=SeasonOut, status_code=201)
def create_season(league_id: int, payload: SeasonCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_league_for_manager(db, league_id, user)
    clash = db.scalar(select(Season).where(Season.league_id == league_id, Season.name == payload.name))
    
    if clash is not None:
        raise HTTPException(status_code=409, detail="NAME_TAKEN")

    season = Season(league_id=league_id, **payload.model_dump())
    db.add(season)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="NAME_TAKEN")
    db.refresh(season)
    return season


@router.get("/seasons/{season_id}", response_model=SeasonOut)
def get_season(season_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_season_for_member(db, season_id, user)