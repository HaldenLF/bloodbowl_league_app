import enum
from datetime import datetime
from sqlalchemy import DateTime, func, String, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security import generate_join_code
from app.core.database import Base


class JoinPolicy(str, enum.Enum):
    INVITE_ONLY = "invite_only"
    OPEN = "open"
    APPROVAL = "approval"

class League(Base):
    __tablename__ = "leagues"
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_leagues_owner_id_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    seasons: Mapped[list["Season"]] = relationship(back_populates="league")
    
    tournaments: Mapped[list["Tournament"]] = relationship(back_populates="league")
    
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    join_policy: Mapped[JoinPolicy] = mapped_column(
        Enum(JoinPolicy, name="join_policy"), nullable=False, server_default="INVITE_ONLY"
    )
    join_code: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, default=generate_join_code
    )
    owner: Mapped["User"] = relationship()