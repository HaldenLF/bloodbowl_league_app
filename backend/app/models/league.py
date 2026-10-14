from datetime import datetime
from sqlalchemy import DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class League(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    seasons: Mapped[list["Season"]] = relationship(back_populates="league")
    
    tournaments: Mapped[list["Tournament"]] = relationship(back_populates="league")