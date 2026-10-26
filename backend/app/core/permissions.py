from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.league import League
from app.models.league_members import LeagueMember, MembershipStatus
from app.models.users import User
from app.models.seasons import Season
from app.models.teams import Team
from app.models.players import Player

LEAGUE_NOT_FOUND = "League not found"
SEASON_NOT_FOUND = "Season not found"
TEAM_NOT_FOUND = "Team not found"
PLAYER_NOT_FOUND = "Player not found"


def get_membership(db: Session, league_id: int, user_id: int) -> LeagueMember | None:
    return db.scalar(
        select(LeagueMember).where(LeagueMember.league_id == league_id, LeagueMember.user_id == user_id)
    )


def can_manage_league(league: League, user: User) -> bool:
    return league.owner_id == user.id


def is_league_member(db: Session, league: League, user: User) -> bool:
    if can_manage_league(league, user):
        return True
    membership = get_membership(db, league.id, user.id)
    return membership is not None and membership.status == MembershipStatus.ACTIVE


def get_league_for_member(db: Session, league_id: int, user: User) -> League:
    league = db.get(League, league_id)
    if league is None or not is_league_member(db, league, user):
        raise HTTPException(status_code=404, detail=LEAGUE_NOT_FOUND)
    return league


def get_league_for_manager(db: Session, league_id: int, user: User) -> League:
    league = get_league_for_member(db, league_id, user)
    if not can_manage_league(league, user):
        raise HTTPException(status_code=403, detail="Only the league's commissioner can do this")
    return league


def get_season_for_member(db: Session, season_id: int, user: User) -> Season:
    season = db.get(Season, season_id)
    if season is None or not is_league_member(db, season.league, user):
        raise HTTPException(status_code=404, detail=SEASON_NOT_FOUND)
    return season


def get_team_for_member(db: Session, team_id: int, user: User) -> Team:
    team = db.get(Team, team_id)
    if team is None or not is_league_member(db, team.season.league, user):
        raise HTTPException(status_code=404, detail=TEAM_NOT_FOUND)
    return team


def can_edit_team(team: Team, user: User) -> bool:
    return team.coach_id == user.id or can_manage_league(team.season.league, user)


def get_team_for_editor(db: Session, team_id: int, user: User) -> Team:
    team = get_team_for_member(db, team_id, user)
    if not can_edit_team(team, user):
        raise HTTPException(status_code=403, detail="Only the team's coach or the league's commissioner can do this")
    return team


def get_player_for_member(db: Session, player_id: int, user: User) -> Player:
    player = db.get(Player, player_id)
    if player is None or not is_league_member(db, player.team.season.league, user):
        raise HTTPException(status_code=404, detail=PLAYER_NOT_FOUND)
    return player
