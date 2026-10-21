from app.schemas.base import ORMModel


class CollegeOut(ORMModel):
    id: int
    name: str
    tier: int | None
    reroll_cost: int | None
    apothecary_allowed: bool
    special_rule_text: str | None


class DungeonBowlPositionOut(ORMModel):
    id: int
    name: str
    role_code: str | None
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