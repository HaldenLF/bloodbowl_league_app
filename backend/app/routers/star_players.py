from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models.affiliations import Affiliation
from app.models.star_players import StarPlayer
from app.schemas.star_players import StarPlayerOut

router = APIRouter(prefix="/star-players", tags=["star-players"])


@router.get("", response_model=list[StarPlayerOut])
def list_star_players(affiliation: str | None = None, db: Session = Depends(get_db)):
    stmt = (
        select(StarPlayer)
        .options(selectinload(StarPlayer.affiliations))
        .order_by(StarPlayer.name)
    )
    if affiliation is not None:
        stmt = stmt.where(StarPlayer.affiliations.any(Affiliation.name == affiliation))
    return db.scalars(stmt).all()


@router.get("/{star_player_id}", response_model=StarPlayerOut)
def get_star_player(star_player_id: int, db: Session = Depends(get_db)):
    star = db.scalar(
        select(StarPlayer)
        .where(StarPlayer.id == star_player_id)
        .options(selectinload(StarPlayer.affiliations))
    )
    if star is None:
        raise HTTPException(status_code=404, detail="Star player not found")
    return star