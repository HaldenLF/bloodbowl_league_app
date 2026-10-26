import pytest

from app.models.users import AccountType


@pytest.fixture
def team(commissioner, coach, race, make_league, make_season, add_member, make_team):
    league = make_league(commissioner)
    season = make_season(commissioner, league, starting_treasury=100_000)
    add_member(coach, league)
    return league, make_team(coach, season, race)


def set_treasury(client, headers, team, amount):
    return client.patch(f"/commissioner/teams/{team['id']}/treasury", json={"treasury": amount}, headers=headers)


def test_league_commissioner_sets_treasury(client, auth, commissioner, team):
    league, team = team
    response = set_treasury(client, auth(commissioner), team, 250_000)
    assert response.status_code == 200
    assert response.json()["treasury"] == 250_000


def test_coach_cannot_set_own_treasury(client, auth, coach, team):
    league, team = team
    assert set_treasury(client, auth(coach), team, 9_999_999).status_code == 403


def test_other_member_cannot_set_treasury(client, auth, make_user, add_member, team):
    league, team = team
    member = make_user(AccountType.COACH)
    add_member(member, league)
    assert set_treasury(client, auth(member), team, 0).status_code == 403


def test_outsiders_cannot_set_treasury(client, auth, make_user, super_admin, team):
    league, team = team
    for outsider in (make_user(AccountType.COMMISSIONER), super_admin):
        assert set_treasury(client, auth(outsider), team, 0).status_code == 404


def test_negative_treasury_rejected(client, auth, commissioner, team):
    league, team = team
    assert set_treasury(client, auth(commissioner), team, -1).status_code == 422


def test_old_shared_key_header_grants_nothing(client, team):
    league, team = team
    assert set_treasury(client, {"X-Commissioner-Key": "anything"}, team, 0).status_code == 401
