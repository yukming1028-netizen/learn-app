"""Offline sync routes: batch upload cached answer records.

Child device stores answers locally when offline, uploads when back online.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.child import Child
from app.models.question import Question
from app.models.answer_record import AnswerRecord
from app.models.offline_sync import OfflineSyncLog
from app.services.adaptive_engine import update_ability
from app.services.review_engine import update_review_schedule, quality_from_answer, remove_review_if_mastered
from app.services.gamification_service import process_answer as process_gamification
from app.routers.deps import get_child_from_device_token

router = APIRouter(prefix="/api/sync", tags=["offline-sync"])


class OfflineAnswerItem(BaseModel):
    question_id: int
    selected_answer: str
    is_correct: bool | None = None
    time_taken_sec: float = 0.0
    answered_at: str | None = None  # ISO timestamp from device


class SyncBatchRequest(BaseModel):
    device_uuid: str | None = None
    answers: list[OfflineAnswerItem]


class SyncBatchResponse(BaseModel):
    batch_id: str
    total: int
    accepted: int
    rejected: int
    gamification_rewards: dict | None = None


@router.post("/answers", response_model=SyncBatchResponse)
def sync_answers(
    req: SyncBatchRequest,
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Batch upload offline answer records.

    - Deduplicates by (child_id, question_id, answered_at) if timestamp provided
    - Updates child stats, ability, review schedule, gamification
    - Returns gamification rewards from the last processed answer
    """
    batch_id = str(uuid.uuid4())
    accepted = 0
    rejected = 0
    details = []

    for item in req.answers:
        # Validate question exists
        question = db.query(Question).filter(Question.id == item.question_id).first()
        if not question:
            rejected += 1
            details.append({"question_id": item.question_id, "status": "question_not_found"})
            continue

        # Determine correctness
        if item.is_correct is None:
            if question.type == "fill_blank":
                correct_parts = [a.strip() for a in question.answer.split("|")]
                user_parts = [a.strip() for a in item.selected_answer.split("|")]
                while len(user_parts) < len(correct_parts):
                    user_parts.append("")
                is_correct = all(u.lower() == c.lower() for u, c in zip(user_parts, correct_parts))
            else:
                is_correct = item.selected_answer.strip().lower() == question.answer.strip().lower()
        else:
            is_correct = item.is_correct

        # Parse timestamp
        answered_at = datetime.utcnow()
        if item.answered_at:
            try:
                answered_at = datetime.fromisoformat(item.answered_at.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        # Dedup check: same child + question + timestamp (within 1 second)
        existing = db.query(AnswerRecord).filter(
            AnswerRecord.child_id == child.id,
            AnswerRecord.question_id == item.question_id,
            AnswerRecord.answered_at == answered_at,
        ).first()
        if existing:
            rejected += 1
            details.append({"question_id": item.question_id, "status": "duplicate"})
            continue

        # Create record
        record = AnswerRecord(
            child_id=child.id,
            question_id=item.question_id,
            subject=question.subject,
            is_correct=is_correct,
            selected_answer=item.selected_answer,
            time_taken_sec=item.time_taken_sec,
            answered_at=answered_at,
        )
        db.add(record)

        # Update child stats
        child.total_questions += 1
        if is_correct:
            child.total_correct += 1
        child.total_study_minutes = max(0, int(child.total_study_minutes + item.time_taken_sec / 60))

        # Update ability + review
        update_ability(db, child.id, question.subject, is_correct, item.time_taken_sec, question.avg_time_sec)
        time_ratio = item.time_taken_sec / max(question.avg_time_sec, 1.0)
        quality = quality_from_answer(is_correct, time_ratio)
        update_review_schedule(db, child.id, item.question_id, quality)
        if is_correct:
            remove_review_if_mastered(db, child.id, item.question_id)

        accepted += 1
        details.append({"question_id": item.question_id, "status": "accepted", "correct": is_correct})

    # Process gamification for the last answer
    game_rewards = None
    if accepted > 0:
        last_item = req.answers[-1]
        last_question = db.query(Question).filter(Question.id == last_item.question_id).first()
        if last_question:
            if last_item.is_correct is None:
                last_correct = last_item.selected_answer.strip().lower() == last_question.answer.strip().lower()
            else:
                last_correct = last_item.is_correct
            game_rewards = process_gamification(db, child.id, last_correct)

    # Log the sync
    log = OfflineSyncLog(
        child_id=child.id,
        device_uuid=req.device_uuid,
        batch_id=batch_id,
        records_count=len(req.answers),
        accepted_count=accepted,
        rejected_count=rejected,
        status="completed" if rejected == 0 else "partial",
        details=details,
    )
    db.add(log)
    db.commit()

    return SyncBatchResponse(
        batch_id=batch_id,
        total=len(req.answers),
        accepted=accepted,
        rejected=rejected,
        gamification_rewards=game_rewards,
    )


@router.get("/status")
def sync_status(
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Get sync history for the child's device."""
    logs = db.query(OfflineSyncLog).filter(
        OfflineSyncLog.child_id == child.id,
    ).order_by(OfflineSyncLog.synced_at.desc()).limit(20).all()
    return [
        {
            "batch_id": l.batch_id,
            "synced_at": l.synced_at.isoformat() if l.synced_at else None,
            "total": l.records_count,
            "accepted": l.accepted_count,
            "rejected": l.rejected_count,
            "status": l.status,
        }
        for l in logs
    ]
