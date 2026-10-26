import pytest

from app.models.players import Player
from app.models.users import AccountType


@pytest.fixture
def setup(commissioner, coach, race, make_league, make_season, add_member, make_team, make_position):
    league = make_league(commissioner)
    season = make_season(commissioner, league, starting_treasury=200_000)
    add_member(coach, league)
    team = make_team(coach, season, race)
    position = make_position(race, cost=50_000, max_allowed=2)
    return league, season, team, position


def hire(client, auth, user, team, position, number, **extra):
    return client.post(
        f"/teams/{team['id']}/players",
        json={"position_id": position.id, "number": number, **extra},
        headers=auth(user),
    )


def test_coach_hires_player_and_pays_from_treasury(client, auth, coach, setup):
    league, season, team, position = setup
    response = hire(client, auth, coach, team, position, 7, name="Griff")
    assert response.status_code == 201
    assert response.json()["position"]["id"] == position.id
    assert client.get(f"/teams/{team['id']}", headers=auth(coach)).json()["treasury"] == 150_000


def test_client_cannot_set_player_stats(client, auth, coach, setup):
    league, season, team, position = setup
    player = hire(client, auth, coach, team, position, 7, touchdowns=50, mvps=9, team_id=999).json()
    assert player["touchdowns"] == 0 and player["mvps"] == 0 and player["team_id"] == team["id"]


def test_commissioner_can_hire_for_any_team_in_league(client, auth, commissioner, setup):
    league, season, team, position = setup
    assert hire(client, auth, commissioner, team, position, 7).status_code == 201


def test_other_member_cannot_hire_for_my_team(client, auth, make_user, add_member, setup):
    league, season, team, position = setup
    rival = make_user(AccountType.COACH)
    add_member(rival, league)
    assert hire(client, auth, rival, team, position, 7).status_code == 403


def test_outsiders_cannot_hire(client, auth, make_user, super_admin, setup):
    league, season, team, position = setup
    for outsider in (make_user(AccountType.COACH), super_admin):
        assert hire(client, auth, outsider, team, position, 7).status_code == 404


def test_position_must_exist_and_match_race(client, auth, coach, make_position, make_race, setup):
    league, season, team, position = setup
    other_race_position = make_position(make_race())
    assert hire(client, auth, coach, team, other_race_position, 7).status_code == 422
    response = client.post(f"/teams/{team['id']}/players", json={"position_id": 999999, "number": 7}, headers=auth(coach))
    assert response.status_code == 422


def test_position_limit(client, auth, coach, setup):
    league, season, team, position = setup
    assert hire(client, auth, coach, team, position, 1).status_code == 201
    assert hire(client, auth, coach, team, position, 2).status_code == 201
    assert hire(client, auth, coach, team, position, 3).status_code == 409


def test_number_must_be_unused(client, auth, coach, setup):
    league, season, team, position = setup
    hire(client, auth, coach, team, position, 7)
    assert hire(client, auth, coach, team, position, 7).status_code == 409


def test_dead_players_free_their_number_and_slot(client, auth, coach, db, setup):
    league, season, team, position = setup
    first = hire(client, auth, coach, team, position, 7).json()
    hire(client, auth, coach, team, position, 8)
    db.get(Player, first["id"]).dead = True
    db.flush()
    assert hire(client, auth, coach, team, position, 7).status_code == 201


def test_cannot_hire_without_enough_gold(client, auth, coach, make_position, race, setup):
    league, season, team, position = setup
    expensive = make_position(race, cost=250_000)
    response = hire(client, auth, coach, team, expensive, 7)
    assert response.status_code == 409
    assert client.get(f"/teams/{team['id']}", headers=auth(coach)).json()["treasury"] == 200_000


def test_members_can_read_roster_outsiders_cannot(client, auth, coach, commissioner, make_user, setup):
    league, season, team, position = setup
    player = hire(client, auth, coach, team, position, 7).json()
    roster = client.get(f"/teams/{team['id']}/players", headers=auth(commissioner)).json()
    assert [item["id"] for item in roster] == [player["id"]]
    assert client.get(f"/players/{player['id']}", headers=auth(commissioner)).status_code == 200

    outsider = make_user(AccountType.COACH)
    assert client.get(f"/teams/{team['id']}/players", headers=auth(outsider)).status_code == 404
    hidden = client.get(f"/players/{player['id']}", headers=auth(outsider))
    missing = client.get("/players/999999", headers=auth(outsider))
    assert hidden.status_code == 404
    assert hidden.json() == missing.json()
