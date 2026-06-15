"""Progress routes: today's task progress.
Child auth: device_token + X-Child-Id."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.child import Child
from app.models.answer_record import AnswerRecord
from app.models.plan import LearningPlan
from app.routers.deps import get_child_from_device_token

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/today")
def get_today_progress(
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    today_start = datetime.combine(now.date(), datetime.min.time()).replace(tzinfo=timezone.utc)

    today_records = (
        db.query(AnswerRecord)
        .filter(
            AnswerRecord.child_id == child.id,
            AnswerRecord.answered_at >= today_start,
        )
        .all()
    )

    plan = (
        db.query(LearningPlan)
        .filter(
            LearningPlan.child_id == child.id,
            LearningPlan.is_active == True,
        )
        .first()
    )
    if not plan:
        plan = (
            db.query(LearningPlan)
            .filter(
                LearningPlan.parent_id == child.parent_id,
                LearningPlan.child_id == None,
                LearningPlan.is_active == True,
            )
            .first()
        )

    target_count = plan.daily_task_count if plan else 5
    target_minutes = plan.daily_minutes if plan else 20

    total_today = len(today_records)
    correct_today = sum(1 for r in today_records if r.is_correct)
    minutes_today = round(sum(r.time_taken_sec for r in today_records) / 60, 1)

    return {
        "child_id": child.id,
        "child_name": child.name,
        "target_count": target_count,
        "target_minutes": target_minutes,
        "completed_count": total_today,
        "correct_count": correct_today,
        "accuracy_today": round(correct_today / total_today, 4) if total_today > 0 else 0.0,
        "minutes_today": minutes_today,
        "completion_rate": round(total_today / target_count, 4) if target_count > 0 else 0.0,
        "plan_title": plan.title if plan else None,
    }


@router.get("/me")
def get_my_info(
    child: Child = Depends(get_child_from_device_token),
):
    """Get active child's full profile (stickers, stats)."""
    return {
        "id": child.id,
        "name": child.name,
        "avatar": child.avatar,
        "grade": child.grade,
        "stickers": child.stickers,
        "total_questions": child.total_questions,
        "total_correct": child.total_correct,
    }
