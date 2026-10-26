import pytest

from app.models.users import AccountType


@pytest.fixture
def setup(commissioner, coach, make_league, make_season, add_member):
    league = make_league(commissioner)
    season = make_season(commissioner, league, starting_treasury=1_000_000)
    add_member(coach, league)
    return league, season


def new_team(race, **extra):
    return {"race_id": race.id, "name": "The Reikland Reavers", **extra}


def test_member_creates_own_team_with_season_treasury(client, auth, coach, race, setup):
    league, season = setup
    response = client.post(f"/seasons/{season['id']}/teams", json=new_team(race), headers=auth(coach))
    assert response.status_code == 201
    team = response.json()
    assert team["coach"] == {"id": coach.id, "display_name": coach.display_name}
    assert team["treasury"] == 1_000_000


def test_client_cannot_set_treasury_or_buy_free_rerolls(client, auth, coach, race, setup):
    league, season = setup
    body = new_team(race, treasury=99_999_999, re_rolls=8, apothecary=1)
    team = client.post(f"/seasons/{season['id']}/teams", json=body, headers=auth(coach)).json()
    assert team["treasury"] == 1_000_000
    assert team["re_rolls"] == 0 and team["apothecary"] == 0


def test_one_team_per_coach_per_season(client, auth, coach, race, setup):
    league, season = setup
    client.post(f"/seasons/{season['id']}/teams", json=new_team(race), headers=auth(coach))
    response = client.post(f"/seasons/{season['id']}/teams", json=new_team(race, name="Second Team"), headers=auth(coach))
    assert response.status_code == 409


def test_outsiders_cannot_create_team(client, auth, make_user, super_admin, race, setup):
    league, season = setup
    for outsider in (make_user(AccountType.COACH), super_admin):
        response = client.post(f"/seasons/{season['id']}/teams", json=new_team(race), headers=auth(outsider))
        assert response.status_code == 404


def test_pending_member_cannot_create_team(client, auth, commissioner, make_user, make_league, make_season, race):
    league = make_league(commissioner, join_policy="approval")
    season = make_season(commissioner, league)
    pending = make_user(AccountType.COACH)
    client.post(f"/leagues/{league['id']}/join", headers=auth(pending))
    response = client.post(f"/seasons/{season['id']}/teams", json=new_team(race), headers=auth(pending))
    assert response.status_code == 404


def test_commissioner_creates_team_for_member(client, auth, commissioner, coach, race, setup):
    league, season = setup
    response = client.post(
        f"/seasons/{season['id']}/teams", json=new_team(race, coach_id=coach.id), headers=auth(commissioner)
    )
    assert response.status_code == 201
    assert response.json()["coach"]["id"] == coach.id


def test_member_cannot_create_team_for_someone_else(client, auth, commissioner, coach, make_user, add_member, race, setup):
    league, season = setup
    other = make_user(AccountType.COACH)
    add_member(other, league)
    response = client.post(f"/seasons/{season['id']}/teams", json=new_team(race, coach_id=other.id), headers=auth(coach))
    assert response.status_code == 403


def test_commissioner_cannot_create_team_for_non_member(client, auth, commissioner, make_user, race, setup):
    league, season = setup
    stranger = make_user(AccountType.COACH)
    response = client.post(
        f"/seasons/{season['id']}/teams", json=new_team(race, coach_id=stranger.id), headers=auth(commissioner)
    )
    assert response.status_code == 422


def test_unknown_race_rejected(client, auth, coach, setup):
    league, season = setup
    response = client.post(f"/seasons/{season['id']}/teams", json={"race_id": 999999, "name": "X"}, headers=auth(coach))
    assert response.status_code == 422


def test_members_can_list_and_read_teams(client, auth, commissioner, coach, race, setup):
    league, season = setup
    team = client.post(f"/seasons/{season['id']}/teams", json=new_team(race), headers=auth(coach)).json()
    listed = client.get(f"/seasons/{season['id']}/teams", headers=auth(commissioner)).json()
    assert [item["id"] for item in listed] == [team["id"]]
    shown = client.get(f"/teams/{team['id']}", headers=auth(commissioner)).json()
    assert "email" not in shown["coach"]


def test_outsider_cannot_see_teams(client, auth, coach, make_user, race, setup):
    league, season = setup
    team = client.post(f"/seasons/{season['id']}/teams", json=new_team(race), headers=auth(coach)).json()
    outsider = make_user(AccountType.COACH)
    assert client.get(f"/seasons/{season['id']}/teams", headers=auth(outsider)).status_code == 404
    hidden = client.get(f"/teams/{team['id']}", headers=auth(outsider))
    missing = client.get("/teams/999999", headers=auth(outsider))
    assert hidden.status_code == 404
    assert hidden.json() == missing.json()
