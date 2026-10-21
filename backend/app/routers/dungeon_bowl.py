from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.dungeon_bowl_positions import db_position
from app.models.dungeon_bowl_races import db_Race
from app.schemas.dungeon_bowl import CollegeOut, DungeonBowlPositionOut

router = APIRouter(prefix="/dungeon-bowl", tags=["dungeon-bowl"])


def get_college_or_404(db: Session, college_id: int) -> db_Race:
    college = db.get(db_Race, college_id)
    if college is None:
        raise HTTPException(status_code=404, detail="College not found")
    return college


@router.get("/colleges", response_model=list[CollegeOut])
def list_colleges(db: Session = Depends(get_db)):
    return db.scalars(select(db_Race).order_by(db_Race.name)).all()


@router.get("/colleges/{college_id}", response_model=CollegeOut)
def get_college(college_id: int, db: Session = Depends(get_db)):
    return get_college_or_404(db, college_id)


@router.get("/colleges/{college_id}/positions", response_model=list[DungeonBowlPositionOut])
def list_college_positions(college_id: int, db: Session = Depends(get_db)):
    get_college_or_404(db, college_id) 
    return db.scalars(
        select(db_position)
        .where(db_position.db_race_id == college_id)
        .order_by(db_position.name)
    ).all()