"""Teacher schemas."""
from pydantic import BaseModel
from datetime import datetime


class TeacherRegister(BaseModel):
    email: str
    password: str  # min 6 chars
    name: str
    school: str = ""


class TeacherLogin(BaseModel):
    email: str
    password: str


class TeacherOut(BaseModel):
    id: int
    email: str
    name: str
    school: str

    class Config:
        from_attributes = True


class ClassroomCreate(BaseModel):
    name: str
    grade: int = 1
    subject: str = "math"


class ClassroomOut(BaseModel):
    id: int
    teacher_id: int
    name: str
    grade: int
    subject: str
    invite_code: str
    student_count: int = 0
    assignment_count: int = 0
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class AssignmentCreate(BaseModel):
    classroom_id: int
    title: str
    description: str = ""
    question_ids: list[int]
    due_date: datetime | None = None


class AssignmentOut(BaseModel):
    id: int
    classroom_id: int
    teacher_id: int
    title: str
    description: str
    question_ids: list
    due_date: datetime | None = None
    is_active: bool = True
    completed_count: int = 0
    total_students: int = 0
    created_at: datetime | None = None

    class Config:
        from_attributes = True
