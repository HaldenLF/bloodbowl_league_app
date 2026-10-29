import pytest
from sqlalchemy.exc import IntegrityError

from app.models.players import Player
from app.models.users import AccountType


@pytest.fixture
def roster(client, auth, commissioner, coach, race, make_league, make_season, add_member, make_team, make_position):
    league = make_league(commissioner)
    season = make_season(commissioner, league, starting_treasury=500_000)
    add_member(coach, league)
    team = make_team(coach, season, race)
    position = make_position(race, cost=50_000, max_allowed=2)

    def hire(number):
        response = client.post(
            f"/teams/{team['id']}/players", json={"position_id": position.id, "number": number}, headers=auth(coach)
        )
        assert response.status_code == 201, response.text
        return response.json()

    return league, team, position, hire


def test_coach_renames_and_renumbers_player(client, auth, coach, roster):
    league, team, position, hire = roster
    player = hire(7)
    response = client.patch(f"/players/{player['id']}", json={"name": "Griff Oberwald", "number": 9}, headers=auth(coach))
    assert response.status_code == 200
    assert response.json()["name"] == "Griff Oberwald" and response.json()["number"] == 9


def test_patch_changes_only_the_fields_sent(client, auth, coach, roster):
    league, team, position, hire = roster
    player = hire(7)
    client.patch(f"/players/{player['id']}", json={"name": "Griff"}, headers=auth(coach))
    response = client.patch(f"/players/{player['id']}", json={"number": 8}, headers=auth(coach))
    assert response.json()["name"] == "Griff" and response.json()["number"] == 8
    cleared = client.patch(f"/players/{player['id']}", json={"name": None}, headers=auth(coach))
    assert cleared.json()["name"] is None


def test_number_cannot_be_cleared(client, auth, coach, roster):
    league, team, position, hire = roster
    player = hire(7)
    assert client.patch(f"/players/{player['id']}", json={"number": None}, headers=auth(coach)).status_code == 422


def test_patch_cannot_touch_stats(client, auth, coach, roster):
    league, team, position, hire = roster
    player = hire(7)
    response = client.patch(f"/players/{player['id']}", json={"touchdowns": 40, "dead": True}, headers=auth(coach))
    assert response.json()["touchdowns"] == 0 and response.json()["dead"] is False


def test_number_change_must_be_free(client, auth, coach, roster):
    league, team, position, hire = roster
    first, second = hire(7), hire(8)
    assert client.patch(f"/players/{second['id']}", json={"number": 7}, headers=auth(coach)).status_code == 409
    assert client.patch(f"/players/{first['id']}", json={"number": 7}, headers=auth(coach)).status_code == 200


def test_only_team_editors_can_change_players(client, auth, make_user, add_member, super_admin, roster):
    league, team, position, hire = roster
    player = hire(7)
    rival = make_user(AccountType.COACH)
    add_member(rival, league)
    assert client.patch(f"/players/{player['id']}", json={"name": "X"}, headers=auth(rival)).status_code == 403
    assert client.post(f"/players/{player['id']}/fire", headers=auth(rival)).status_code == 403
    for outsider in (make_user(AccountType.COACH), super_admin):
        assert client.patch(f"/players/{player['id']}", json={"name": "X"}, headers=auth(outsider)).status_code == 404
        assert client.post(f"/players/{player['id']}/fire", headers=auth(outsider)).status_code == 404


def test_fired_player_keeps_history_and_frees_number_and_slot(client, auth, coach, roster):
    league, team, position, hire = roster
    first, second = hire(7), hire(8)
    treasury_before = client.get(f"/teams/{team['id']}", headers=auth(coach)).json()["treasury"]

    fired = client.post(f"/players/{first['id']}/fire", headers=auth(coach))
    assert fired.status_code == 200 and fired.json()["fired"] is True
    assert client.get(f"/teams/{team['id']}", headers=auth(coach)).json()["treasury"] == treasury_before
    assert client.get(f"/players/{first['id']}", headers=auth(coach)).status_code == 200

    current = client.get(f"/teams/{team['id']}/players", headers=auth(coach)).json()
    assert [p["id"] for p in current] == [second["id"]]
    everyone = client.get(f"/teams/{team['id']}/players", params={"include_former": True}, headers=auth(coach)).json()
    assert sorted(p["id"] for p in everyone) == sorted([first["id"], second["id"]])

    assert hire(7)["number"] == 7


def test_commissioner_can_fire(client, auth, commissioner, roster):
    league, team, position, hire = roster
    player = hire(7)
    assert client.post(f"/players/{player['id']}/fire", headers=auth(commissioner)).status_code == 200


def test_former_players_cannot_be_fired_or_edited(client, auth, coach, db, roster):
    league, team, position, hire = roster
    fired, dead = hire(7), hire(8)
    client.post(f"/players/{fired['id']}/fire", headers=auth(coach))
    db.get(Player, dead["id"]).dead = True
    db.flush()
    for player in (fired, dead):
        assert client.post(f"/players/{player['id']}/fire", headers=auth(coach)).status_code == 409
        assert client.patch(f"/players/{player['id']}", json={"name": "X"}, headers=auth(coach)).status_code == 409


def test_database_refuses_two_roster_players_with_one_number(db, roster):
    league, team, position, hire = roster
    hire(7)
    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.add(Player(team_id=team["id"], position_id=position.id, number=7))
