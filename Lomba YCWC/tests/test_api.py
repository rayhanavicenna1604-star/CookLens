from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def test_analyze_image_does_not_invent_ingredients_without_a_model():
    image = Image.new("RGB", (20, 20), "white")
    response = client.post("/api/analyze", files={"file": ("food.png", BytesIO(_png(image)), "image/png")})
    assert response.status_code == 200
    payload = response.json()
    assert payload["ingredients"] == []
    assert "image recognition is not connected" in payload["message"].lower()
    assert "food safety" in payload["safety_note"].lower()


def test_analyze_rejects_non_image_type():
    response = client.post("/api/analyze", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert response.status_code == 415


def test_main_alias_renders_homepage():
    response = client.get("/main")
    assert response.status_code == 200
    assert "CookLens" in response.text


def _png(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
