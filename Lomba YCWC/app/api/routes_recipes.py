from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Recipe
from app.recipes.engine import RecipeEngine
from app.recipes.online import search_online_recipes
from app.recipes.catalog import online_catalog
from app.schemas.ingredients import PreferenceSet
from app.schemas.recipes import RecommendationRequest, RecommendationResponse, RecipeResult

router = APIRouter(prefix="/api/recipes", tags=["recipes"])
engine = RecipeEngine()

IMAGE_URLS = {
    "Chicken Fried Rice": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=1200&q=85",
    "Garden Omelet": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=1200&q=85",
    "Comfort Chicken Soup": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=1200&q=85",
    "Spicy Garlic Rice Bowl": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=1200&q=85",
    "Tomato Egg Toast": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=1200&q=85",
    "Rainbow Vegetable Noodles": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=1200&q=85",
    "Chickpea Garden Salad": "https://images.unsplash.com/photo-1512621776951-a57141f2e3e7?auto=format&fit=crop&w=1200&q=85",
    "Coconut Vegetable Curry": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=1200&q=85",
    "Creamy Potato Hash": "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?auto=format&fit=crop&w=1200&q=85",
    "Tofu Vegetable Stir-Fry": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=1200&q=85",
    "Tuna Corn Rice Bowl": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=1200&q=85",
    "Banana Oat Pancakes": "https://images.unsplash.com/photo-1528207776546-365bb710ee93?auto=format&fit=crop&w=1200&q=85",
    "Garlic Spinach Pasta": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=1200&q=85",
    "Tomato Bean Stew": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=1200&q=85",
    "Instant Noodle Egg Bowl": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=1200&q=85",
    "Crispy Noodle Omelet": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=1200&q=85",
    "Peanut Noodle Salad": "https://images.unsplash.com/photo-1557872943-16a5ac26437e?auto=format&fit=crop&w=1200&q=85",
    "Chicken Noodle Soup": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=1200&q=85",
    "Garlic Butter Noodles": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=1200&q=85",
    "Instant Noodle Cheese Bowl": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=1200&q=85",
    "Cereal Banana Bowl": "https://images.unsplash.com/photo-1517093728432-a0440f8d45af?auto=format&fit=crop&w=1200&q=85",
    "Yogurt Cereal Crunch": "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=1200&q=85",
    "Peanut Banana Cereal": "https://images.unsplash.com/photo-1528825871115-3581a5387919?auto=format&fit=crop&w=1200&q=85",
    "Cold Cereal Overnight Cup": "https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?auto=format&fit=crop&w=1200&q=85",
    "Fruit Yogurt Cup": "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=1200&q=85",
    "Banana Honey Toast": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=1200&q=85",
    "Chia Yogurt Pudding": "https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?auto=format&fit=crop&w=1200&q=85",
    "Cucumber Tuna Cups": "https://images.unsplash.com/photo-1512621776951-a57141f2e3e7?auto=format&fit=crop&w=1200&q=85",
    "Fresh Lettuce Egg Wraps": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1200&q=85",
    "Vegetable Spring Roll Bites": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1200&q=85",
}


def to_result(scored) -> RecipeResult:
    return RecipeResult(id=scored.recipe.id, name=scored.recipe.name, description=scored.recipe.description, cooking_time=scored.recipe.cooking_time, difficulty=scored.recipe.difficulty, servings=scored.recipe.servings, tags=scored.recipe.tags, ingredients=scored.recipe.ingredients, instructions=scored.recipe.instructions, available_ingredients=scored.available, missing_ingredients=scored.missing, compatibility=scored.compatibility, food_waste_score=scored.waste_score, estimated_additional_cost=scored.estimated_additional_cost, image_url=IMAGE_URLS.get(scored.recipe.name, "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1200&q=85"), substitution=scored.substitution)


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest, db: Session = Depends(get_db)):
    confirmed = [item.name for item in request.ingredients if item.confirmed]
    if request.online:
        try:
            online_results = [item for item in search_online_recipes(confirmed) if item["compatibility"] > 0]
            if online_results:
                return RecommendationResponse(recipes=online_results, priority_ingredient=None)
        except Exception:
            pass
    scored = engine.recommend(db.query(Recipe).all(), confirmed, request.preferences)
    if confirmed:
        scored = [item for item in scored if item.compatibility > 0]
    return RecommendationResponse(recipes=[to_result(item) for item in scored[:6]], priority_ingredient=next((item.name for item in request.ingredients if item.name in {"chicken", "spinach", "milk"}), None))


@router.get("/catalog", response_model=list[dict])
def browse_online_catalog(limit: int = 1000):
    limit = max(1, min(limit, 1000))
    try:
        meals = online_catalog(limit)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="The online recipe catalog is temporarily unavailable.") from exc
    return [{"id": -int(meal["idMeal"]), "name": meal["strMeal"], "category": "Online recipe", "image_url": meal.get("strMealThumb", "")} for meal in meals]


@router.get("/{recipe_id}", response_model=RecipeResult)
def recipe_detail(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    scored = engine.score(recipe, [], PreferenceSet())
    return to_result(scored)
