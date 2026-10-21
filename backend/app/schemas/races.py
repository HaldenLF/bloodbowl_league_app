from app.schemas.base import ORMModel
from app.schemas.affiliations import AffiliationOut


class PositionOut(ORMModel):
    id: int
    name: str
    max_allowed: int
    movement: int
    strength: int
    agility: int
    passing: int
    armor: int
    skill_list: str | None
    cost: int
    primary_access: str | None
    secondary_access: str | None


class RaceOut(ORMModel):
    id: int
    name: str
    tier: int | None
    reroll_cost: int | None
    reroll_cost_7s: int | None
    apothecary_allowed: bool
    special_rule_text: str | None


class RaceDetail(RaceOut):
    positions: list[PositionOut]
    affiliations: list[AffiliationOut]