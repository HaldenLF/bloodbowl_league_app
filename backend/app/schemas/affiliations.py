from app.schemas.base import ORMModel


class AffiliationOut(ORMModel):
    id: int
    name: str