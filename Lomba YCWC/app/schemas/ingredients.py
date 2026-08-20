from typing import Literal

from pydantic import BaseModel, Field

Condition = Literal["fresh", "cooked", "frozen", "opened", "wilted", "unknown", "possibly_spoiled", "raw"]


class Ingredient(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    confidence: float = Field(default=1.0, ge=0, le=1)
    condition: Condition = "unknown"
    quantity: str = "unknown"
    confirmed: bool = True


class IngredientRequest(BaseModel):
    ingredients: list[Ingredient]


class PreferenceSet(BaseModel):
    diet: str | None = None
    taste: str | None = None
    max_time: int | None = Field(default=None, ge=1, le=240)
    difficulty: str | None = None
    meal: str | None = None
