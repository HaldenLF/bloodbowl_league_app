from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, UniqueConstraint, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Game(Base):
    __tablename__ = "games"
    __table_args__ = (UniqueConstraint("season_id", "round_number", "home_team_id", "away_team_id", 
                                       name="uq_games_season_round_home_away"),
                      CheckConstraint("round_number > 0", name="ck_games_round_number_positive"),
                      CheckConstraint("home_team_id <> away_team_id", name="ck_games_teams_differ"),)
    
    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False, index=True)
    round_number: Mapped[int] = mapped_column(nullable=False)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    season: Mapped["Season"] = relationship(back_populates="games")
    home_team: Mapped["Team"] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped["Team"] = relationship(foreign_keys=[away_team_id])
    
