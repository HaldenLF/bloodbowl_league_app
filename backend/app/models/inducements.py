from app.core.database import Base
from sqlalchemy import Integer, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import inducements_affiliations

class Inducement(Base):
    __tablename__ = "inducements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    max_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    affiliations: Mapped[list["Affiliation"]] = relationship(secondary=inducements_affiliations, back_populates="inducements")