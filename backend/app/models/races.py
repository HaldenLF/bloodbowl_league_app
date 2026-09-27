from app.core.database import Base
from sqlalchemy import Integer, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import race_affiliations

class Race(Base):
    __tablename__ = "races"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tier: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reroll_cost: Mapped[int | None] = mapped_column(Integer, nullable=True)
    apothecary_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    special_rule_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    affiliations: Mapped[list["Affiliation"]] = relationship(secondary=race_affiliations, back_populates="races")
    positions: Mapped[list["Position"]] = relationship(back_populates="race")
