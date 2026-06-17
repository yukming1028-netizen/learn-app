"""Classroom (班級) + ClassroomStudent (學生關聯) + Assignment (作業) models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # e.g. "三年甲班"
    grade = Column(Integer, default=1)  # 0-6
    subject = Column(String(20), default="math")  # primary subject
    invite_code = Column(String(10), unique=True, index=True)  # 6-char code
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("Teacher", backref="classrooms")
    students = relationship("ClassroomStudent", backref="classroom", cascade="all, delete-orphan")
    assignments = relationship("Assignment", backref="classroom", cascade="all, delete-orphan")


class ClassroomStudent(Base):
    """Links a child to a classroom."""
    __tablename__ = "classroom_students"
    __table_args__ = (
        # unique constraint on (classroom_id, child_id)
    )

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    child = relationship("Child")


class Assignment(Base):
    """Teacher-created assignment with selected questions."""
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    question_ids = Column(JSON, default=list)  # [1, 5, 12, ...]
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    progresses = relationship("AssignmentProgress", backref="assignment", cascade="all, delete-orphan")


class AssignmentProgress(Base):
    """Tracks each child's progress on an assignment."""
    __tablename__ = "assignment_progress"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    completed_question_ids = Column(JSON, default=list)  # [1, 5, ...]
    score = Column(Integer, default=0)  # correct count
    total = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
