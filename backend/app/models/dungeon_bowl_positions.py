from app.core.database import Base
from sqlalchemy import Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class db_position(Base):
    __tablename__ = "dungeon_bowl_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    db_race_id: Mapped[int] = mapped_column(ForeignKey("db_races.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    max_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    movement: Mapped[int] = mapped_column(Integer, nullable=False)
    strength: Mapped[int] = mapped_column(Integer, nullable=False)
    agility: Mapped[int] = mapped_column(Integer, nullable=False)
    passing: Mapped[int] = mapped_column(Integer, nullable=False)
    armor: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_list: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    primary_access: Mapped[bool] = mapped_column(String(100), nullable=False)
    secondary_access: Mapped[bool] = mapped_column(String(100), nullable=False)
    
    race: Mapped["db_Race"] = relationship(back_populates="positions")