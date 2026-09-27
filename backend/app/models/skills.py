from app.core.database import Base
from sqlalchemy import Integer, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    general: Mapped[bool] = mapped_column(Boolean, default=False)
    agility: Mapped[bool] = mapped_column(Boolean, default=False)
    strength: Mapped[bool] = mapped_column(Boolean, default=False)
    passing: Mapped[bool] = mapped_column(Boolean, default=False)
    mutation: Mapped[bool] = mapped_column(Boolean, default=False)
    devious: Mapped[bool] = mapped_column(Boolean, default=False)
    Elite: Mapped[bool] = mapped_column(Boolean, default=False)