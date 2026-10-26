import pytest


@pytest.mark.parametrize("user_fixture", ["coach", "super_admin"])
def test_only_commissioners_create_leagues(client, auth, request, user_fixture):
    user = request.getfixturevalue(user_fixture)
    response = client.post("/leagues", json={"name": "Not Allowed"}, headers=auth(user))
    assert response.status_code == 403


def test_join_code_only_in_create_response(client, auth, commissioner, make_league):
    league = make_league(commissioner)
    assert "join_code" in league
    assert "join_code" not in client.get(f"/leagues/{league['id']}", headers=auth(commissioner)).json()
    assert all("join_code" not in item for item in client.get("/leagues", headers=auth(commissioner)).json())


def test_outsider_gets_same_404_as_missing_league(client, auth, commissioner, coach, super_admin, make_league):
    league = make_league(commissioner)
    missing = client.get("/leagues/999999", headers=auth(coach))
    for outsider in (coach, super_admin):
        hidden = client.get(f"/leagues/{league['id']}", headers=auth(outsider))
        assert hidden.status_code == 404
        assert hidden.json() == missing.json()


def test_member_cannot_see_join_code(client, auth, commissioner, coach, make_league):
    league = make_league(commissioner)
    client.post("/leagues/join", json={"join_code": league["join_code"]}, headers=auth(coach))
    assert client.get(f"/leagues/{league['id']}", headers=auth(coach)).status_code == 200
    assert client.get(f"/leagues/{league['id']}/join-code", headers=auth(coach)).status_code == 403


def test_commissioner_cannot_manage_another_commissioners_league(client, auth, commissioner, make_user, make_league):
    league = make_league(commissioner)
    other = make_user(account_type=commissioner.account_type)
    assert client.get(f"/leagues/{league['id']}/join-code", headers=auth(other)).status_code == 404


def test_search_hides_invite_only_and_ignores_wildcards(client, auth, commissioner, coach, make_league):
    visible = make_league(commissioner, join_policy="open")
    hidden = make_league(commissioner, join_policy="invite_only")
    names = [item["name"] for item in client.get("/leagues/search", params={"q": "league"}, headers=auth(coach)).json()]
    assert visible["name"] in names and hidden["name"] not in names
    assert client.get("/leagues/search", params={"q": "%%"}, headers=auth(coach)).json() == []


def test_approval_flow(client, auth, commissioner, coach, make_league):
    league = make_league(commissioner, join_policy="approval")
    request = client.post(f"/leagues/{league['id']}/join", headers=auth(coach))
    assert request.json()["status"] == "pending"
    assert client.get(f"/leagues/{league['id']}", headers=auth(coach)).status_code == 404

    approve = client.post(f"/leagues/{league['id']}/join-requests/{coach.id}/approve", headers=auth(commissioner))
    assert approve.json()["status"] == "active"
    assert client.get(f"/leagues/{league['id']}", headers=auth(coach)).status_code == 200


def test_coach_cannot_approve_themselves(client, auth, commissioner, coach, make_league):
    league = make_league(commissioner, join_policy="approval")
    client.post(f"/leagues/{league['id']}/join", headers=auth(coach))
    response = client.post(f"/leagues/{league['id']}/join-requests/{coach.id}/approve", headers=auth(coach))
    assert response.status_code == 404


def test_invite_only_league_cannot_be_joined_without_code(client, auth, commissioner, coach, make_league):
    league = make_league(commissioner, join_policy="invite_only")
    assert client.post(f"/leagues/{league['id']}/join", headers=auth(coach)).status_code == 404


def test_regenerated_code_replaces_old_one(client, auth, commissioner, coach, make_league):
    league = make_league(commissioner)
    new_code = client.post(f"/leagues/{league['id']}/join-code/regenerate", headers=auth(commissioner)).json()["join_code"]
    assert client.post("/leagues/join", json={"join_code": league["join_code"]}, headers=auth(coach)).status_code == 404
    joined = client.post("/leagues/join", json={"join_code": new_code}, headers=auth(coach))
    assert joined.json()["status"] == "active"
