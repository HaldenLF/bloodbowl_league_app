from app.core.database import Base
from sqlalchemy import Integer, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column


class Inducement(Base):
    __tablename__ = "inducements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    max_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    affiliated_league: Mapped[str | None] = mapped_column(String(100), nullable=True)