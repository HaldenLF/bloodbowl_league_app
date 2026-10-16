from app.core.database import Base
from sqlalchemy import Integer, String, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Position(Base):
    __tablename__ = "positions"
    __table_args__ = (
        UniqueConstraint("race_id", "name", name="uq_positions_race_id_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    max_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    movement: Mapped[int] = mapped_column(Integer, nullable=False)
    strength: Mapped[int] = mapped_column(Integer, nullable=False)
    agility: Mapped[int] = mapped_column(Integer, nullable=False)
    passing: Mapped[int] = mapped_column(Integer, nullable=False)
    armor: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_list: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    primary_access: Mapped[str | None] = mapped_column(String(100), nullable=True)
    secondary_access: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    race: Mapped["Race"] = relationship(back_populates="positions")
    