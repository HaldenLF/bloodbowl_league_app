from datetime import datetime
from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TournamentMatch(Base):
    __tablename__ = "tournament_matches"
    __table_args__ = (
        UniqueConstraint("tournament_id", "round_number", "match_number", 
                         name="uq_tournament_matches_position",),
        CheckConstraint("round_number > 0", name="ck_tournament_matches_round_positive"),
        CheckConstraint("match_number > 0", name="ck_tournament_matches_match_positive"),
        CheckConstraint("team1_id IS NULL OR team2_id IS NULL OR team1_id <> team2_id",
                        name="ck_tournament_matches_teams_differ",),
        CheckConstraint("winner_id IS NULL OR winner_id = team1_id OR winner_id = team2_id",
                        name="ck_tournament_matches_winner_is_entrant",),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"), nullable=False, index=True)
    round_number: Mapped[int] = mapped_column(nullable=False)
    match_number: Mapped[int] = mapped_column(nullable=False)
    team1_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True, index=True)
    team2_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True, index=True)
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True, index=True)
    team1_touchdowns: Mapped[int | None] = mapped_column(nullable=True)
    team2_touchdowns: Mapped[int | None] = mapped_column(nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


    tournament: Mapped["Tournament"] = relationship(back_populates="matches")
    team1: Mapped["Team"] = relationship(foreign_keys=[team1_id])
    team2: Mapped["Team"] = relationship(foreign_keys=[team2_id])
    winner: Mapped["Team"] = relationship(foreign_keys=[winner_id])