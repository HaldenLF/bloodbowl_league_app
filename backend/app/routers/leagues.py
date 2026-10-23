from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import StringConstraints
from sqlalchemy import select, or_
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.deps import get_current_user, require_account_type
from app.core.permissions import get_league_for_member, LEAGUE_NOT_FOUND, get_league_for_manager, get_membership
from app.core.security import generate_join_code
from app.models.league import League, JoinPolicy
from app.models.league_members import LeagueMember, MembershipStatus
from app.models.users import AccountType, User
from app.schemas.leagues import LeagueCreate, LeagueOut, LeagueCreatedOut, LeagueSearchOut, JoinByCode, JoinCodeOut, MemberOut, MembershipOut


router = APIRouter(prefix="/leagues", tags=["leagues"])
NAME_TAKEN = "A league with that name already exists"
SearchText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100), Query()]
ALREADY_MEMBER = "You are already a member of this league or have a pending request"

# Temp
def get_league_or_404(db: Session, league_id: int) -> League:
    league = db.get(League, league_id)
    if league is None:
        raise HTTPException(status_code=404, detail="League not found")
    return league


def list_memberships(db: Session, league_id: int, status: MembershipStatus) -> list[LeagueMember]:
    return db.scalars(
        select(LeagueMember)
        .where(LeagueMember.league_id == league_id, LeagueMember.status == status)
        .options(selectinload(LeagueMember.user))
        .order_by(LeagueMember.joined_at)
    ).all()


def get_join_request_or_404(db: Session, league_id: int, user_id: int) -> LeagueMember:
    membership = get_membership(db, league_id, user_id)
    if membership is None or membership.status != MembershipStatus.PENDING:
        raise HTTPException(status_code=404, detail="Join request not found")
    return membership


def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@router.post("", response_model=LeagueCreatedOut, status_code=201)
def create_league(payload: LeagueCreate, db: Session = Depends(get_db), 
                  user: User = Depends(require_account_type(AccountType.COMMISSIONER))):
    
    if db.scalar(select(League).where(League.name == payload.name)) is not None:
        raise HTTPException(status_code=409, detail=NAME_TAKEN)
    
    league = League(name=payload.name, join_policy=payload.join_policy, owner_id=user.id)
    try:
        db.add(league)
        db.flush()
        db.add(LeagueMember(league_id=league.id, user_id=user.id, status=MembershipStatus.ACTIVE))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=NAME_TAKEN)
    db.refresh(league)
    return league


@router.get("", response_model=list[LeagueOut])
def list_my_leagues(db: Session = Depends(get_db), user: User=Depends(get_current_user)):
    my_active_leagues = select(LeagueMember.league_id).where(
        LeagueMember.user_id == user.id, LeagueMember.status == MembershipStatus.ACTIVE)
    return db.scalars(select(League)
                      .where(or_(League.owner_id == user.id, League.id.in_(my_active_leagues)))
                      .options(selectinload(League.owner))
                      .order_by(League.name)).all()

@router.get("/search", response_model=list[LeagueSearchOut])
def search_leagues(q: SearchText, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(
        select(League)
        .where(League.join_policy != JoinPolicy.INVITE_ONLY,League.name.ilike(f"%{escape_like(q)}%", escape="\\"),)
        .order_by(League.name)
        .limit(20)).all()


@router.post("/join", response_model=MembershipOut)
def join_by_code(payload: JoinByCode, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    league = db.scalar(select(League).where(League.join_code == payload.join_code))
    if league is None:
        raise HTTPException(status_code=404, detail="Invalid join code")
    membership = get_membership(db, league.id, user.id)
    if membership is None:
        membership = LeagueMember(league_id=league.id, user_id=user.id, status=MembershipStatus.ACTIVE)
        db.add(membership)
    else:
        membership.status = MembershipStatus.ACTIVE
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=ALREADY_MEMBER)
    db.refresh(membership)
    return membership


@router.get("/{league_id}", response_model=LeagueOut)
def get_league(league_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
        return get_league_for_member(db, league_id, user)


@router.post("/{league_id}/join", response_model=MembershipOut, status_code=201)
def request_to_join(league_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    league = db.get(League, league_id)
    if league is None or league.join_policy == JoinPolicy.INVITE_ONLY:
        raise HTTPException(status_code=404, detail=LEAGUE_NOT_FOUND)
    if get_membership(db, league_id, user.id) is not None:
        raise HTTPException(status_code=409, detail=ALREADY_MEMBER)
    status = MembershipStatus.ACTIVE if league.join_policy == JoinPolicy.OPEN else MembershipStatus.PENDING
    membership = LeagueMember(league_id=league_id, user_id=user.id, status=status)
    db.add(membership)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=ALREADY_MEMBER)
    db.refresh(membership)
    return membership


@router.get("/{league_id}/members", response_model=list[MemberOut])
def list_members(league_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_league_for_member(db, league_id, user)
    return list_memberships(db, league_id, MembershipStatus.ACTIVE)


@router.get("/{league_id}/join-code", response_model=JoinCodeOut)
def get_join_code(league_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_league_for_manager(db, league_id, user)


@router.post("/{league_id}/join-code/regenerate", response_model=JoinCodeOut)
def regenerate_join_code(league_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    league = get_league_for_manager(db, league_id, user)
    league.join_code = generate_join_code()
    db.commit()
    db.refresh(league)
    return league


@router.get("/{league_id}/join-requests", response_model=list[MemberOut])
def list_join_requests(league_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_league_for_manager(db, league_id, user)
    return list_memberships(db, league_id, MembershipStatus.PENDING)


@router.post("/{league_id}/join-requests/{user_id}/approve", response_model=MemberOut)
def approve_join_request(
    league_id: int, user_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    get_league_for_manager(db, league_id, user)
    membership = get_join_request_or_404(db, league_id, user_id)
    membership.status = MembershipStatus.ACTIVE
    db.commit()
    db.refresh(membership)
    return membership


@router.delete("/{league_id}/join-requests/{user_id}", status_code=204)
def reject_join_request(
    league_id: int, user_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    get_league_for_manager(db, league_id, user)
    db.delete(get_join_request_or_404(db, league_id, user_id))
    db.commit()
