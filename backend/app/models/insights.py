"""AggregatedInsights — daily aggregated learning data for analytics."""
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, UniqueConstraint
from app.database import Base


class AggregatedInsights(Base):
    """Daily aggregated insights per grade/subject/topic.
    Used for learning heatmap and education analytics.
    """
    __tablename__ = "aggregated_insights"
    __table_args__ = (
        UniqueConstraint("date", "grade", "subject", "topic", name="uq_insights_daily"),
    )

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=date.today, index=True)
    grade = Column(Integer, index=True)  # 0-6
    subject = Column(String(20), index=True)  # math, chinese, english, science
    topic = Column(String(100), default="")  # e.g. "加法", "進位"
    total_attempts = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    wrong_rate = Column(Float, default=0.0)  # 0.0-1.0
    avg_time_sec = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)
