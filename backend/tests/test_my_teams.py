from app.models.users import AccountType


def test_my_teams_lists_only_my_teams_with_summary(client, auth, commissioner, coach, make_user, race, make_league, make_season, add_member, make_team, make_position):
    league = make_league(commissioner)
    season = make_season(commissioner, league)
    add_member(coach, league)
    rival = make_user(AccountType.COACH)
    add_member(rival, league)
    mine = make_team(coach, season, race)
    make_team(rival, season, race)
    position = make_position(race, cost=50_000)
    client.post(f"/teams/{mine['id']}/players", json={"position_id": position.id}, headers=auth(coach))

    response = client.get("/me/teams", headers=auth(coach))
    assert response.status_code == 200
    [team] = response.json()
    assert team["id"] == mine["id"]
    assert team["race"] == {"id": race.id, "name": race.name}
    assert team["season"]["id"] == season["id"]
    assert team["season"]["league"] == {"id": league["id"], "name": league["name"]}
    assert team["team_value"] == 50_000


def test_current_seasons_come_before_finished_ones(client, auth, commissioner, coach, race, make_league, make_season, add_member, make_team):
    league = make_league(commissioner)
    add_member(coach, league)
    finished = client.post(
        f"/leagues/{league['id']}/seasons",
        json={"name": "Old season", "format": "11s", "starting_treasury": 1_000_000, "is_active": False},
        headers=auth(commissioner),
    ).json()
    current = make_season(commissioner, league)
    old_team = make_team(coach, finished, race)
    new_team = make_team(coach, current, race)
    teams = client.get("/me/teams", headers=auth(coach)).json()
    assert [team["id"] for team in teams] == [new_team["id"], old_team["id"]]
    assert [team["season"]["is_active"] for team in teams] == [True, False]


def test_no_teams_gives_an_empty_list(client, auth, coach):
    assert client.get("/me/teams", headers=auth(coach)).json() == []


def test_my_teams_needs_login(client):
    assert client.get("/me/teams").status_code == 401
