from app.models.positions import Position
from app.rules.roster import is_journeyman, journeymen_allowed, lowest_free_number


def test_lowest_free_number_fills_gaps():
    assert lowest_free_number(set()) == 1
    assert lowest_free_number({1, 2, 4}) == 3


def test_no_free_number_when_all_are_taken():
    assert lowest_free_number(set(range(1, 100))) is None


def test_journeymen_are_recognised_by_name():
    assert is_journeyman(Position(name="Journeyman Human Lineman"))
    assert not is_journeyman(Position(name="Human Lineman"))


def test_journeymen_only_below_eleven_available_players():
    assert journeymen_allowed(10)
    assert not journeymen_allowed(11)
