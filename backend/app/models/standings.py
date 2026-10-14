from sqlalchemy import CheckConstraint, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Standing(Base):
    __tablename__ = "standings"
    __table_args__ = (UniqueConstraint("season_id", "team_id", name="uq_standings_season_id_team_id"),
        CheckConstraint(
            "wins >= 0 AND draws >= 0 AND losses >= 0 AND touchdowns_for >= 0 "
            "AND touchdowns_against >= 0 AND casualties_for >= 0 AND casualties_against >= 0",
            name="ck_standings_counts_non_negative",),)
    
    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    wins: Mapped[int] = mapped_column(nullable=False, server_default="0")
    losses: Mapped[int] = mapped_column(nullable=False, server_default="0")
    draws: Mapped[int] = mapped_column(nullable=False, server_default="0")
    touchdowns_for: Mapped[int] = mapped_column(nullable=False, server_default="0")
    touchdowns_against: Mapped[int] = mapped_column(nullable=False, server_default="0")
    casualties_for: Mapped[int] = mapped_column(nullable=False, server_default="0")
    casualties_against: Mapped[int] = mapped_column(nullable=False, server_default="0")
    
    season: Mapped["Season"] = relationship()
    team: Mapped["Team"] = relationship()