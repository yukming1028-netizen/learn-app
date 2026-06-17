"""AI Question Generation + Review routes.
Parent can generate questions, review pending ones, approve/reject.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.question import Question
from app.models.parent import Parent
from app.routers.deps import get_current_parent
from app.services.question_generator import generate_questions

router = APIRouter(prefix="/api/ai-questions", tags=["ai-questions"])


class GenerateRequest(BaseModel):
    subject: str = "math"
    grade: int = 1
    topic: str | None = None
    count: int = 5
    difficulty: int | None = None


class QuestionOut(BaseModel):
    id: int
    subject: str
    grade: int
    difficulty: int
    type: str
    content: str
    options: list
    answer: str
    explanation: str
    tags: list
    status: str
    source: str

    class Config:
        from_attributes = True


@router.post("/generate")
def generate(
    req: GenerateRequest,
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """Generate questions using template engine. Questions saved as 'pending'."""
    if req.count < 1 or req.count > 50:
        raise HTTPException(400, "數量需在 1-50 之間")
    if req.grade < 0 or req.grade > 6:
        raise HTTPException(400, "年級需在 0-6 之間")

    generated = generate_questions(
        subject=req.subject,
        grade=req.grade,
        topic=req.topic,
        count=req.count,
        difficulty=req.difficulty,
    )

    created = []
    for gq in generated:
        q = Question(
            subject=gq.subject, grade=gq.grade, difficulty=gq.difficulty,
            type=gq.type, content=gq.content, options=gq.options,
            answer=gq.answer, explanation=gq.explanation, tags=gq.tags,
            avg_time_sec=gq.avg_time_sec,
            status="pending", source="ai_generated",
        )
        db.add(q)
        created.append(q)

    db.commit()
    return {
        "message": f"成功生成 {len(created)} 道題目",
        "questions": [QuestionOut.model_validate(q).model_dump() for q in created],
    }


@router.get("/pending")
def list_pending(
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """List all pending questions for review."""
    qs = db.query(Question).filter(Question.status == "pending").order_by(Question.id.desc()).all()
    return [QuestionOut.model_validate(q).model_dump() for q in qs]


class ReviewAction(BaseModel):
    question_ids: list[int]
    action: str  # "approve" or "reject"


@router.post("/review")
def review_questions(
    req: ReviewAction,
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """Approve or reject pending questions."""
    if req.action not in ("approve", "reject"):
        raise HTTPException(400, "action 必須是 approve 或 reject")

    updated = 0
    for qid in req.question_ids:
        q = db.query(Question).filter(Question.id == qid).first()
        if q and q.status == "pending":
            q.status = "approved" if req.action == "approve" else "rejected"
            updated += 1

    db.commit()
    return {"message": f"已{'通過' if req.action == 'approve' else '拒絕'} {updated} 道題目"}


@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """Delete a question (any status)."""
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(404, "找不到題目")
    db.delete(q)
    db.commit()
    return {"message": "題目已刪除"}
