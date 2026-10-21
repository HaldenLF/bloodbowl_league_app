from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models.inducements import Inducement
from app.schemas.inducements import InducementOut

router = APIRouter(prefix="/inducements", tags=["inducements"])

@router.get("", response_model=list[InducementOut])
def list_inducements(category: str | None = None, db: Session = Depends(get_db)):
    stmt = (
        select(Inducement)
        .options(selectinload(Inducement.affiliations))
        .order_by(Inducement.category, Inducement.name)
    )
    if category is not None:
        stmt = stmt.where(Inducement.category == category)
    return db.scalars(stmt).all()
