from app.schemas.affiliations import AffiliationOut
from app.schemas.base import ORMModel


class MercenaryOut(ORMModel):
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
    upkeep: int
    special_rule: str | None
    affiliations: list[AffiliationOut]