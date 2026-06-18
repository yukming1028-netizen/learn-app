"""SQLAlchemy models package."""
from app.models.parent import Parent
from app.models.child import Child
from app.models.device import Device
from app.models.question import Question
from app.models.plan import LearningPlan
from app.models.answer_record import AnswerRecord, ChildAbility
from app.models.review import ReviewSchedule
from app.models.teacher import Teacher
from app.models.classroom import Classroom, ClassroomStudent, Assignment, AssignmentProgress
from app.models.insights import AggregatedInsights
from app.models.admin import Admin
from app.models.gamification import (
    Achievement, ChildAchievement, ChildPet, DailyStreak, PetAccessory,
)
from app.models.offline_sync import OfflineSyncLog
from app.models.forum import ForumPost, ForumReply

__all__ = [
    "Parent", "Child", "Device", "Question", "LearningPlan",
    "AnswerRecord", "ChildAbility", "ReviewSchedule",
    "Teacher", "Classroom", "ClassroomStudent", "Assignment", "AssignmentProgress",
    "AggregatedInsights", "Admin",
    "Achievement", "ChildAchievement", "ChildPet", "DailyStreak", "PetAccessory",
    "OfflineSyncLog", "ForumPost", "ForumReply",
]
