"""Question (題庫) model."""
from sqlalchemy import Column, Integer, String, Text, Float, JSON
from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(20), index=True)  # math, chinese, english, science
    grade = Column(Integer, index=True)  # 0-6
    difficulty = Column(Integer, default=2)  # 1-5
    type = Column(String(20), default="choice")  # choice, input, fill_blank
    content = Column(Text, nullable=False)
    options = Column(JSON, default=list)  # ["A選項", "B選項", ...]
    answer = Column(String(200), nullable=False)
    explanation = Column(Text, default="")
    tags = Column(JSON, default=list)  # ["加法", "進位"]
    avg_time_sec = Column(Float, default=15.0)
    correct_rate = Column(Float, default=0.7)
    status = Column(String(20), default="approved")  # approved, pending, rejected
    source = Column(String(20), default="seed")  # seed, ai_generated, teacher
