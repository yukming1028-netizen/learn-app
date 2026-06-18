"""Gamification service: achievements, pet EXP, daily streaks.

Called after each answer submission to update game state.
"""
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.gamification import (
    Achievement, ChildAchievement, ChildPet, DailyStreak, PetAccessory,
)
from app.models.child import Child
from app.models.answer_record import AnswerRecord


# ─── Achievement Definitions ───

ACHIEVEMENT_DEFS = [
    # General
    {"code": "first_answer", "name": "初次答題", "description": "完成第一道題目", "icon": "🌱",
     "category": "general", "metric": "total_questions", "threshold": 1},
    {"code": "answer_50", "name": "勤奮學員", "description": "完成 50 道題目", "icon": "📚",
     "category": "general", "metric": "total_questions", "threshold": 50},
    {"code": "answer_100", "name": "百題達人", "description": "完成 100 道題目", "icon": "💯",
     "category": "general", "metric": "total_questions", "threshold": 100},
    {"code": "correct_50", "name": "正確之星", "description": "答對 50 題", "icon": "⭐",
     "category": "general", "metric": "total_correct", "threshold": 50},
    {"code": "correct_100", "name": "滿分戰士", "description": "答對 100 題", "icon": "🏆",
     "category": "general", "metric": "total_correct", "threshold": 100},
    # Streak
    {"code": "streak_3", "name": "三日不輟", "description": "連續 3 天學習", "icon": "🔥",
     "category": "streak", "metric": "streak", "threshold": 3},
    {"code": "streak_7", "name": "一週堅持", "description": "連續 7 天學習", "icon": "⚡",
     "category": "streak", "metric": "streak", "threshold": 7},
    {"code": "streak_30", "name": "月度標兵", "description": "連續 30 天學習", "icon": "👑",
     "category": "streak", "metric": "streak", "threshold": 30},
    # Subject-specific
    {"code": "math_30", "name": "數學小能手", "description": "數學答對 30 題", "icon": "🔢",
     "category": "math", "metric": "subject_correct", "threshold": 30, "subject": "math"},
    {"code": "chinese_30", "name": "語文小達人", "description": "語文答對 30 題", "icon": "📝",
     "category": "chinese", "metric": "subject_correct", "threshold": 30, "subject": "chinese"},
    {"code": "english_30", "name": "英語小明星", "description": "英語答對 30 題", "icon": "🔤",
     "category": "english", "metric": "subject_correct", "threshold": 30, "subject": "english"},
]

# Pet types unlocked at level milestones
PET_UNLOCK_LEVELS = {
    1: [("cat", "小貓", "🐱"), ("dog", "小狗", "🐶")],
    3: [("rabbit", "兔子", "🐰"), ("hamster", "倉鼠", "🐹")],
    5: [("dragon", "小龍", "🐲"), ("unicorn", "獨角獸", "🦄")],
    10: [("phoenix", "鳳凰", "🦅"), ("panda", "熊貓", "🐼")],
}

# Pet accessories unlocked at achievements
ACCESSORY_UNLOCKS = {
    "correct_50": ("hat_crown", "👑"),
    "correct_100": ("scarf_gold", "🟡"),
    "streak_7": ("hat_star", "🌟"),
    "streak_30": ("aura_rainbow", "🌈"),
}

# EXP per action
EXP_CORRECT = 10
EXP_WRONG = 3
EXP_DAILY_BONUS = 20


def ensure_achievements_seeded(db: Session):
    """Seed achievement definitions if not present."""
    if db.query(Achievement).count() == 0:
        for defn in ACHIEVEMENT_DEFS:
            db.add(Achievement(**defn))
        db.commit()


def get_current_streak(db: Session, child_id: int) -> int:
    """Calculate current consecutive day streak."""
    today = date.today()
    streak = 0
    d = today
    for _ in range(365):  # max lookback
        record = db.query(DailyStreak).filter(
            DailyStreak.child_id == child_id,
            DailyStreak.study_date == d,
        ).first()
        if record and record.questions_answered > 0:
            streak += 1
            from datetime import timedelta
            d = d - timedelta(days=1)
        else:
            # Allow today to be empty (haven't answered yet today)
            if d == today:
                from datetime import timedelta
                d = d - timedelta(days=1)
                continue
            break
    return streak


def get_subject_correct_count(db: Session, child_id: int, subject: str) -> int:
    return db.query(AnswerRecord).filter(
        AnswerRecord.child_id == child_id,
        AnswerRecord.subject == subject,
        AnswerRecord.is_correct == True,
    ).count()


def update_daily_streak(db: Session, child_id: int, is_correct: bool):
    """Update today's streak record."""
    today = date.today()
    record = db.query(DailyStreak).filter(
        DailyStreak.child_id == child_id,
        DailyStreak.study_date == today,
    ).first()
    if not record:
        record = DailyStreak(child_id=child_id, study_date=today, questions_answered=0, correct_count=0)
        db.add(record)
        db.flush()  # ensure defaults are loaded
    record.questions_answered = (record.questions_answered or 0) + 1
    if is_correct:
        record.correct_count += 1


def check_and_unlock_achievements(db: Session, child_id: int) -> list[dict]:
    """Check all achievement conditions and unlock new ones. Returns newly unlocked."""
    ensure_achievements_seeded(db)
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        return []

    streak = get_current_streak(db, child_id)
    unlocked = []

    all_achievements = db.query(Achievement).all()
    existing_ids = set(
        ua.achievement_id for ua in
        db.query(ChildAchievement).filter(ChildAchievement.child_id == child_id).all()
    )

    for ach in all_achievements:
        if ach.id in existing_ids:
            continue

        met = False
        if ach.metric == "total_questions":
            met = child.total_questions >= ach.threshold
        elif ach.metric == "total_correct":
            met = child.total_correct >= ach.threshold
        elif ach.metric == "streak":
            met = streak >= ach.threshold
        elif ach.metric == "subject_correct":
            if ach.subject:
                count = get_subject_correct_count(db, child_id, ach.subject)
                met = count >= ach.threshold

        if met:
            db.add(ChildAchievement(child_id=child_id, achievement_id=ach.id))
            unlocked.append({
                "code": ach.code, "name": ach.name, "icon": ach.icon,
                "description": ach.description,
            })

            # Unlock pet accessory if applicable
            if ach.code in ACCESSORY_UNLOCKS:
                acc_code, acc_emoji = ACCESSORY_UNLOCKS[ach.code]
                existing = db.query(PetAccessory).filter(
                    PetAccessory.child_id == child_id,
                    PetAccessory.accessory_code == acc_code,
                ).first()
                if not existing:
                    db.add(PetAccessory(
                        child_id=child_id,
                        accessory_code=acc_code,
                        accessory_emoji=acc_emoji,
                    ))

    return unlocked


def grant_pet_exp(db: Session, child_id: int, is_correct: bool):
    """Give EXP to active pet. Level up if threshold met."""
    pet = db.query(ChildPet).filter(
        ChildPet.child_id == child_id,
        ChildPet.is_active == True,
    ).first()
    if not pet:
        # Auto-create a starter pet
        pet = ChildPet(child_id=child_id, pet_type="cat", pet_name="小貓", pet_emoji="🐱")
        db.add(pet)
        db.flush()

    exp_gain = EXP_CORRECT if is_correct else EXP_WRONG
    pet.exp += exp_gain
    pet.happiness = min(100, pet.happiness + (2 if is_correct else 0))
    pet.hunger = min(100, pet.hunger + 1)
    pet.last_interaction = datetime.utcnow()

    # Level up: each level needs level * 100 EXP
    while pet.exp >= pet.level * 100:
        pet.exp -= pet.level * 100
        pet.level += 1

    db.flush()
    return pet


def check_pet_unlocks(db: Session, child_id: int) -> list[dict]:
    """Check if new pets should be unlocked based on active pet level."""
    pet = db.query(ChildPet).filter(
        ChildPet.child_id == child_id,
        ChildPet.is_active == True,
    ).first()
    if not pet:
        return []

    unlocked = []
    for unlock_level, pets in PET_UNLOCK_LEVELS.items():
        if pet.level >= unlock_level:
            for pet_type, pet_name, pet_emoji in pets:
                existing = db.query(ChildPet).filter(
                    ChildPet.child_id == child_id,
                    ChildPet.pet_type == pet_type,
                ).first()
                if not existing:
                    db.add(ChildPet(
                        child_id=child_id, pet_type=pet_type,
                        pet_name=pet_name, pet_emoji=pet_emoji,
                        is_active=False,
                    ))
                    unlocked.append({"pet_type": pet_type, "pet_name": pet_name, "pet_emoji": pet_emoji})
    return unlocked


def process_answer(db: Session, child_id: int, is_correct: bool) -> dict:
    """Main entry point: called after each answer. Returns all rewards."""
    update_daily_streak(db, child_id, is_correct)
    grant_pet_exp(db, child_id, is_correct)
    new_achievements = check_and_unlock_achievements(db, child_id)
    new_pets = check_pet_unlocks(db, child_id)
    streak = get_current_streak(db, child_id)

    return {
        "streak": streak,
        "new_achievements": new_achievements,
        "new_pets": new_pets,
    }
