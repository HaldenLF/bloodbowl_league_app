from app.schemas.base import ORMModel
from app.schemas.affiliations import AffiliationOut

class AffiliationOut(ORMModel):
    id: int
    name: str
    

class InducementOut(ORMModel):
    id: int
    name: str
    category: str | None
    max_allowed: int
    description: str | None
    cost: int
    affiliations: list[AffiliationOut]
    