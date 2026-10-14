import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Enum, ForeignKey, String, UniqueConstraint, DateTime, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class TournamentFormat(str, enum.Enum):
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS = "swiss"
    

class Tournament(Base):
    __tablename__ = "tournaments"
    __table_args__ = (UniqueConstraint("league_id", "name", name="uq_tournaments_league_id_name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    format: Mapped[TournamentFormat] = mapped_column(Enum(TournamentFormat, name="tournament_format"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    league: Mapped["League"] = relationship(back_populates="tournaments")
    matches: Mapped[list["TournamentMatch"]] = relationship(back_populates="tournament")
