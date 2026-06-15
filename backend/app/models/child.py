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
    grade = Column(Integer, default=0)  # 0=學前預備, 1=小一 ... 6=小六
    grade_set_at = Column(DateTime, default=datetime.utcnow)  # 年級設定日期（用於計算自動升級提示）
    grade_prompt_dismissed_at = Column(DateTime, nullable=True)  # 用戶取消年級升級提示的時間
    avatar = Column(String(20), default="🐻")  # emoji
    bound_at = Column(DateTime, default=datetime.utcnow)
    stickers = Column(JSON, default=list)  # ["🌟", "🐶", ...]
    total_study_minutes = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)

    parent = relationship("Parent", backref="children")
