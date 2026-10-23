from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.league import League
from app.models.league_members import LeagueMember, MembershipStatus
from app.models.users import User

LEAGUE_NOT_FOUND = "League not found"


def get_membership(db: Session, league_id: int, user_id: int) -> LeagueMember | None:
    return db.scalar(
        select(LeagueMember).where(LeagueMember.league_id == league_id, LeagueMember.user_id == user_id)
    )


def can_manage_league(league: League, user: User) -> bool:
    return league.owner_id == user.id


def get_league_for_member(db: Session, league_id: int, user: User) -> League:
    league = db.get(League, league_id)
    if league is None:
        raise HTTPException(status_code=404, detail=LEAGUE_NOT_FOUND)
    if can_manage_league(league, user):
        return league
    membership = get_membership(db, league_id, user.id)
    if membership is None or membership.status != MembershipStatus.ACTIVE:
        raise HTTPException(status_code=404, detail=LEAGUE_NOT_FOUND)
    return league


def get_league_for_manager(db: Session, league_id: int, user: User) -> League:
    league = get_league_for_member(db, league_id, user)
    if not can_manage_league(league, user):
        raise HTTPException(status_code=403, detail="Only the league's commissioner can do this")
    return league
