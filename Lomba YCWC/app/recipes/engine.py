from dataclasses import dataclass

from app.ai.normalizer import normalize_many, normalize_ingredient
from app.database.models import Recipe
from app.schemas.ingredients import PreferenceSet

ESTIMATED_PRICES_IDR = {
    "soy sauce": 3_000,
    "oil": 3_000,
    "bread": 6_000,
    "noodles": 4_000,
    "chickpea": 7_000,
    "lemon": 2_500,
    "coconut milk": 6_000,
    "onion": 3_000,
    "potato": 5_000,
    "tomato": 4_000,
    "tofu": 6_000,
    "pasta": 8_000,
    "corn": 5_000,
    "tuna": 12_000,
    "banana": 4_000,
    "oats": 5_000,
    "spinach": 4_000,
    "avocado": 8_000,
    "kidney bean": 7_000,
    "cereal": 5_000,
    "milk": 4_000,
    "yogurt": 6_000,
    "peanut butter": 5_000,
    "cheese": 6_000,
    "cucumber": 3_000,
    "lettuce": 4_000,
    "honey": 3_000,
    "chia seeds": 4_000,
    "apple": 6_000,
    "spring roll wrapper": 5_000,
}


@dataclass
class ScoredRecipe:
    recipe: Recipe
    available: list[str]
    missing: list[str]
    compatibility: int
    waste_score: int
    preference_score: int
    substitution: str | None
    estimated_additional_cost: int


class RecipeEngine:
    def score(self, recipe: Recipe, ingredient_names: list[str], preferences: PreferenceSet) -> ScoredRecipe:
        available_set = normalize_many(ingredient_names)
        required = [normalize_ingredient(item) for item in recipe.ingredients]
        available = [item for item in recipe.ingredients if normalize_ingredient(item) in available_set]
        missing = [item for item in recipe.ingredients if normalize_ingredient(item) not in available_set]
        match = len(available) / max(len(required), 1)
        compatibility = round(match * 100)
        waste_score = round(match * 85 + min(len(available_set), 5) * 3)
        preference_score = self._preference_score(recipe, preferences)
        return ScoredRecipe(recipe, available, missing, compatibility, min(waste_score, 100), preference_score, self._substitution(missing), self._additional_cost(missing))

    def recommend(self, recipes: list[Recipe], ingredient_names: list[str], preferences: PreferenceSet) -> list[ScoredRecipe]:
        scored = [self.score(recipe, ingredient_names, preferences) for recipe in recipes]
        scored = [item for item in scored if not preferences.max_time or item.recipe.cooking_time <= preferences.max_time]
        return sorted(scored, key=lambda item: (item.compatibility * 0.4 + item.waste_score * 0.25 + item.preference_score * 0.2 + self._ease(item.recipe) * 0.1 + self._time(item.recipe) * 0.05), reverse=True)

    @staticmethod
    def _preference_score(recipe: Recipe, preferences: PreferenceSet) -> int:
        selected = [preferences.diet, preferences.taste, preferences.difficulty, preferences.meal]
        return round(sum(1 for value in selected if value and value.lower() in [tag.lower() for tag in recipe.tags]) / max(sum(bool(value) for value in selected), 1) * 100)

    @staticmethod
    def _substitution(missing: list[str]) -> str | None:
        if "soy sauce" in [normalize_ingredient(item) for item in missing]:
            return "Salt plus a small amount of sugar can replace soy sauce."
        return None

    @staticmethod
    def _additional_cost(missing: list[str]) -> int:
        return sum(ESTIMATED_PRICES_IDR.get(normalize_ingredient(item), 4_000) for item in missing)

    @staticmethod
    def _ease(recipe: Recipe) -> int:
        return {"Easy": 100, "Medium": 70, "Hard": 40}.get(recipe.difficulty, 50)

    @staticmethod
    def _time(recipe: Recipe) -> int:
        return max(0, 100 - recipe.cooking_time)
