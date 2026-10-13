import enum
from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, UniqueConstraint, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class AdvancementTier(str, enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    PRIMARY_ELITE = "primary_elite"
    SECONDARY_ELITE = "secondary_elite"

class StatType(str, enum.Enum):
    MA = "MA"
    ST = "ST"
    AG = "AG"
    PA = "PA"
    AV = "AV"

class PlayerAdvancement(Base):
    __tablename__ = "player_advancements"
    __table_args__ = (UniqueConstraint("player_id", "slot", name="uq_player_advancements_player_id_slot"),
        CheckConstraint("slot BETWEEN 1 AND 6", name="ck_player_advancements_slot_range"),
        CheckConstraint(
            "(skill_id IS NOT NULL) <> (stat_increase IS NOT NULL)",
            name="ck_player_advancements_skill_xor_stat",
        ),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    slot: Mapped[int] = mapped_column(nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=True)
    tier: Mapped[AdvancementTier | None] = mapped_column(Enum(AdvancementTier, name="advancement_tier"), nullable=True)
    stat_increase: Mapped[StatType | None] = mapped_column(Enum(StatType, name="stat_type"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    player: Mapped["Player"] = relationship(back_populates="advancements")
    skill: Mapped["Skill"] = relationship()
    