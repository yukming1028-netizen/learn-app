"""Child (子女) model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False, index=True)
    name = Column(String(50), default="小寶貝")
    grade = Column(Integer, default=1)  # 1=小一 ... 9=中三
    avatar = Column(String(20), default="🐻")  # emoji
    device_uuid = Column(String(64), nullable=True, index=True)  # Same device can have multiple children
    bound_at = Column(DateTime, default=datetime.utcnow)
    stickers = Column(JSON, default=list)  # ["🌟", "🐶", ...]
    total_study_minutes = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)

    parent = relationship("Parent", backref="children")
