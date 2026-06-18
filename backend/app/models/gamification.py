"""Gamification models: Achievement (成就), ChildPet (虛擬寵物), Streak (連續答題)."""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Float, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Achievement(Base):
    """Badge/achievement definition (shared across all children)."""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)  # e.g. "first_100", "math_master"
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    icon = Column(String(10), default="🏅")  # emoji
    category = Column(String(30), default="general")  # general, math, chinese, english, streak
    threshold = Column(Integer, default=0)  # e.g. 100 for "答對100題"
    metric = Column(String(30), default="total_correct")  # total_correct, streak, subject_correct, speed
    subject = Column(String(20), nullable=True)  # if metric is subject-specific


class ChildAchievement(Base):
    """Unlocked achievement per child."""
    __tablename__ = "child_achievements"
    __table_args__ = (UniqueConstraint("child_id", "achievement_id", name="uq_child_achievement"),)

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)


class ChildPet(Base):
    """Virtual pet owned by a child."""
    __tablename__ = "child_pets"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    pet_type = Column(String(30), nullable=False)  # cat, dog, rabbit, dragon, unicorn
    pet_name = Column(String(30), default="小夥伴")
    pet_emoji = Column(String(10), default="🐱")
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)  # experience points
    happiness = Column(Integer, default=100)  # 0-100
    hunger = Column(Integer, default=50)  # 0=餓, 100=飽
    is_active = Column(Boolean, default=True)  # currently equipped pet
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow)


class DailyStreak(Base):
    """Daily study streak per child."""
    __tablename__ = "daily_streaks"
    __table_args__ = (UniqueConstraint("child_id", "study_date", name="uq_child_date"),)

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    study_date = Column(Date, nullable=False)
    questions_answered = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)


class PetAccessory(Base):
    """Cosmetic accessory for virtual pet (unlocked via achievements)."""
    __tablename__ = "pet_accessories"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    accessory_code = Column(String(50), nullable=False)  # e.g. "hat_bow", "scarf_red"
    accessory_emoji = Column(String(10), default="🎀")
    is_equipped = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)
