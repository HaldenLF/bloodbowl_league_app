import enum
from sqlalchemy import String, Boolean, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class LeagueFormat(str, enum.Enum):
    SIXTEENS = "16s"
    SEVENS = "7s"
    DUNGEON_BOWL = "dungeon_bowl"
    

class Season(Base):
    __tablename__ = "seasons"
    __table_args__ = (UniqueConstraint("league_id", "name", name="uq_seasons_league_id_name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    teams: Mapped[list["Team"]] = relationship(back_populates="season")
    format: Mapped[LeagueFormat] = mapped_column(Enum(LeagueFormat, name="league_format"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    league: Mapped["League"] = relationship(back_populates="seasons")
    
    games: Mapped[list["Game"]] = relationship(back_populates="season")
