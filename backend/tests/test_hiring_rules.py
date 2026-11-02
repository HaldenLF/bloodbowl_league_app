import pytest

from app.models.players import Player


@pytest.fixture
def squad(client, auth, commissioner, coach, race, make_league, make_season, add_member, make_team, make_position):
    league = make_league(commissioner)
    season = make_season(commissioner, league, starting_treasury=2_000_000)
    add_member(coach, league)
    team = make_team(coach, season, race)
    lineman = make_position(race, cost=50_000, max_allowed=16)
    journeyman = make_position(race, cost=50_000, max_allowed=16, name="Journeyman Lineman")

    def hire(position, **body):
        return client.post(
            f"/teams/{team['id']}/players", json={"position_id": position.id, **body}, headers=auth(coach)
        )

    return team, lineman, journeyman, hire


def test_numbers_are_assigned_automatically(squad):
    team, lineman, journeyman, hire = squad
    assert [hire(lineman).json()["number"] for _ in range(3)] == [1, 2, 3]


def test_fired_players_number_is_reused(client, auth, coach, squad):
    team, lineman, journeyman, hire = squad
    first, second = hire(lineman).json(), hire(lineman).json()
    client.post(f"/players/{first['id']}/fire", headers=auth(coach))
    assert hire(lineman).json()["number"] == first["number"]
    assert second["number"] == 2


def test_a_chosen_number_is_still_accepted(squad):
    team, lineman, journeyman, hire = squad
    assert hire(lineman, number=12).json()["number"] == 12
    assert hire(lineman).json()["number"] == 1


def test_journeyman_refused_with_eleven_available_players(squad):
    team, lineman, journeyman, hire = squad
    for _ in range(11):
        hire(lineman)
    response = hire(journeyman)
    assert response.status_code == 409


def test_journeyman_allowed_below_eleven(squad):
    team, lineman, journeyman, hire = squad
    for _ in range(10):
        hire(lineman)
    assert hire(journeyman).status_code == 201


def test_players_missing_the_next_game_do_not_count(db, squad):
    team, lineman, journeyman, hire = squad
    players = [hire(lineman).json() for _ in range(11)]
    db.get(Player, players[0]["id"]).missing_next_game = True
    db.flush()
    assert hire(journeyman).status_code == 201
