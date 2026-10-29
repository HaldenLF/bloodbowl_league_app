import pytest

from app.models.players import Player
from app.models.users import AccountType


@pytest.fixture
def valued_team(client, auth, commissioner, coach, make_league, make_season, add_member, make_team, make_race, make_position):
    league = make_league(commissioner)
    season = make_season(commissioner, league, starting_treasury=1_000_000)
    add_member(coach, league)
    race = make_race()
    team = make_team(coach, season, race)
    position = make_position(race, cost=50_000, max_allowed=4)
    players = [
        client.post(f"/teams/{team['id']}/players", json={"position_id": position.id, "number": n}, headers=auth(coach)).json()
        for n in (1, 2)
    ]
    for item, quantity in (("re_roll", 2), ("apothecary", 1)):
        client.post(f"/teams/{team['id']}/purchases", json={"item": item, "quantity": quantity}, headers=auth(coach))
    return league, team, race, players


def test_team_value_breakdown(client, auth, coach, valued_team):
    league, team, race, players = valued_team
    response = client.get(f"/teams/{team['id']}/value", headers=auth(coach))
    assert response.status_code == 200
    assert response.json() == {
        "players": 100_000,
        "re_rolls": 2 * race.reroll_cost,
        "staff": 50_000,
        "total": 100_000 + 2 * race.reroll_cost + 50_000,
    }


def test_missing_next_game_lowers_team_value(client, auth, coach, db, valued_team):
    league, team, race, players = valued_team
    db.get(Player, players[0]["id"]).missing_next_game = True
    db.flush()
    assert client.get(f"/teams/{team['id']}/value", headers=auth(coach)).json()["players"] == 50_000


def test_members_can_read_team_value_outsiders_cannot(client, auth, commissioner, make_user, super_admin, valued_team):
    league, team, race, players = valued_team
    assert client.get(f"/teams/{team['id']}/value", headers=auth(commissioner)).status_code == 200
    for outsider in (make_user(AccountType.COACH), super_admin):
        assert client.get(f"/teams/{team['id']}/value", headers=auth(outsider)).status_code == 404
