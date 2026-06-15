"""Adaptive difficulty engine — simplified IRT.

Tracks per-child, per-subject ability (theta). On each answer, adjusts theta
based on correctness and response time, then maps to a difficulty level 1-5.
"""
import math
from sqlalchemy.orm import Session
from app.models.answer_record import ChildAbility


def get_or_create_ability(db: Session, child_id: int, subject: str) -> ChildAbility:
    ability = (
        db.query(ChildAbility)
        .filter(ChildAbility.child_id == child_id, ChildAbility.subject == subject)
        .first()
    )
    if not ability:
        ability = ChildAbility(child_id=child_id, subject=subject, theta=0.0)
        db.add(ability)
        db.flush()
    return ability


def update_ability(db: Session, child_id: int, subject: str, is_correct: bool, time_taken_sec: float, avg_time_sec: float):
    """Update theta based on answer result. Returns new theta."""
    ability = get_or_create_ability(db, child_id, subject)

    if is_correct:
        ratio = time_taken_sec / max(avg_time_sec, 1.0)
        if ratio < 0.7:
            # Fast and correct — big boost
            ability.theta = min(3.0, ability.theta + 0.3)
        elif ratio < 1.5:
            ability.theta = min(3.0, ability.theta + 0.15)
        else:
            # Slow but correct — small boost
            ability.theta = min(3.0, ability.theta + 0.05)
    else:
        # Incorrect — decrease
        ability.theta = max(-3.0, ability.theta - 0.2)

    ability.total_answered += 1
    db.flush()
    return ability.theta


def theta_to_difficulty(theta: float) -> int:
    """Map theta (-3..3) to difficulty (1..5)."""
    d = round(theta + 3)  # -3→0, 0→3, 3→6
    return max(1, min(5, d))


def get_recommended_difficulty(db: Session, child_id: int, subject: str) -> int:
    """Get recommended difficulty for next question."""
    ability = (
        db.query(ChildAbility)
        .filter(ChildAbility.child_id == child_id, ChildAbility.subject == subject)
        .first()
    )
    if not ability:
        return 2  # default medium-easy
    return theta_to_difficulty(ability.theta)
