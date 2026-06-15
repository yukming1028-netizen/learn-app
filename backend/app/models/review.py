"""ReviewSchedule (錯題複習排程) — SM-2 Spaced Repetition model."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class ReviewSchedule(Base):
    __tablename__ = "review_schedules"
    __table_args__ = (UniqueConstraint("child_id", "question_id", name="uq_review_child_question"),)

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    ease_factor = Column(Float, default=2.5)    # 1.3 ~ 2.5
    interval_days = Column(Integer, default=0)
    repetitions = Column(Integer, default=0)
    next_review_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_reviewed_at = Column(DateTime, nullable=True)

    child = relationship("Child", backref="review_schedules")
    question = relationship("Question", backref="review_schedules")
