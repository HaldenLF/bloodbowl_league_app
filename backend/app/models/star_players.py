from app.core.database import Base
from sqlalchemy import Integer, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import star_player_affiliations

class StarPlayer(Base):
    __tablename__ = "star_players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    max_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    movement: Mapped[int] = mapped_column(Integer, nullable=False)
    strength: Mapped[int] = mapped_column(Integer, nullable=False)
    agility: Mapped[int] = mapped_column(Integer, nullable=False)
    passing: Mapped[int] = mapped_column(Integer, nullable=False)
    armor: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_list: Mapped[str | None] = mapped_column(Text, nullable=True)
    affiliations: Mapped[list["Affiliation"]] = relationship(secondary=star_player_affiliations, back_populates="star_players")
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    upkeep: Mapped[int] = mapped_column(Integer, nullable=False)
    special_rule: Mapped[str | None] = mapped_column(Text, nullable=True)