"""SM-2 Spaced Repetition Algorithm.

Standard SM-2 implementation for error review scheduling.
Quality scale: 0 (complete fail) to 5 (perfect).
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.review import ReviewSchedule


def quality_from_answer(is_correct: bool, time_ratio: float) -> int:
    """Map answer result to SM-2 quality (0-5)."""
    if not is_correct:
        return 2 if time_ratio < 1.0 else 1
    if time_ratio < 0.5:
        return 5
    elif time_ratio < 0.8:
        return 4
    elif time_ratio < 1.5:
        return 3
    else:
        return 3


def update_review_schedule(db: Session, child_id: int, question_id: int, quality: int) -> ReviewSchedule:
    """Create or update a review schedule entry using SM-2."""
    review = (
        db.query(ReviewSchedule)
        .filter(
            ReviewSchedule.child_id == child_id,
            ReviewSchedule.question_id == question_id,
        )
        .first()
    )

    now = datetime.now(timezone.utc)

    if not review:
        review = ReviewSchedule(
            child_id=child_id,
            question_id=question_id,
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
            next_review_at=now,
        )
        db.add(review)
        db.flush()

    review.last_reviewed_at = now

    if quality >= 3:
        # Correct response
        if review.repetitions == 0:
            review.interval_days = 1
        elif review.repetitions == 1:
            review.interval_days = 3
        else:
            review.interval_days = round(review.interval_days * review.ease_factor)
        review.repetitions += 1
        review.ease_factor = min(2.5, review.ease_factor + 0.1)
    else:
        # Failed response — reset
        review.repetitions = 0
        review.interval_days = 1  # relearn tomorrow... but for kids, 1 hour
        review.ease_factor = max(1.3, review.ease_factor - 0.2)

    # For children, we use shorter intervals initially (hours instead of days for first repeat)
    if review.repetitions == 0 and quality < 3:
        review.next_review_at = now + timedelta(hours=1)
    elif review.repetitions == 1:
        review.next_review_at = now + timedelta(days=1)
    else:
        review.next_review_at = now + timedelta(days=review.interval_days)

    db.flush()
    return review


def get_due_reviews(db: Session, child_id: int) -> list[ReviewSchedule]:
    """Get all review items due now for a child."""
    now = datetime.now(timezone.utc)
    return (
        db.query(ReviewSchedule)
        .filter(
            ReviewSchedule.child_id == child_id,
            ReviewSchedule.next_review_at <= now,
        )
        .order_by(ReviewSchedule.next_review_at)
        .all()
    )


def remove_review_if_mastered(db: Session, child_id: int, question_id: int) -> bool:
    """Remove from review schedule if child got it right 3 times in a row."""
    review = (
        db.query(ReviewSchedule)
        .filter(
            ReviewSchedule.child_id == child_id,
            ReviewSchedule.question_id == question_id,
        )
        .first()
    )
    if review and review.repetitions >= 3:
        db.delete(review)
        db.flush()
        return True
    return False
