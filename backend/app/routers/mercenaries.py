from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models.affiliations import Affiliation
from app.models.mercenaries import Mercenary
from app.schemas.mercenaries import MercenaryOut

router = APIRouter(prefix="/mercenaries", tags=["mercenaries"])


@router.get("", response_model=list[MercenaryOut])
def list_mercenaries(affiliation: str | None = None, db: Session = Depends(get_db)):
    stmt = (
        select(Mercenary)
        .options(selectinload(Mercenary.affiliations))
        .order_by(Mercenary.name)
    )
    if affiliation is not None:
        stmt = stmt.where(Mercenary.affiliations.any(Affiliation.name == affiliation))
    return db.scalars(stmt).all()


@router.get("/{mercenary_id}", response_model=MercenaryOut)
def get_mercenary(mercenary_id: int, db: Session = Depends(get_db)):
    merc = db.scalar(
        select(Mercenary)
        .where(Mercenary.id == mercenary_id)
        .options(selectinload(Mercenary.affiliations))
    )
    if merc is None:
        raise HTTPException(status_code=404, detail="Mercenary not found")
    return merc