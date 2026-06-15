"""Child schemas."""
from datetime import datetime
from pydantic import BaseModel


class ChildCreate(BaseModel):
    name: str = "小寶貝"
    grade: int = 1
    avatar: str = "🐻"


class ChildUpdate(BaseModel):
    name: str | None = None
    grade: int | None = None
    avatar: str | None = None


class ChildOut(BaseModel):
    id: int
    parent_id: int
    name: str
    grade: int
    avatar: str
    device_uuid: str | None
    bound_at: datetime
    stickers: list
    total_study_minutes: int
    total_questions: int
    total_correct: int
    accuracy: float = 0.0

    class Config:
        from_attributes = True


class ChildStats(BaseModel):
    child_id: int
    total_study_minutes: int
    total_questions: int
    total_correct: int
    accuracy: float
    subject_breakdown: dict
    daily_trend: list
    weekly_trend: list
