"""LearningPlan (學習計劃) model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class LearningPlan(Base):
    __tablename__ = "learning_plans"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=True)  # null = all children
    title = Column(String(100), nullable=False)
    subjects = Column(JSON, default=list)  # ["math", "english"]
    daily_minutes = Column(Integer, default=20)
    daily_task_count = Column(Integer, default=5)
    difficulty_range = Column(JSON, default=lambda: [1, 3])
    weekdays = Column(JSON, default=lambda: [1, 2, 3, 4, 5])
    time_window_start = Column(String(5), nullable=True)  # "17:00"
    time_window_end = Column(String(5), nullable=True)    # "18:30"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    child = relationship("Child", backref="plans")
