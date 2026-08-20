ALIASES = {
    "tomatoes": "tomato", "tomat": "tomato", "fresh tomato": "tomato",
    "ayam": "chicken", "chicken breast": "chicken", "ayam dada": "chicken",
    "telur": "egg", "eggs": "egg", "nasi": "rice", "wortel": "carrot",
    "bawang putih": "garlic", "daun bawang": "green onion", "cabai": "chili",
    "minyak": "oil", "kecap asin": "soy sauce",
    "tahu": "tofu", "mie": "noodles", "noodle": "noodles", "noodles": "noodles", "instant noodle": "noodles", "instant noodles": "noodles", "pasta": "pasta", "jagung": "corn",
    "tuna kaleng": "tuna", "pisang": "banana", "havermut": "oats", "sereal": "cereal", "susu": "milk", "yogurt": "yogurt", "timun": "cucumber", "selada": "lettuce", "madu": "honey", "chia seed": "chia seeds",
    "bayam": "spinach", "alpukat": "avocado", "kacang merah": "kidney bean",
}


def normalize_ingredient(value: str) -> str:
    cleaned = " ".join(value.lower().strip().split())
    return ALIASES.get(cleaned, cleaned.rstrip("s") if cleaned.endswith("s") else cleaned)


def normalize_many(values: list[str]) -> set[str]:
    return {normalize_ingredient(value) for value in values if value.strip()}
