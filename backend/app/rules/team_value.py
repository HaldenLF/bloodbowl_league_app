from dataclasses import dataclass

from app.models.player_advancements import AdvancementTier, PlayerAdvancement, StatType
from app.models.players import Player
from app.models.races import Race
from app.models.seasons import LeagueFormat
from app.models.teams import Team
from app.rules.team_extras import RULES, TeamExtra, unit_price

SKILL_VALUES = {
    AdvancementTier.PRIMARY: 20_000,
    AdvancementTier.SECONDARY: 40_000,
    AdvancementTier.PRIMARY_ELITE: 30_000,
    AdvancementTier.SECONDARY_ELITE: 50_000,
}

STAT_VALUES = {
    StatType.AV: 10_000,
    StatType.MA: 20_000,
    StatType.PA: 20_000,
    StatType.AG: 30_000,
    StatType.ST: 60_000,
}

STAFF = (TeamExtra.ASSISTANT_COACH, TeamExtra.CHEERLEADER, TeamExtra.APOTHECARY)


@dataclass(frozen=True)
class TeamValue:
    players: int
    re_rolls: int
    staff: int

    @property
    def total(self) -> int:
        return self.players + self.re_rolls + self.staff


def advancement_value(advancement: PlayerAdvancement) -> int:
    if advancement.stat_increase is not None:
        return STAT_VALUES[advancement.stat_increase]
    return SKILL_VALUES.get(advancement.tier, 0)


def has_low_cost_linemen(race: Race) -> bool:
    return "low cost linemen" in (race.special_rule_text or "").lower()


def player_value(player: Player, race: Race) -> int:
    lineman = "lineman" in player.position.name.lower()
    hiring_fee = 0 if lineman and has_low_cost_linemen(race) else player.position.cost
    return hiring_fee + sum(advancement_value(advancement) for advancement in player.advancements)


def counts_towards_value(player: Player) -> bool:
    return not (player.dead or player.fired or player.missing_next_game)


def team_value(team: Team, players: list[Player], season_format: LeagueFormat) -> TeamValue:
    reroll_price = unit_price(TeamExtra.RE_ROLL, team.race, season_format, has_played=False) or 0
    staff = sum(getattr(team, RULES[extra].team_field) * RULES[extra].price for extra in STAFF)
    return TeamValue(
        players=sum(player_value(player, team.race) for player in players if counts_towards_value(player)),
        re_rolls=team.re_rolls * reroll_price,
        staff=staff,
    )
