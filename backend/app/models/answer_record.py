"""AnswerRecord (答題記錄) + ChildAbility (能力追蹤) models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class AnswerRecord(Base):
    __tablename__ = "answer_records"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    subject = Column(String(20))  # denormalized for fast queries
    is_correct = Column(Boolean, nullable=False)
    selected_answer = Column(String(200), nullable=True)
    time_taken_sec = Column(Float, default=0.0)
    answered_at = Column(DateTime, default=datetime.utcnow, index=True)

    child = relationship("Child", backref="answer_records")
    question = relationship("Question", backref="answer_records")


class ChildAbility(Base):
    """Per-child, per-subject ability score for adaptive engine (simplified IRT)."""
    __tablename__ = "child_abilities"
    __table_args__ = (UniqueConstraint("child_id", "subject", name="uq_child_subject"),)

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    subject = Column(String(20), nullable=False)
    theta = Column(Float, default=0.0)  # ability score, range roughly -3 to 3
    total_answered = Column(Integer, default=0)
