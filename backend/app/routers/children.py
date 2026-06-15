"""Children routes: CRUD + stats + grade management."""
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.parent import Parent
from app.models.child import Child
from app.models.answer_record import AnswerRecord
from app.schemas.child import ChildCreate, ChildOut, ChildUpdate, ChildStats
from app.utils.grade import grade_label, check_grade_update
from app.routers.deps import get_current_parent

router = APIRouter(prefix="/api/children", tags=["children"])


def _get_child_or_404(db, child_id, parent_id):
    child = db.query(Child).filter(Child.id == child_id, Child.parent_id == parent_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="找不到子女")
    return child


@router.get("", response_model=list[ChildOut])
def list_children(parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    children = db.query(Child).filter(Child.parent_id == parent.id).all()
    result = []
    for c in children:
        out = ChildOut.model_validate(c)
        out.accuracy = round(c.total_correct / c.total_questions, 4) if c.total_questions > 0 else 0.0
        result.append(out)
    return result


@router.post("", response_model=ChildOut)
def create_child(payload: ChildCreate, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    """Create a new child profile."""
    count = db.query(Child).filter(Child.parent_id == parent.id).count()
    if count >= 3:
        raise HTTPException(status_code=400, detail="已達最大子女數限制（3名）")
    now = datetime.utcnow()
    child = Child(
        parent_id=parent.id,
        name=payload.name,
        grade=payload.grade,
        avatar=payload.avatar or "🐻",
        grade_set_at=now,
        bound_at=now,
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


@router.get("/{child_id}", response_model=ChildOut)
def get_child(child_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = _get_child_or_404(db, child_id, parent.id)
    out = ChildOut.model_validate(child)
    out.accuracy = round(child.total_correct / child.total_questions, 4) if child.total_questions > 0 else 0.0
    return out


@router.put("/{child_id}", response_model=ChildOut)
def update_child(child_id: int, payload: ChildUpdate, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = _get_child_or_404(db, child_id, parent.id)
    data = payload.model_dump(exclude_unset=True)
    # If grade changed, update grade_set_at and clear dismissal
    if "grade" in data and data["grade"] != child.grade:
        data["grade_set_at"] = datetime.utcnow()
        data["grade_prompt_dismissed_at"] = None
    for field, value in data.items():
        setattr(child, field, value)
    db.commit()
    db.refresh(child)
    return child


@router.delete("/{child_id}")
def delete_child(child_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = _get_child_or_404(db, child_id, parent.id)
    db.delete(child)
    db.commit()
    return {"success": True, "message": "已刪除子女"}


# ─── Grade update prompts ───

@router.get("/{child_id}/grade-check")
def check_child_grade(child_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    """Check if grade update is needed."""
    child = _get_child_or_404(db, child_id, parent.id)
    result = check_grade_update(child.grade, child.grade_set_at, child.grade_prompt_dismissed_at)
    result["child_name"] = child.name
    result["grade_label"] = grade_label(child.grade)
    return result


@router.post("/{child_id}/grade/confirm")
def confirm_grade_update(child_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    """Confirm grade upgrade."""
    child = _get_child_or_404(db, child_id, parent.id)
    result = check_grade_update(child.grade, child.grade_set_at, child.grade_prompt_dismissed_at)
    if not result["needs_prompt"]:
        return {"success": True, "message": "無需更新", "grade": child.grade}
    child.grade = result["suggested_grade"]
    child.grade_set_at = datetime.utcnow()
    child.grade_prompt_dismissed_at = None
    db.commit()
    return {"success": True, "message": f"已升級到{result['suggested_label']}", "grade": child.grade}


@router.post("/{child_id}/grade/dismiss")
def dismiss_grade_update(child_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    """Dismiss grade upgrade prompt until next September."""
    child = _get_child_or_404(db, child_id, parent.id)
    child.grade_prompt_dismissed_at = datetime.utcnow()
    db.commit()
    return {"success": True, "message": "已取消，下次9月1日再提示"}


@router.get("/{child_id}/stats", response_model=ChildStats)
def get_child_stats(child_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = _get_child_or_404(db, child_id, parent.id)
    now = datetime.now(timezone.utc)

    # Subject breakdown
    subject_stats = (
        db.query(
            AnswerRecord.subject,
            func.count(AnswerRecord.id),
            func.sum(AnswerRecord.is_correct),
        )
        .filter(AnswerRecord.child_id == child_id)
        .group_by(AnswerRecord.subject)
        .all()
    )
    subject_breakdown = {}
    for subj, total, correct in subject_stats:
        subject_breakdown[subj] = {
            "total": total,
            "correct": int(correct) if correct else 0,
            "accuracy": round(int(correct) / total, 4) if total else 0.0,
        }

    # Daily trend (last 7 days)
    daily_trend = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        day_start = datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        records = (
            db.query(AnswerRecord)
            .filter(
                AnswerRecord.child_id == child_id,
                AnswerRecord.answered_at >= day_start,
                AnswerRecord.answered_at < day_end,
            )
            .all()
        )
        total = len(records)
        correct = sum(1 for r in records if r.is_correct)
        daily_trend.append({
            "date": day.isoformat(),
            "total": total,
            "correct": correct,
            "accuracy": round(correct / total, 4) if total else 0.0,
            "minutes": round(sum(r.time_taken_sec for r in records) / 60, 1),
        })

    # Weekly trend (last 4 weeks)
    weekly_trend = []
    for i in range(3, -1, -1):
        week_end = now - timedelta(weeks=i)
        week_start = week_end - timedelta(weeks=1)
        records = (
            db.query(AnswerRecord)
            .filter(
                AnswerRecord.child_id == child_id,
                AnswerRecord.answered_at >= week_start,
                AnswerRecord.answered_at < week_end,
            )
            .all()
        )
        total = len(records)
        correct = sum(1 for r in records if r.is_correct)
        weekly_trend.append({
            "week": f"W{i+1}",
            "total": total,
            "correct": correct,
            "accuracy": round(correct / total, 4) if total else 0.0,
        })

    accuracy = round(child.total_correct / child.total_questions, 4) if child.total_questions > 0 else 0.0

    return ChildStats(
        child_id=child_id,
        total_study_minutes=child.total_study_minutes,
        total_questions=child.total_questions,
        total_correct=child.total_correct,
        accuracy=accuracy,
        subject_breakdown=subject_breakdown,
        daily_trend=daily_trend,
        weekly_trend=weekly_trend,
    )
