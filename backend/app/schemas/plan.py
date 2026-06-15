"""Plan schemas."""
from datetime import datetime
from pydantic import BaseModel


class PlanCreate(BaseModel):
    child_id: int | None = None
    title: str
    subjects: list[str] = ["math"]
    daily_minutes: int = 20
    daily_task_count: int = 5
    difficulty_range: list[int] = [1, 3]
    weekdays: list[int] = [1, 2, 3, 4, 5]
    time_window_start: str | None = None
    time_window_end: str | None = None


class PlanUpdate(BaseModel):
    title: str | None = None
    subjects: list[str] | None = None
    daily_minutes: int | None = None
    daily_task_count: int | None = None
    difficulty_range: list[int] | None = None
    weekdays: list[int] | None = None
    time_window_start: str | None = None
    time_window_end: str | None = None
    is_active: bool | None = None


class PlanOut(BaseModel):
    id: int
    parent_id: int
    child_id: int | None
    title: str
    subjects: list
    daily_minutes: int
    daily_task_count: int
    difficulty_range: list
    weekdays: list
    time_window_start: str | None
    time_window_end: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
