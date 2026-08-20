from pydantic import BaseModel

from app.schemas.ingredients import Ingredient, PreferenceSet


class RecipeResult(BaseModel):
    id: int
    name: str
    description: str
    cooking_time: int
    difficulty: str
    servings: int
    tags: list[str]
    ingredients: list[str]
    instructions: list[str]
    available_ingredients: list[str]
    missing_ingredients: list[str]
    compatibility: int
    food_waste_score: int
    estimated_additional_cost: int
    image_url: str
    source_url: str | None = None
    substitution: str | None = None


class RecommendationRequest(BaseModel):
    ingredients: list[Ingredient]
    preferences: PreferenceSet = PreferenceSet()
    online: bool = False


class RecommendationResponse(BaseModel):
    recipes: list[RecipeResult]
    priority_ingredient: str | None = None


class CatalogRecipe(BaseModel):
    id: int
    name: str
    category: str = "Online"
    image_url: str
