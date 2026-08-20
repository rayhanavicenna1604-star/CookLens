from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Feedback

router = APIRouter(prefix="/api", tags=["feedback"])


@router.post("/feedback")
def submit_feedback(payload: dict, db: Session = Depends(get_db)):
    feedback = Feedback(recipe_id=int(payload.get("recipe_id", 0)), rating=str(payload.get("rating", "okay")), note=str(payload.get("note", ""))[:500])
    db.add(feedback)
    db.commit()
    return {"message": "Thanks for helping us improve."}
