from app.models.players import Player
from app.rules.spp import star_player_points


def make_player(completions=0, touchdowns=0, interceptions=0, casualties=0, mvps=0):
    return Player(completions=completions, touchdowns=touchdowns, interceptions=interceptions, casualties=casualties, mvps=mvps)


def test_new_player_has_no_spp():
    assert star_player_points(make_player()) == 0


def test_spp_follows_the_sheet_formula():
    player = make_player(completions=1, touchdowns=2, interceptions=1, casualties=3, mvps=1)
    assert star_player_points(player) == 1 + 2 * 3 + 2 + 3 * 2 + 4
