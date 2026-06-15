"""Review routes: spaced repetition error review (V2)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.child import Child
from app.models.question import Question
from app.schemas.question import QuestionBrief
from app.services.review_engine import get_due_reviews
from app.routers.deps import get_child_or_parent

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("/{child_id}", response_model=list[QuestionBrief])
def get_review_list(
    child_id: int,
    auth = Depends(get_child_or_parent),
    db: Session = Depends(get_db),
):
    """Get all due review questions for a child."""
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == auth["parent_id"],
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="找不到子女")

    reviews = get_due_reviews(db, child_id)
    question_ids = [r.question_id for r in reviews]
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    return questions


@router.get("/{child_id}/count")
def get_review_count(
    child_id: int,
    auth = Depends(get_child_or_parent),
    db: Session = Depends(get_db),
):
    """Get count of due reviews."""
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == auth["parent_id"],
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="找不到子女")

    reviews = get_due_reviews(db, child_id)
    return {"child_id": child_id, "due_count": len(reviews)}
