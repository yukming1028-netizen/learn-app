"""AI Question Generation routes.

Admin generates questions via template engine → saved as 'pending'.
Admin then reviews via /api/admin/questions/review.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.question import Question
from app.models.admin import Admin
from app.routers.deps import get_current_admin
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
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Generate questions using template engine (admin only).
    Questions saved as 'pending' for admin review.
    """
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
    for q in created:
        db.refresh(q)
    return {
        "message": f"成功生成 {len(created)} 道題目，待管理員審核",
        "questions": [QuestionOut.model_validate(q).model_dump() for q in created],
    }
