import pytest

from app.models.users import AccountType


@pytest.fixture
def league_with_members(commissioner, make_user, make_league, add_member):
    league = make_league(commissioner)
    members = [make_user(AccountType.COACH) for _ in range(3)]
    for member in members:
        add_member(member, league)
    return league


def member_ids(client, auth, user, league, **params):
    response = client.get(f"/leagues/{league['id']}/members", params=params, headers=auth(user))
    assert response.status_code == 200, response.text
    return [item["user"]["id"] for item in response.json()]


def test_limit_and_offset_walk_through_a_list(client, auth, commissioner, league_with_members):
    everyone = member_ids(client, auth, commissioner, league_with_members)
    assert len(everyone) == 4
    first_page = member_ids(client, auth, commissioner, league_with_members, limit=2)
    second_page = member_ids(client, auth, commissioner, league_with_members, limit=2, offset=2)
    assert first_page + second_page == everyone


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
def test_page_size_is_bounded(client, auth, commissioner, league_with_members, params):
    response = client.get(f"/leagues/{league_with_members['id']}/members", params=params, headers=auth(commissioner))
    assert response.status_code == 422


@pytest.mark.parametrize("path", ["/leagues", "/leagues/{id}/seasons", "/leagues/{id}/join-requests"])
def test_other_league_lists_accept_a_limit(client, auth, commissioner, league_with_members, path):
    url = path.format(id=league_with_members["id"])
    assert client.get(url, params={"limit": 101}, headers=auth(commissioner)).status_code == 422
    assert client.get(url, params={"limit": 1}, headers=auth(commissioner)).status_code == 200


def test_team_list_accepts_a_limit(client, auth, commissioner, coach, race, make_league, make_season, add_member, make_team):
    league = make_league(commissioner)
    season = make_season(commissioner, league)
    add_member(coach, league)
    make_team(coach, season, race)
    make_team(commissioner, season, race)
    response = client.get(f"/seasons/{season['id']}/teams", params={"limit": 1}, headers=auth(coach))
    assert len(response.json()) == 1
