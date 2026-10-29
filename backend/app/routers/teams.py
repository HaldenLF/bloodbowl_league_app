from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import can_manage_league, get_season_for_member, get_team_for_member, is_league_member, get_team_for_editor
from app.core.pagination import PageParams
from app.models.races import Race
from app.models.teams import Team
from app.models.users import User
from app.models.game_results import GameResult
from app.models.games import Game
from app.models.players import Player
from app.rules.team_extras import RULES, TeamExtra, unit_price
from app.rules.team_value import team_value
from app.schemas.teams import PurchaseCreate, TeamCreate, TeamOut, TeamValueOut

router = APIRouter(tags=["teams"])
NAME_TAKEN = "This season already has a team with that name"
COACH_TAKEN = "This coach already has a team in this season"


@router.get("/seasons/{season_id}/teams", response_model=list[TeamOut])
def list_teams(season_id: int, page: PageParams, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_season_for_member(db, season_id, user)
    return db.scalars(
        select(Team).where(Team.season_id == season_id).options(selectinload(Team.coach)).order_by(Team.name)
        .limit(page.limit).offset(page.offset)).all()


@router.post("/seasons/{season_id}/teams", response_model=TeamOut, status_code=201)
def create_team(season_id: int, payload: TeamCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    season = get_season_for_member(db, season_id, user)

    coach_id = user.id if payload.coach_id is None else payload.coach_id
    if coach_id != user.id:
        if not can_manage_league(season.league, user):
            raise HTTPException(status_code=403, detail="Only the league's commissioner can create a team for someone else")
        coach = db.get(User, coach_id)
        if coach is None or not is_league_member(db, season.league, coach):
            raise HTTPException(status_code=422, detail="That coach is not a member of this league")
    if db.get(Race, payload.race_id) is None:
        raise HTTPException(status_code=422, detail=f"Race {payload.race_id} does not exist")
    if db.scalar(select(Team).where(Team.season_id == season_id, Team.coach_id == coach_id)) is not None:
        raise HTTPException(status_code=409, detail=COACH_TAKEN)
    if db.scalar(select(Team).where(Team.season_id == season_id, Team.name == payload.name)) is not None:
        raise HTTPException(status_code=409, detail=NAME_TAKEN)

    team = Team(
        season_id=season_id,
        coach_id=coach_id,
        race_id=payload.race_id,
        name=payload.name,
        treasury=season.starting_treasury,
    )
    db.add(team)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A team with that name or coach already exists in this season")
    db.refresh(team)
    return team


@router.get("/teams/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_team_for_member(db, team_id, user)


def has_played(db: Session, team: Team) -> bool:
    played = (
        select(Game.id)
        .join(GameResult, GameResult.game_id == Game.id)
        .where(or_(Game.home_team_id == team.id, Game.away_team_id == team.id))
        .limit(1)
    )
    return db.scalar(played) is not None


@router.post("/teams/{team_id}/purchases", response_model=TeamOut)
def buy_extra(
    team_id: int, payload: PurchaseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    team = get_team_for_editor(db, team_id, user)
    db.refresh(team, with_for_update=True)

    rule = RULES[payload.item]
    played = has_played(db, team)
    if payload.item is TeamExtra.APOTHECARY and not team.race.apothecary_allowed:
        raise HTTPException(status_code=409, detail="This team's race cannot have an apothecary")
    if payload.item is TeamExtra.DEDICATED_FAN and played:
        raise HTTPException(status_code=409, detail="Dedicated fans can only be bought before the team's first game")

    owned = getattr(team, rule.team_field)
    if owned + payload.quantity > rule.maximum:
        raise HTTPException(status_code=409, detail=f"A team can have at most {rule.maximum} of these")

    price = unit_price(payload.item, team.race, team.season.format, played)
    if price is None:
        raise HTTPException(status_code=409, detail="This race has no re-roll price for this season's format")
    cost = price * payload.quantity
    if team.treasury < cost:
        raise HTTPException(status_code=409, detail="Not enough gold in the treasury")

    team.treasury -= cost
    setattr(team, rule.team_field, owned + payload.quantity)
    db.commit()
    db.refresh(team)
    return team


@router.get("/teams/{team_id}/value", response_model=TeamValueOut)
def get_team_value(team_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    team = get_team_for_member(db, team_id, user)
    players = db.scalars(
        select(Player)
        .where(Player.team_id == team.id)
        .options(selectinload(Player.position), selectinload(Player.advancements))
    ).all()
    value = team_value(team, players, team.season.format)
    return TeamValueOut(players=value.players, re_rolls=value.re_rolls, staff=value.staff, total=value.total)
