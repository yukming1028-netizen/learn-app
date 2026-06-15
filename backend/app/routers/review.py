"""Review routes: spaced repetition error review (V2).
Child auth: device_token + X-Child-Id."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.child import Child
from app.models.question import Question
from app.schemas.question import QuestionBrief
from app.services.review_engine import get_due_reviews
from app.routers.deps import get_child_from_device_token

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("", response_model=list[QuestionBrief])
def get_review_list(
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Get all due review questions for the active child."""
    reviews = get_due_reviews(db, child.id)
    question_ids = [r.question_id for r in reviews]
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    return questions


@router.get("/count")
def get_review_count(
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Get count of due reviews."""
    reviews = get_due_reviews(db, child.id)
    return {"child_id": child.id, "due_count": len(reviews)}
