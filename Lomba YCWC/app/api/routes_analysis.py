from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

import os

from dotenv import load_dotenv

from app.ai.detector import MockFoodDetector, OnlineVisionDetector
from app.schemas.analysis import AnalysisResponse

load_dotenv()
router = APIRouter(prefix="/api", tags=["analysis"])
detector = OnlineVisionDetector() if os.getenv("VISION_API_KEY") else MockFoodDetector()
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_food(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Please upload a JPG, PNG, or WEBP image.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image must be smaller than 8 MB.")
    try:
        image = Image.open(BytesIO(content))
        image.verify()
        image = Image.open(BytesIO(content))
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=400, detail="We couldn't read that image. Try another photo.") from exc
    try:
        ingredients = detector.detect(image)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="The online vision service could not analyze this image. Check your API configuration and try again.") from exc
    low_confidence = [item for item in ingredients if item.confidence < 0.7]
    message = f"I found {len(ingredients)} possible ingredients." if ingredients else "Online image recognition is not connected. Add the ingredients from your photo below, or configure a vision API to identify them automatically."
    return AnalysisResponse(message=message, ingredients=ingredients, low_confidence=low_confidence, safety_note="Visual AI cannot guarantee food safety. Check storage time, temperature, packaging, and expiry details before eating.")
