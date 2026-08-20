import json
from urllib.parse import quote
from urllib.request import Request, urlopen

from app.ai.normalizer import normalize_ingredient

THEMEALDB = "https://www.themealdb.com/api/json/v1/1"


def _get_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "CookLens/1.0"})
    with urlopen(request, timeout=4) as response:
        return json.loads(response.read().decode("utf-8"))


def search_online_recipes(ingredients: list[str], limit: int = 3) -> list[dict]:
    if not ingredients:
        return []
    meals = {}
    for ingredient in ingredients[:3]:
        response = _get_json(f"{THEMEALDB}/filter.php?i={quote(normalize_ingredient(ingredient))}")
        for meal in response.get("meals") or []:
            meals[meal["idMeal"]] = meal
    results = []
    available = {normalize_ingredient(item) for item in ingredients}
    for meal in list(meals.values())[:limit]:
        detail = (_get_json(f"{THEMEALDB}/lookup.php?i={meal['idMeal']}").get("meals") or [None])[0]
        if not detail:
            continue
        required = []
        for index in range(1, 21):
            value = detail.get(f"strIngredient{index}")
            if value and value.strip():
                required.append(value.strip())
        matched = [item for item in required if normalize_ingredient(item) in available]
        missing = [item for item in required if normalize_ingredient(item) not in available]
        results.append({
            "id": -int(detail["idMeal"]),
            "name": detail["strMeal"],
            "description": "Online recipe source from TheMealDB.",
            "cooking_time": 30,
            "difficulty": "Medium",
            "servings": 2,
            "tags": [detail.get("strCategory") or "Online"],
            "ingredients": required,
            "instructions": [detail.get("strInstructions") or "Follow the source instructions."],
            "available_ingredients": matched,
            "missing_ingredients": missing,
            "compatibility": round(len(matched) / max(len(required), 1) * 100),
            "food_waste_score": round(len(matched) / max(len(required), 1) * 100),
            "estimated_additional_cost": len(missing) * 4_000,
            "image_url": detail.get("strMealThumb") or "",
            "substitution": None,
            "source_url": detail.get("strSource") or f"https://www.themealdb.com/meal/{detail['idMeal']}",
        })
    return sorted(results, key=lambda item: item["compatibility"], reverse=True)
