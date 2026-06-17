"""Insights aggregation service.

Computes daily aggregated statistics from answer_records.
Called after each answer submission or via periodic refresh.
"""
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.answer_record import AnswerRecord
from app.models.question import Question
from app.models.insights import AggregatedInsights


def aggregate_daily(db: Session, target_date: date | None = None):
    """Aggregate all answer records for a given date into insights table."""
    if target_date is None:
        target_date = date.today()

    # Query answer records joined with questions for that date
    rows = (
        db.query(
            AnswerRecord.subject,
            Question.grade,
            func.json_extract(Question.tags, '$').label("tags_json"),
            AnswerRecord.is_correct,
            AnswerRecord.time_taken_sec,
        )
        .join(Question, AnswerRecord.question_id == Question.id)
        .filter(func.date(AnswerRecord.answered_at) == target_date)
        .all()
    )

    # Group by (grade, subject, topic)
    groups = {}
    for subject, grade, tags_json, is_correct, time_taken in rows:
        # Extract first tag as topic
        topic = "general"
        if tags_json:
            try:
                import json
                tags = json.loads(tags_json) if isinstance(tags_json, str) else tags_json
                if tags:
                    topic = tags[0]
            except Exception:
                pass

        key = (grade or 0, subject or "unknown", topic)
        if key not in groups:
            groups[key] = {"attempts": 0, "correct": 0, "total_time": 0.0}
        g = groups[key]
        g["attempts"] += 1
        if is_correct:
            g["correct"] += 1
        g["total_time"] += time_taken or 0

    # Upsert into aggregated_insights
    for (grade, subject, topic), g in groups.items():
        existing = db.query(AggregatedInsights).filter(
            AggregatedInsights.date == target_date,
            AggregatedInsights.grade == grade,
            AggregatedInsights.subject == subject,
            AggregatedInsights.topic == topic,
        ).first()

        wrong_rate = 1.0 - (g["correct"] / g["attempts"]) if g["attempts"] > 0 else 0.0
        avg_time = g["total_time"] / g["attempts"] if g["attempts"] > 0 else 0.0

        if existing:
            existing.total_attempts = g["attempts"]
            existing.correct_count = g["correct"]
            existing.wrong_rate = round(wrong_rate, 4)
            existing.avg_time_sec = round(avg_time, 2)
            existing.updated_at = datetime.utcnow()
        else:
            ins = AggregatedInsights(
                date=target_date, grade=grade, subject=subject, topic=topic,
                total_attempts=g["attempts"], correct_count=g["correct"],
                wrong_rate=round(wrong_rate, 4), avg_time_sec=round(avg_time, 2),
            )
            db.add(ins)

    db.commit()
    return len(groups)
