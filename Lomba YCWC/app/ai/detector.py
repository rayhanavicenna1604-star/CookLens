from abc import ABC, abstractmethod
import base64
import json
import os
from io import BytesIO
from urllib.request import Request, urlopen

from PIL import Image

from app.schemas.ingredients import Ingredient


class FoodDetector(ABC):
    @abstractmethod
    def detect(self, image: Image.Image) -> list[Ingredient]:
        raise NotImplementedError


class MockFoodDetector(FoodDetector):
    """Safe development detector that never invents ingredients from pixels."""

    def detect(self, image: Image.Image) -> list[Ingredient]:
        return []


class OnlineVisionDetector(FoodDetector):
    """Optional OpenAI-compatible vision detector enabled by VISION_API_KEY."""

    def detect(self, image: Image.Image) -> list[Ingredient]:
        api_key = os.getenv("VISION_API_KEY")
        if not api_key:
            return []
        buffer = BytesIO()
        image.convert("RGB").save(buffer, format="JPEG", quality=82)
        payload = {
            "model": os.getenv("VISION_MODEL", "gpt-4o-mini"),
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": "Identify only food ingredients clearly visible in this image. Do not guess. Return JSON exactly as {\"ingredients\":[{\"name\":\"canonical English name\",\"confidence\":0.0,\"condition\":\"unknown\",\"quantity\":\"unknown\"}]}. Use confidence below 0.7 when uncertain. Never include an ingredient that is not visibly supported."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(buffer.getvalue()).decode()}"}},
            ]}],
        }
        request = Request("https://api.openai.com/v1/chat/completions", data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
        with urlopen(request, timeout=25) as response:
            result = json.loads(response.read().decode())
        content = result["choices"][0]["message"]["content"]
        values = json.loads(content).get("ingredients", [])
        return [Ingredient(name=item["name"], confidence=float(item.get("confidence", 0)), condition=item.get("condition", "unknown"), quantity=item.get("quantity", "unknown"), confirmed=float(item.get("confidence", 0)) >= 0.7) for item in values if item.get("name")]


def confidence_band(confidence: float) -> str:
    if confidence >= 0.9:
        return "high"
    if confidence >= 0.7:
        return "medium"
    return "needs_confirmation"
