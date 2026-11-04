from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import get_player_for_editor, get_player_for_member, get_team_for_editor, get_team_for_member
from app.models.players import Player
from app.models.positions import Position
from app.models.races import Race
from app.models.users import User
from app.rules.roster import MIN_PLAYERS_FOR_A_GAME, is_journeyman, journeymen_allowed, lowest_free_number
from app.rules.spp import star_player_points
from app.rules.team_value import player_value
from app.schemas.players import PlayerCreate, PlayerOut, PlayerUpdate, RosterPlayerOut


router = APIRouter(tags=["players"])
ON_ROSTER = (Player.dead.is_(False), Player.fired.is_(False))


def number_taken(number: int) -> HTTPException:
    return HTTPException(status_code=409, detail=f"Number {number} is already taken")


def require_on_roster(player: Player) -> None:
    if player.dead or player.fired:
        raise HTTPException(status_code=409, detail="This player is no longer on the roster")


def roster_line(player: Player, race: Race) -> RosterPlayerOut:
    return RosterPlayerOut(
        **PlayerOut.model_validate(player).model_dump(),
        spp=star_player_points(player),
        value=player_value(player, race),
    )


@router.get("/teams/{team_id}/players", response_model=list[RosterPlayerOut])
def list_players(team_id: int, include_former: bool = False, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    team = get_team_for_member(db, team_id, user)
    query = select(Player).where(Player.team_id == team_id)
    if not include_former:
        query = query.where(*ON_ROSTER)
    players = db.scalars(
        query.options(selectinload(Player.position), selectinload(Player.advancements)).order_by(Player.number)
    ).all()
    return [roster_line(player, team.race) for player in players]



@router.post("/teams/{team_id}/players", response_model=PlayerOut, status_code=201)
def hire_player(team_id: int, payload: PlayerCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    
    team = get_team_for_editor(db, team_id, user)
    db.refresh(team, with_for_update=True)

    position = db.get(Position, payload.position_id)
    if position is None:
        raise HTTPException(status_code=422, detail=f"Position {payload.position_id} does not exist")
    if position.race_id != team.race_id:
        raise HTTPException(status_code=422, detail="That position is not available to this team's race")

    roster = db.scalars(select(Player).where(Player.team_id == team.id, *ON_ROSTER)).all()
    if is_journeyman(position):
        available = sum(1 for player in roster if not player.missing_next_game)
        if not journeymen_allowed(available):
            raise HTTPException(
                status_code=409,
                detail=f"Journeymen can only be hired while fewer than {MIN_PLAYERS_FOR_A_GAME} players are available",
            )
    if sum(1 for player in roster if player.position_id == position.id) >= position.max_allowed:
        raise HTTPException(status_code=409, detail=f"This team already has the maximum of {position.max_allowed} {position.name}")

    taken = {player.number for player in roster}
    number = lowest_free_number(taken) if payload.number is None else payload.number
    if number is None:
        raise HTTPException(status_code=409, detail="Every shirt number is already taken")
    if number in taken:
        raise number_taken(number)
    if team.treasury < position.cost:
        raise HTTPException(status_code=409, detail="Not enough gold in the treasury")

    team.treasury -= position.cost
    player = Player(team_id=team.id, position_id=position.id, number=number, name=payload.name)
    db.add(player)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise number_taken(number)
    db.refresh(player)
    return player


@router.get("/players/{player_id}", response_model=PlayerOut)
def get_player(player_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_player_for_member(db, player_id, user)


@router.patch("/players/{player_id}", response_model=PlayerOut)
def update_player(player_id: int, payload: PlayerUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    player = get_player_for_editor(db, player_id, user)
    db.refresh(player.team, with_for_update=True)
    require_on_roster(player)

    changes = payload.model_dump(exclude_unset=True)
    new_number = changes.get("number", player.number)
    if new_number != player.number:
        clash = select(Player).where(Player.team_id == player.team_id, Player.number == new_number, *ON_ROSTER)
        if db.scalar(clash) is not None:
            raise number_taken(new_number)

    for field, value in changes.items():
        setattr(player, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise number_taken(new_number)
    db.refresh(player)
    return player


@router.post("/players/{player_id}/fire", response_model=PlayerOut)
def fire_player(player_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    player = get_player_for_editor(db, player_id, user)
    require_on_roster(player)
    player.fired = True
    db.commit()
    db.refresh(player)
    return player