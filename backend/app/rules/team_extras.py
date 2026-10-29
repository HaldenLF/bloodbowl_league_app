import enum
from dataclasses import dataclass

from app.models.races import Race
from app.models.seasons import LeagueFormat


class TeamExtra(str, enum.Enum):
    RE_ROLL = "re_roll"
    ASSISTANT_COACH = "assistant_coach"
    CHEERLEADER = "cheerleader"
    APOTHECARY = "apothecary"
    DEDICATED_FAN = "dedicated_fan"


@dataclass(frozen=True)
class ExtraRule:
    team_field: str
    maximum: int
    price: int | None = None


RULES = {
    TeamExtra.RE_ROLL: ExtraRule("re_rolls", maximum=8),
    TeamExtra.ASSISTANT_COACH: ExtraRule("assistant_coaches", maximum=6, price=10_000),
    TeamExtra.CHEERLEADER: ExtraRule("cheerleaders", maximum=6, price=10_000),
    TeamExtra.APOTHECARY: ExtraRule("apothecary", maximum=1, price=50_000),
    TeamExtra.DEDICATED_FAN: ExtraRule("dedicated_fans", maximum=3, price=5_000),
}


def unit_price(extra: TeamExtra, race: Race, season_format: LeagueFormat, has_played: bool) -> int | None:
    if extra is not TeamExtra.RE_ROLL:
        return RULES[extra].price
    base = race.reroll_cost_7s if season_format == LeagueFormat.SEVENS else race.reroll_cost
    if base is None:
        return None
    return base * 2 if has_played else base
