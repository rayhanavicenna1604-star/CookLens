from pydantic import BaseModel

from app.schemas.ingredients import Ingredient


class AnalysisResponse(BaseModel):
    message: str
    ingredients: list[Ingredient]
    safety_note: str
    low_confidence: list[Ingredient]
