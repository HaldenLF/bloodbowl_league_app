from app.core.database import Base
from sqlalchemy import Integer, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import mercenaries_affiliations

class Mercenary(Base):
    __tablename__ = "mercenaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    max_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    movement: Mapped[int] = mapped_column(Integer, nullable=False)
    strength: Mapped[int] = mapped_column(Integer, nullable=False)
    agility: Mapped[int] = mapped_column(Integer, nullable=False)
    passing: Mapped[int] = mapped_column(Integer, nullable=False)
    armor: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_list: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    upkeep: Mapped[int] = mapped_column(Integer, nullable=False)
    affiliations: Mapped[list["Affiliation"]] = relationship(secondary=mercenaries_affiliations, back_populates="mercenaries")
    special_rule: Mapped[str | None] = mapped_column(Text, nullable=True)