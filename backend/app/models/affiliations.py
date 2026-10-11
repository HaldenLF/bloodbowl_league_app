from app.core.database import Base
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import race_affiliations, star_player_affiliations, inducements_affiliations, mercenaries_affiliations, dungeon_bowl_affiliations

class Affiliation(Base):
    __tablename__ = "affiliations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    races: Mapped[list["Race"]] = relationship(secondary=race_affiliations, back_populates="affiliations")
    star_players: Mapped[list["StarPlayer"]] = relationship(secondary=star_player_affiliations, back_populates="affiliations")
    inducements: Mapped[list["Inducement"]] = relationship(secondary=inducements_affiliations, back_populates="affiliations")
    mercenaries: Mapped[list["Mercenary"]] = relationship(secondary=mercenaries_affiliations, back_populates="affiliations")
    dungeon_bowl: Mapped[list["db_Race"]] = relationship(secondary=dungeon_bowl_affiliations, back_populates="affiliations")