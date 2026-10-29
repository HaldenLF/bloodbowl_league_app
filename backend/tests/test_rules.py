import pytest

from app.models.races import Race
from app.models.seasons import LeagueFormat
from app.rules.team_extras import TeamExtra, unit_price

RACE = Race(name="Test", reroll_cost=60_000, reroll_cost_7s=100_000)


def test_reroll_price_comes_from_the_race():
    assert unit_price(TeamExtra.RE_ROLL, RACE, LeagueFormat.SIXTEENS, has_played=False) == 60_000


def test_reroll_price_doubles_once_the_team_has_played():
    assert unit_price(TeamExtra.RE_ROLL, RACE, LeagueFormat.SIXTEENS, has_played=True) == 120_000


def test_sevens_uses_the_sevens_reroll_price():
    assert unit_price(TeamExtra.RE_ROLL, RACE, LeagueFormat.SEVENS, has_played=False) == 100_000


@pytest.mark.parametrize("extra, price", [
    (TeamExtra.ASSISTANT_COACH, 10_000),
    (TeamExtra.CHEERLEADER, 10_000),
    (TeamExtra.APOTHECARY, 50_000),
    (TeamExtra.DEDICATED_FAN, 5_000),
])
def test_staff_prices_are_fixed(extra, price):
    assert unit_price(extra, RACE, LeagueFormat.SIXTEENS, has_played=True) == price


def test_missing_reroll_price_gives_no_price():
    race = Race(name="Unpriced", reroll_cost=None)
    assert unit_price(TeamExtra.RE_ROLL, race, LeagueFormat.SIXTEENS, has_played=False) is None
