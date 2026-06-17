"""Insights routes — aggregated learning analytics.

Parent can view platform-wide insights (heat map, wrong-rate by topic).
"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.insights import AggregatedInsights
from app.models.answer_record import AnswerRecord
from app.models.question import Question
from app.routers.deps import get_current_parent
from app.services.insights_service import aggregate_daily

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.post("/refresh")
def refresh_insights(
    days: int = Query(7, le=30),
    parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """Manually trigger insights aggregation for last N days."""
    total = 0
    for i in range(days):
        d = date.today() - timedelta(days=i)
        total += aggregate_daily(db, d)
    return {"message": f"已更新 {total} 個維度的數據"}


@router.get("/heatmap")
def heatmap(
    subject: str | None = Query(None),
    grade: int | None = Query(None),
    days: int = Query(7, le=30),
    parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """Get learning heatmap data: wrong_rate by topic."""
    since = date.today() - timedelta(days=days)

    q = db.query(
        AggregatedInsights.subject,
        AggregatedInsights.grade,
        AggregatedInsights.topic,
        func.sum(AggregatedInsights.total_attempts).label("attempts"),
        func.sum(AggregatedInsights.correct_count).label("correct"),
        func.avg(AggregatedInsights.wrong_rate).label("avg_wrong"),
    ).filter(AggregatedInsights.date >= since).group_by(
        AggregatedInsights.subject, AggregatedInsights.grade, AggregatedInsights.topic
    )

    if subject:
        q = q.filter(AggregatedInsights.subject == subject)
    if grade is not None:
        q = q.filter(AggregatedInsights.grade == grade)

    rows = q.all()
    return [
        {
            "subject": r.subject,
            "grade": r.grade,
            "topic": r.topic,
            "total_attempts": int(r.attempts or 0),
            "correct": int(r.correct or 0),
            "wrong_rate": round(float(r.avg_wrong or 0), 4),
        }
        for r in rows
    ]


@router.get("/overview")
def overview(
    parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """Platform-wide overview stats."""
    total_q = db.query(Question).filter(Question.status == "approved").count()
    total_records = db.query(AnswerRecord).count()

    # By subject
    by_subject = (
        db.query(
            AnswerRecord.subject,
            func.count().label("total"),
            func.sum(AnswerRecord.is_correct.cast(__import__('sqlalchemy').Integer)).label("correct"),
        )
        .group_by(AnswerRecord.subject)
        .all()
    )

    subjects = []
    for r in by_subject:
        total = int(r.total or 0)
        correct = int(r.correct or 0)
        subjects.append({
            "subject": r.subject,
            "total": total,
            "correct": correct,
            "accuracy": round(correct / total * 100, 1) if total > 0 else 0,
        })

    return {
        "total_questions": total_q,
        "total_answers": total_records,
        "by_subject": subjects,
    }
