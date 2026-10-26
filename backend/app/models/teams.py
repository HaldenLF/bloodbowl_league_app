from datetime import datetime
from sqlalchemy import Integer, String, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (UniqueConstraint("season_id", "name", name="uq_teams_season_id_name"),
                      UniqueConstraint("season_id", "coach_id", name="uq_teams_season_id_coach_id"),)
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), nullable=False)
    season: Mapped["Season"] = relationship(back_populates="teams")
    race: Mapped["Race"] = relationship()
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    coach_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    coach: Mapped["User"] = relationship()
    treasury: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    re_rolls: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    assistant_coaches: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    cheerleaders: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    apothecary: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    dedicated_fans: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    players: Mapped[list["Player"]] = relationship(back_populates="team")