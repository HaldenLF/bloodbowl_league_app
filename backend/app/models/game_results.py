from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, UniqueConstraint, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class GameResult(Base):
    __tablename__ = "game_results"
    __table_args__ = (CheckConstraint(
                        "home_touchdowns >= 0 AND away_touchdowns >= 0 "
                        "AND home_casualties >= 0 AND away_casualties >= 0",
                        name="ck_game_results_counts_non_negative",),)
    
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), unique=True, nullable=False)
    home_touchdowns: Mapped[int] = mapped_column(nullable=False, server_default="0")
    away_touchdowns: Mapped[int] = mapped_column(nullable=False, server_default="0")
    home_casualties: Mapped[int] = mapped_column(nullable=False, server_default="0")
    away_casualties: Mapped[int] = mapped_column(nullable=False, server_default="0")
    home_winnings: Mapped[int] = mapped_column(nullable=False, server_default="0")
    away_winnings: Mapped[int] = mapped_column(nullable=False, server_default="0")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    game: Mapped["Game"] = relationship(back_populates="result")