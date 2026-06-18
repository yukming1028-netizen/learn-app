"""Gamification routes: achievements, virtual pet, daily streak.

Child-side API (device_token auth).
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.child import Child
from app.models.gamification import (
    Achievement, ChildAchievement, ChildPet, PetAccessory, DailyStreak,
)
from app.services.gamification_service import (
    ensure_achievements_seeded, get_current_streak, check_and_unlock_achievements,
)
from app.routers.deps import get_child_from_device_token

router = APIRouter(prefix="/api/game", tags=["gamification"])


# ─── Achievements ───

@router.get("/achievements")
def get_achievements(
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Get all achievements + which ones the child has unlocked."""
    ensure_achievements_seeded(db)
    all_achs = db.query(Achievement).all()
    unlocked_ids = set(
        ua.achievement_id for ua in
        db.query(ChildAchievement).filter(ChildAchievement.child_id == child.id).all()
    )
    return [
        {
            "id": a.id,
            "code": a.code,
            "name": a.name,
            "description": a.description,
            "icon": a.icon,
            "category": a.category,
            "threshold": a.threshold,
            "unlocked": a.id in unlocked_ids,
        }
        for a in all_achs
    ]


# ─── Virtual Pet ───

class PetOut(BaseModel):
    id: int
    pet_type: str
    pet_name: str
    pet_emoji: str
    level: int
    exp: int
    exp_to_next: int  # exp needed for next level
    happiness: int
    hunger: int
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/pet")
def get_active_pet(
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Get the child's active pet."""
    pet = db.query(ChildPet).filter(
        ChildPet.child_id == child.id,
        ChildPet.is_active == True,
    ).first()
    if not pet:
        # Auto-create starter pet
        pet = ChildPet(
            child_id=child.id, pet_type="cat",
            pet_name="小貓", pet_emoji="🐱",
        )
        db.add(pet)
        db.commit()
        db.refresh(pet)

    exp_to_next = pet.level * 100
    return {
        "id": pet.id,
        "pet_type": pet.pet_type,
        "pet_name": pet.pet_name,
        "pet_emoji": pet.pet_emoji,
        "level": pet.level,
        "exp": pet.exp,
        "exp_to_next": exp_to_next,
        "happiness": pet.happiness,
        "hunger": pet.hunger,
        "is_active": True,
    }


@router.get("/pets")
def get_all_pets(
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Get all pets owned by the child."""
    pets = db.query(ChildPet).filter(ChildPet.child_id == child.id).all()
    if not pets:
        # Create starter
        pet = ChildPet(child_id=child.id, pet_type="cat", pet_name="小貓", pet_emoji="🐱")
        db.add(pet)
        db.commit()
        db.refresh(pet)
        pets = [pet]
    return [
        {
            "id": p.id,
            "pet_type": p.pet_type,
            "pet_name": p.pet_name,
            "pet_emoji": p.pet_emoji,
            "level": p.level,
            "exp": p.exp,
            "exp_to_next": p.level * 100,
            "happiness": p.happiness,
            "hunger": p.hunger,
            "is_active": p.is_active,
            "unlocked_at": p.unlocked_at.isoformat() if p.unlocked_at else None,
        }
        for p in pets
    ]


class SwitchPetRequest(BaseModel):
    pet_id: int


@router.post("/pet/switch")
def switch_pet(
    req: SwitchPetRequest,
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Switch active pet."""
    # Deactivate all
    db.query(ChildPet).filter(ChildPet.child_id == child.id).update({ChildPet.is_active: False})
    # Activate selected
    pet = db.query(ChildPet).filter(
        ChildPet.id == req.pet_id,
        ChildPet.child_id == child.id,
    ).first()
    if not pet:
        raise HTTPException(404, "找不到此寵物")
    pet.is_active = True
    db.commit()
    return {"message": f"已切換到 {pet.pet_name} {pet.pet_emoji}"}


class FeedPetRequest(BaseModel):
    pet_id: int


@router.post("/pet/feed")
def feed_pet(
    req: FeedPetRequest,
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Feed the pet (increases happiness + hunger)."""
    pet = db.query(ChildPet).filter(
        ChildPet.id == req.pet_id,
        ChildPet.child_id == child.id,
    ).first()
    if not pet:
        raise HTTPException(404, "找不到此寵物")
    pet.hunger = min(100, pet.hunger + 20)
    pet.happiness = min(100, pet.happiness + 5)
    pet.last_interaction = datetime.utcnow()
    db.commit()
    return {"message": f"{pet.pet_name} 吃飽了！😊", "hunger": pet.hunger, "happiness": pet.happiness}


# ─── Accessories ───

@router.get("/accessories")
def get_accessories(
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Get all unlocked accessories."""
    accs = db.query(PetAccessory).filter(PetAccessory.child_id == child.id).all()
    return [
        {
            "id": a.id,
            "accessory_code": a.accessory_code,
            "accessory_emoji": a.accessory_emoji,
            "is_equipped": a.is_equipped,
            "unlocked_at": a.unlocked_at.isoformat() if a.unlocked_at else None,
        }
        for a in accs
    ]


class EquipAccessoryRequest(BaseModel):
    accessory_id: int


@router.post("/accessory/equip")
def equip_accessory(
    req: EquipAccessoryRequest,
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Equip/unequip an accessory."""
    acc = db.query(PetAccessory).filter(
        PetAccessory.id == req.accessory_id,
        PetAccessory.child_id == child.id,
    ).first()
    if not acc:
        raise HTTPException(404, "找不到此配件")
    # Toggle
    acc.is_equipped = not acc.is_equipped
    db.commit()
    action = "已裝備" if acc.is_equipped else "已卸下"
    return {"message": f"{action} {acc.accessory_emoji}", "is_equipped": acc.is_equipped}


# ─── Streak ───

@router.get("/streak")
def get_streak(
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Get current daily streak + history."""
    streak = get_current_streak(db, child.id)
    recent = db.query(DailyStreak).filter(
        DailyStreak.child_id == child.id,
    ).order_by(DailyStreak.study_date.desc()).limit(30).all()

    return {
        "current_streak": streak,
        "history": [
            {
                "date": r.study_date.isoformat(),
                "questions_answered": r.questions_answered,
                "correct_count": r.correct_count,
            }
            for r in recent
        ],
    }
