from app.schemas.base import ORMModel

class SkillOut(ORMModel):
    id: int
    name: str
    description: str | None
    category: str
    
