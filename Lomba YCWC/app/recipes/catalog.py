import json
from functools import lru_cache
from urllib.parse import quote
from urllib.request import Request, urlopen

THEMEALDB = "https://www.themealdb.com/api/json/v1/1"


def _get_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "CookLens/1.0"})
    with urlopen(request, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


@lru_cache(maxsize=1)
def online_catalog(limit: int = 1000) -> list[dict]:
    categories = (_get_json(f"{THEMEALDB}/list.php?c=list").get("meals") or [])
    meals: dict[str, dict] = {}
    for category in categories:
        values = _get_json(f"{THEMEALDB}/filter.php?c={quote(category['strCategory'])}").get("meals") or []
        for meal in values:
            meals.setdefault(meal["idMeal"], meal)
            if len(meals) >= limit:
                return list(meals.values())[:limit]
    return list(meals.values())[:limit]
