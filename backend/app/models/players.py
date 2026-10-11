from datetime import datetime
from sqlalchemy import Integer, String, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Player(Base):
    __tablename__ = "players"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id"), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    coach_name: Mapped[str] = mapped_column(String(100), nullable=False)
    completions: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    touchdowns: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    interceptions: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    casualties: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    mvps: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    niggling_injuries: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    missing_next_game: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    dead: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    team: Mapped["Team"] = relationship("Team", back_populates="players")
    position: Mapped["Position"] = relationship("Position", back_populates="players")
    