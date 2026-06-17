"""Admin routes: login + AI question review.

AI-generated questions are reviewed by admin (not parents).
Admin JWT uses role='admin'.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.admin import Admin
from app.models.question import Question
from app.routers.deps import get_current_admin
from app.services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ─── Admin Auth ───

class AdminLogin(BaseModel):
    username: str
    password: str


class AdminOut(BaseModel):
    id: int
    username: str
    display_name: str
    is_super: bool

    class Config:
        from_attributes = True


@router.post("/login")
def admin_login(req: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == req.username).first()
    if not admin or not verify_password(req.password, admin.password_hash):
        raise HTTPException(401, "用戶名或密碼錯誤")
    token = create_access_token({"sub": admin.id, "role": "admin"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "admin": AdminOut.model_validate(admin).model_dump(),
    }


@router.get("/me")
def admin_me(admin: Admin = Depends(get_current_admin)):
    return AdminOut.model_validate(admin).model_dump()


# ─── AI Question Review ───

class ReviewAction(BaseModel):
    question_ids: list[int]
    action: str  # "approve" or "reject"


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


@router.get("/questions/pending")
def list_pending_questions(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """List all pending AI-generated questions for admin review."""
    qs = db.query(Question).filter(Question.status == "pending").order_by(Question.id.desc()).all()
    return [QuestionOut.model_validate(q).model_dump() for q in qs]


@router.post("/questions/review")
def review_questions(
    req: ReviewAction,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Approve or reject pending questions (admin only)."""
    if req.action not in ("approve", "reject"):
        raise HTTPException(400, "action 必須是 approve 或 reject")

    updated = 0
    for qid in req.question_ids:
        q = db.query(Question).filter(Question.id == qid).first()
        if q and q.status == "pending":
            q.status = "approved" if req.action == "approve" else "rejected"
            updated += 1

    db.commit()
    action_text = "通過" if req.action == "approve" else "拒絕"
    return {"message": f"已{action_text} {updated} 道題目", "updated": updated}


@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Delete any question (admin only)."""
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(404, "找不到題目")
    db.delete(q)
    db.commit()
    return {"message": "題目已刪除"}


@router.get("/questions/all")
def list_all_questions(
    status_filter: str | None = None,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """List all questions with optional status filter."""
    q = db.query(Question)
    if status_filter:
        q = q.filter(Question.status == status_filter)
    return [QuestionOut.model_validate(r).model_dump() for r in q.order_by(Question.id.desc()).all()]
