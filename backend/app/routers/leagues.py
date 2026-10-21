from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.league import League
from app.schemas.leagues import LeagueCreate, LeagueOut

router = APIRouter(prefix="/leagues", tags=["leagues"])


def get_league_or_404(db: Session, league_id: int) -> League:
    league = db.get(League, league_id)
    if league is None:
        raise HTTPException(status_code=404, detail="League not found")
    return league


@router.get("", response_model=list[LeagueOut])
def list_leagues(db: Session = Depends(get_db)):
    return db.scalars(select(League).order_by(League.name)).all()


@router.get("/{league_id}", response_model=LeagueOut)
def get_league(league_id: int, db: Session = Depends(get_db)):
    league = db.get(League, league_id)
    if league is None:
        raise HTTPException(status_code=404, detail="League not found")
    return get_league_or_404(db, league_id)


@router.post("", response_model=LeagueOut, status_code=201)
def create_league(payload: LeagueCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(League).where(League.name == payload.name))
    if existing is not None:
        raise HTTPException(status_code=409, detail="A league with that name already exists")

    league = League(**payload.model_dump())
    db.add(league)
    db.commit()
    db.refresh(league)
    return league