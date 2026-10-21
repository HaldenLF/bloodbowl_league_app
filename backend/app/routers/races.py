from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models.races import Race
from app.schemas.races import RaceDetail, RaceOut

router = APIRouter(prefix="/races", tags=["races"])


@router.get("", response_model=list[RaceOut])
def list_races(db: Session = Depends(get_db)):
    return db.scalars(select(Race).order_by(Race.name)).all()


@router.get("/{race_id}", response_model=RaceDetail)
def get_race(race_id: int, db: Session = Depends(get_db)):
    race = db.scalar(
        select(Race)
        .where(Race.id == race_id)
        .options(selectinload(Race.positions), selectinload(Race.affiliations))
    )
    if race is None:
        raise HTTPException(status_code=404, detail="Race not found")
    return race