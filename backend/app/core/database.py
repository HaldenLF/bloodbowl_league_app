from sqlalchemy import create_engine, Table, Column, ForeignKey
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import Settings

from collections.abc import Generator

engine = create_engine(Settings().database_url)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
race_affiliations = Table(
    "race_affiliations",
    Base.metadata,
    Column("race_id", ForeignKey("races.id"), primary_key=True),
    Column("affiliation_id", ForeignKey("affiliations.id"), primary_key=True),
)

star_player_affiliations = Table(
    "star_player_affiliations",
    Base.metadata,
    Column("star_player_id", ForeignKey("star_players.id"), primary_key=True),
    Column("affiliation_id", ForeignKey("affiliations.id"), primary_key=True),
)

inducements_affiliations = Table(
    "inducements_affiliations",
    Base.metadata,
    Column("inducement_id", ForeignKey("inducements.id"), primary_key=True),
    Column("affiliation_id", ForeignKey("affiliations.id"), primary_key=True),
)

mercenaries_affiliations = Table(
    "mercenary_affiliations",
    Base.metadata,
    Column("mercenary_id", ForeignKey("mercenaries.id"), primary_key=True),
    Column("affiliation_id", ForeignKey("affiliations.id"), primary_key=True),
)

dungeon_bowl_affiliations = Table(
    "dungeon_bowl_affiliations",
    Base.metadata,
    Column("db_race_id", ForeignKey("db_races.id"), primary_key=True),
    Column("affiliation_id", ForeignKey("affiliations.id"), primary_key=True),
)