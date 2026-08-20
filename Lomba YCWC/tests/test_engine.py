from types import SimpleNamespace

from app.ai.detector import confidence_band
from app.ai.normalizer import normalize_ingredient
from app.recipes.engine import RecipeEngine
from app.schemas.ingredients import PreferenceSet


def recipe(**overrides):
    values = {"id": 1, "name": "Test", "description": "", "cooking_time": 15, "difficulty": "Easy", "servings": 2, "ingredients": ["rice", "egg", "soy sauce"], "instructions": [], "tags": ["Savory"]}
    values.update(overrides)
    return SimpleNamespace(**values)


def test_normalization_handles_aliases():
    assert normalize_ingredient("tomatoes") == "tomato"
    assert normalize_ingredient("ayam dada") == "chicken"
    assert normalize_ingredient("instant noodle") == "noodles"
    assert normalize_ingredient("noodles") == "noodles"
    assert normalize_ingredient("sereal") == "cereal"


def test_confidence_bands_require_confirmation_below_point_seven():
    assert confidence_band(.95) == "high"
    assert confidence_band(.75) == "medium"
    assert confidence_band(.69) == "needs_confirmation"


def test_recipe_matching_reports_missing_ingredients_and_score():
    result = RecipeEngine().score(recipe(), ["nasi", "egg"], PreferenceSet())
    assert result.available == ["rice", "egg"]
    assert result.missing == ["soy sauce"]
    assert result.compatibility == 67
    assert result.substitution
    assert result.estimated_additional_cost == 3_000


def test_recipe_time_preference_filters_results():
    result = RecipeEngine().recommend([recipe(cooking_time=40), recipe(id=2, cooking_time=10)], ["rice"], PreferenceSet(max_time=15))
    assert len(result) == 1
    assert result[0].recipe.id == 2
