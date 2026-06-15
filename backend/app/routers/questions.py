"""Question routes: list, filter, get next adaptive question, submit answer.
Child auth: device_token + X-Child-Id."""
import random
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.question import Question
from app.models.answer_record import AnswerRecord
from app.models.child import Child
from app.schemas.question import QuestionOut, QuestionBrief, AnswerSubmit, AnswerResult, NextQuestionRequest
from app.services.adaptive_engine import get_recommended_difficulty, update_ability
from app.services.review_engine import update_review_schedule, quality_from_answer, remove_review_if_mastered
from app.routers.deps import get_child_from_device_token

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("", response_model=list[QuestionOut])
def list_questions(
    subject: str | None = Query(None),
    grade: int | None = Query(None),
    difficulty: int | None = Query(None),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Question)
    if subject:
        q = q.filter(Question.subject == subject)
    if grade:
        q = q.filter(Question.grade == grade)
    if difficulty:
        q = q.filter(Question.difficulty == difficulty)
    return q.order_by(Question.id).limit(limit).all()


@router.post("/next", response_model=QuestionBrief | None)
def get_next_question(
    req: NextQuestionRequest,
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Get the next adaptive question for the active child."""
    child_id = child.id
    recommended = get_recommended_difficulty(db, child_id, req.subject or "math")
    subject = req.subject or "math"

    recent_ids = set(
        r.question_id for r in
        db.query(AnswerRecord)
        .filter(AnswerRecord.child_id == child_id)
        .order_by(AnswerRecord.id.desc())
        .limit(20)
        .all()
    )

    candidates = (
        db.query(Question)
        .filter(Question.subject == subject, Question.difficulty == recommended)
        .all()
    )
    candidates = [c for c in candidates if c.id not in recent_ids]

    if not candidates:
        for diff_offset in [-1, 1, -2, 2]:
            candidates = (
                db.query(Question)
                .filter(Question.subject == subject, Question.difficulty == recommended + diff_offset)
                .all()
            )
            candidates = [c for c in candidates if c.id not in recent_ids]
            if candidates:
                break

    if not candidates:
        candidates = db.query(Question).filter(Question.subject == subject).all()
        candidates = [c for c in candidates if c.id not in recent_ids]

    if not candidates:
        candidates = db.query(Question).all()

    if not candidates:
        return None

    question = random.choice(candidates)
    return QuestionBrief.model_validate(question)


@router.post("/answer", response_model=AnswerResult)
def submit_answer(
    payload: AnswerSubmit,
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Submit an answer and get feedback + reward."""
    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="找不到題目")

    if payload.is_correct is None:
        is_correct = payload.selected_answer.strip() == question.answer.strip()
    else:
        is_correct = payload.is_correct

    record = AnswerRecord(
        child_id=child.id,
        question_id=payload.question_id,
        subject=question.subject,
        is_correct=is_correct,
        selected_answer=payload.selected_answer,
        time_taken_sec=payload.time_taken_sec,
    )
    db.add(record)

    new_theta = update_ability(
        db, child.id, question.subject,
        is_correct, payload.time_taken_sec, question.avg_time_sec,
    )

    child.total_questions += 1
    if is_correct:
        child.total_correct += 1
    child.total_study_minutes = max(0, int(child.total_study_minutes + payload.time_taken_sec / 60))

    reward_msg = None
    new_sticker = None
    if is_correct and child.total_correct % 5 == 0:
        stickers_pool = ["🌟", "🎉", "🏅", "🌈", "⭐", "💎", "🔥", "🦄", "🎈"]
        new_sticker = random.choice(stickers_pool)
        if new_sticker not in child.stickers:
            child.stickers = child.stickers + [new_sticker]
        reward_msg = f"太棒了！獲得了 {new_sticker} 貼紙！"

    time_ratio = payload.time_taken_sec / max(question.avg_time_sec, 1.0)
    quality = quality_from_answer(is_correct, time_ratio)
    update_review_schedule(db, child.id, payload.question_id, quality)

    if is_correct:
        remove_review_if_mastered(db, child.id, payload.question_id)

    db.commit()

    feedback = "答對了！好厲害！🎉" if is_correct else "沒關係，再接再厲！💪"

    return AnswerResult(
        is_correct=is_correct,
        correct_answer=question.answer,
        explanation=question.explanation,
        reward=reward_msg or feedback,
        new_sticker=new_sticker,
    )
