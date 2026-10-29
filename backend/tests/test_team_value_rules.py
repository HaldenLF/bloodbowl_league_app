from app.models.player_advancements import AdvancementTier, PlayerAdvancement, StatType
from app.models.players import Player
from app.models.positions import Position
from app.models.races import Race
from app.models.seasons import LeagueFormat
from app.models.teams import Team
from app.rules.team_value import player_value, team_value

HUMANS = Race(name="Human", reroll_cost=50_000, reroll_cost_7s=100_000, special_rule_text="Apothecary (Yes)")
SNOTLINGS = Race(name="Snotling", reroll_cost=60_000, special_rule_text="Bribery & Corruption\nLow Cost Linemen\nSwarming")


def make_player(cost, name="Blitzer", advancements=(), **flags):
    return Player(position=Position(name=name, cost=cost), advancements=list(advancements), **flags)


def skill(tier):
    return PlayerAdvancement(skill_id=1, tier=tier)


def stat(stat_type):
    return PlayerAdvancement(stat_increase=stat_type)


def test_player_value_is_hiring_fee_plus_advancements():
    player = make_player(85_000, advancements=[skill(AdvancementTier.PRIMARY), stat(StatType.ST)])
    assert player_value(player, HUMANS) == 85_000 + 20_000 + 60_000


def test_advancement_values_follow_the_league_table():
    values = {
        AdvancementTier.PRIMARY: 20_000, AdvancementTier.SECONDARY: 40_000,
        AdvancementTier.PRIMARY_ELITE: 30_000, AdvancementTier.SECONDARY_ELITE: 50_000,
    }
    for tier, value in values.items():
        assert player_value(make_player(0, advancements=[skill(tier)]), HUMANS) == value
    stats = {StatType.AV: 10_000, StatType.MA: 20_000, StatType.PA: 20_000, StatType.AG: 30_000, StatType.ST: 60_000}
    for stat_type, value in stats.items():
        assert player_value(make_player(0, advancements=[stat(stat_type)]), HUMANS) == value


def test_low_cost_linemen_count_zero_but_keep_advancements():
    lineman = make_player(15_000, name="Snotling Lineman", advancements=[skill(AdvancementTier.PRIMARY)])
    assert player_value(lineman, SNOTLINGS) == 20_000


def test_low_cost_rule_only_covers_linemen():
    assert player_value(make_player(115_000, name="Trained Troll"), SNOTLINGS) == 115_000


def test_linemen_of_other_races_cost_full_price():
    assert player_value(make_player(50_000, name="Human Lineman"), HUMANS) == 50_000


def test_team_value_breakdown():
    team = Team(race=HUMANS, re_rolls=2, assistant_coaches=1, cheerleaders=2, apothecary=1)
    players = [make_player(50_000), make_player(85_000)]
    value = team_value(team, players, LeagueFormat.SIXTEENS)
    assert (value.players, value.re_rolls, value.staff) == (135_000, 100_000, 80_000)
    assert value.total == 315_000


def test_unavailable_players_are_not_counted():
    team = Team(race=HUMANS, re_rolls=0, assistant_coaches=0, cheerleaders=0, apothecary=0)
    players = [
        make_player(50_000),
        make_player(50_000, dead=True),
        make_player(50_000, fired=True),
        make_player(50_000, missing_next_game=True),
    ]
    assert team_value(team, players, LeagueFormat.SIXTEENS).players == 50_000


def test_sevens_rerolls_use_the_sevens_price():
    team = Team(race=HUMANS, re_rolls=1, assistant_coaches=0, cheerleaders=0, apothecary=0)
    assert team_value(team, [], LeagueFormat.SEVENS).re_rolls == 100_000
