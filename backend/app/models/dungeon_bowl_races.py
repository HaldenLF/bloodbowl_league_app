from app.core.database import Base
from sqlalchemy import Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class db_Race(Base):
    __tablename__ = "db_races"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tier: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reroll_cost: Mapped[int | None] = mapped_column(Integer, nullable=True)
    affiliated_league: Mapped[str | None] = mapped_column(String(100), nullable=True)
    apothecary_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    special_rule_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    positions: Mapped[list["db_position"]] = relationship(back_populates="race")