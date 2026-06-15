"""Learning plan routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.parent import Parent
from app.models.plan import LearningPlan
from app.schemas.plan import PlanCreate, PlanUpdate, PlanOut
from app.routers.deps import get_current_parent

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.get("", response_model=list[PlanOut])
def list_plans(parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    return db.query(LearningPlan).filter(LearningPlan.parent_id == parent.id).order_by(LearningPlan.created_at.desc()).all()


@router.post("", response_model=PlanOut, status_code=201)
def create_plan(payload: PlanCreate, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    plan = LearningPlan(parent_id=parent.id, **payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.put("/{plan_id}", response_model=PlanOut)
def update_plan(plan_id: int, payload: PlanUpdate, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    plan = db.query(LearningPlan).filter(LearningPlan.id == plan_id, LearningPlan.parent_id == parent.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="找不到計劃")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}")
def delete_plan(plan_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    plan = db.query(LearningPlan).filter(LearningPlan.id == plan_id, LearningPlan.parent_id == parent.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="找不到計劃")
    db.delete(plan)
    db.commit()
    return {"success": True, "message": "計劃已刪除"}


@router.patch("/{plan_id}/toggle", response_model=PlanOut)
def toggle_plan(plan_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    plan = db.query(LearningPlan).filter(LearningPlan.id == plan_id, LearningPlan.parent_id == parent.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="找不到計劃")
    plan.is_active = not plan.is_active
    db.commit()
    db.refresh(plan)
    return plan
