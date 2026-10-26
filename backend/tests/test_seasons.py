from app.models.users import AccountType

SEASON = {"name": "Season One", "format": "16s", "starting_treasury": 1_000_000}


def test_owner_creates_season(client, auth, commissioner, make_league):
    league = make_league(commissioner)
    response = client.post(f"/leagues/{league['id']}/seasons", json=SEASON, headers=auth(commissioner))
    assert response.status_code == 201
    assert response.json()["starting_treasury"] == 1_000_000


def test_member_cannot_create_season(client, auth, commissioner, coach, make_league, add_member):
    league = make_league(commissioner)
    add_member(coach, league)
    response = client.post(f"/leagues/{league['id']}/seasons", json=SEASON, headers=auth(coach))
    assert response.status_code == 403


def test_outsiders_cannot_create_season(client, auth, commissioner, super_admin, make_user, make_league):
    league = make_league(commissioner)
    other_commissioner = make_user(AccountType.COMMISSIONER)
    for outsider in (other_commissioner, super_admin):
        response = client.post(f"/leagues/{league['id']}/seasons", json=SEASON, headers=auth(outsider))
        assert response.status_code == 404


def test_season_name_unique_per_league(client, auth, commissioner, make_league):
    league = make_league(commissioner)
    client.post(f"/leagues/{league['id']}/seasons", json=SEASON, headers=auth(commissioner))
    response = client.post(f"/leagues/{league['id']}/seasons", json=SEASON, headers=auth(commissioner))
    assert response.status_code == 409


def test_negative_starting_treasury_rejected(client, auth, commissioner, make_league):
    league = make_league(commissioner)
    response = client.post(
        f"/leagues/{league['id']}/seasons", json={**SEASON, "starting_treasury": -1}, headers=auth(commissioner)
    )
    assert response.status_code == 422


def test_members_can_list_and_read_seasons(client, auth, commissioner, coach, make_league, make_season, add_member):
    league = make_league(commissioner)
    season = make_season(commissioner, league)
    add_member(coach, league)
    listed = client.get(f"/leagues/{league['id']}/seasons", headers=auth(coach))
    assert [item["id"] for item in listed.json()] == [season["id"]]
    assert client.get(f"/seasons/{season['id']}", headers=auth(coach)).status_code == 200


def test_outsider_cannot_see_seasons(client, auth, commissioner, coach, make_league, make_season):
    league = make_league(commissioner)
    season = make_season(commissioner, league)
    assert client.get(f"/leagues/{league['id']}/seasons", headers=auth(coach)).status_code == 404
    hidden = client.get(f"/seasons/{season['id']}", headers=auth(coach))
    missing = client.get("/seasons/999999", headers=auth(coach))
    assert hidden.status_code == 404
    assert hidden.json() == missing.json()


def test_seasons_require_login(client, commissioner, make_league, make_season):
    league = make_league(commissioner)
    season = make_season(commissioner, league)
    assert client.get(f"/leagues/{league['id']}/seasons").status_code == 401
    assert client.get(f"/seasons/{season['id']}").status_code == 401
