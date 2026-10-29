import pytest

from app.models.game_results import GameResult
from app.models.games import Game
from app.models.races import Race
from app.models.users import AccountType


@pytest.fixture
def shop(client, auth, commissioner, coach, make_league, make_season, add_member, make_team, make_race):
    league = make_league(commissioner)
    season = make_season(commissioner, league, starting_treasury=200_000)
    add_member(coach, league)
    race = make_race()
    team = make_team(coach, season, race)
    opponent = make_team(commissioner, season, race)

    def buy(item, quantity=1, user=coach):
        return client.post(
            f"/teams/{team['id']}/purchases", json={"item": item, "quantity": quantity}, headers=auth(user)
        )

    return league, season, team, opponent, race, buy


def play_game(db, season, home, away, with_result=True):
    game = Game(season_id=season["id"], round_number=1, home_team_id=home["id"], away_team_id=away["id"])
    db.add(game)
    db.flush()
    if with_result:
        db.add(GameResult(game_id=game.id))
        db.flush()


def test_buying_staff_takes_gold_and_adds_staff(shop):
    league, season, team, opponent, race, buy = shop
    response = buy("cheerleader", 2)
    assert response.status_code == 200
    assert response.json()["cheerleaders"] == 2
    assert response.json()["treasury"] == 180_000


def test_reroll_uses_race_price_and_doubles_after_first_game(db, shop):
    league, season, team, opponent, race, buy = shop
    assert buy("re_roll").json()["treasury"] == 200_000 - race.reroll_cost
    play_game(db, season, team, opponent)
    assert buy("re_roll").json()["treasury"] == 200_000 - 3 * race.reroll_cost


def test_dedicated_fans_at_most_two_extra(shop):
    league, season, team, opponent, race, buy = shop
    assert buy("dedicated_fan", 2).json()["dedicated_fans"] == 3
    assert buy("dedicated_fan").status_code == 409


def test_no_dedicated_fans_after_first_game(db, shop):
    league, season, team, opponent, race, buy = shop
    play_game(db, season, opponent, team)
    assert buy("dedicated_fan").status_code == 409


def test_scheduled_game_without_result_does_not_count_as_played(db, shop):
    league, season, team, opponent, race, buy = shop
    play_game(db, season, team, opponent, with_result=False)
    assert buy("dedicated_fan").status_code == 200


def test_maximums_are_enforced(shop):
    league, season, team, opponent, race, buy = shop
    assert buy("assistant_coach", 6).status_code == 200
    assert buy("assistant_coach").status_code == 409
    assert buy("apothecary").status_code == 200
    assert buy("apothecary").status_code == 409


def test_apothecary_only_for_races_that_allow_it(client, auth, db, coach, commissioner, make_league, make_season, add_member, make_team):
    league = make_league(commissioner)
    season = make_season(commissioner, league, starting_treasury=200_000)
    add_member(coach, league)
    race = Race(name="No Apothecary Race", reroll_cost=70_000, apothecary_allowed=False)
    db.add(race)
    db.flush()
    team = make_team(coach, season, race)
    response = client.post(f"/teams/{team['id']}/purchases", json={"item": "apothecary"}, headers=auth(coach))
    assert response.status_code == 409


def test_not_enough_gold_changes_nothing(client, auth, coach, shop):
    league, season, team, opponent, race, buy = shop
    buy("cheerleader", 6)
    buy("assistant_coach", 6)
    assert buy("re_roll", 3).status_code == 409
    after = client.get(f"/teams/{team['id']}", headers=auth(coach)).json()
    assert after["re_rolls"] == 0 and after["treasury"] == 80_000


def test_only_team_editors_can_buy(commissioner, make_user, add_member, super_admin, shop):
    league, season, team, opponent, race, buy = shop
    assert buy("cheerleader", user=commissioner).status_code == 200
    rival = make_user(AccountType.COACH)
    add_member(rival, league)
    assert buy("cheerleader", user=rival).status_code == 403
    for outsider in (make_user(AccountType.COACH), super_admin):
        assert buy("cheerleader", user=outsider).status_code == 404


@pytest.mark.parametrize("body", [{"item": "free_gold"}, {"item": "cheerleader", "quantity": 0}])
def test_bad_purchase_requests_are_rejected(client, auth, coach, shop, body):
    league, season, team, opponent, race, buy = shop
    assert client.post(f"/teams/{team['id']}/purchases", json=body, headers=auth(coach)).status_code == 422


def test_client_cannot_name_a_price(client, auth, coach, shop):
    league, season, team, opponent, race, buy = shop
    body = {"item": "cheerleader", "price": 1}
    response = client.post(f"/teams/{team['id']}/purchases", json=body, headers=auth(coach))
    assert response.json()["treasury"] == 190_000
