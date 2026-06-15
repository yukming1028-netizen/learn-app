"""Binding routes — device generates QR/code, parent scans and binds."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.parent import Parent
from app.models.child import Child
from app.schemas.binding import (
    DeviceGenerateRequest, DeviceGenerateResponse,
    DeviceBindRequest, DeviceUnbindRequest,
    BindResult, DeviceChildOut,
)
from app.utils.qr import generate_device_bind_token, verify_device_bind_token
from app.utils.bind_code import store_bind_code, lookup_bind_code
from app.utils.grade import compute_current_grade, grade_label
from app.routers.deps import get_current_parent

router = APIRouter(prefix="/api/binding", tags=["binding"])


# ─── Child device: generate QR / bind code ───

@router.post("/device/generate", response_model=DeviceGenerateResponse)
def device_generate(req: DeviceGenerateRequest):
    """Child device generates a QR token + short bind code for parent to scan."""
    token, expires_at = generate_device_bind_token(req.device_uuid)
    expires_ts = expires_at.timestamp()
    code = store_bind_code(token, 0, expires_ts)
    return DeviceGenerateResponse(
        qr_token=token,
        bind_code=code,
        expires_at=expires_at.isoformat(),
    )


# ─── Child device: list bound children ───

@router.get("/device/{device_uuid}/children", response_model=list[DeviceChildOut])
def device_list_children(device_uuid: str, db: Session = Depends(get_db)):
    """List all child profiles bound to this device (from any parent)."""
    children = db.query(Child).filter(Child.device_uuid == device_uuid).all()
    result = []
    for c in children:
        # Compute current grade
        if c.grade_start_date:
            cur_grade, cur_label = compute_current_grade(c.grade, c.grade_start_date)
        else:
            cur_grade, cur_label = c.grade, grade_label(c.grade)
        result.append(DeviceChildOut(
            id=c.id, name=c.name, avatar=c.avatar,
            grade=cur_grade, grade_label=cur_label,
            parent_email=c.parent.email if c.parent else "",
            total_questions=c.total_questions,
            total_correct=c.total_correct,
        ))
    return result


# ─── Parent: scan QR / enter code to bind ───

@router.post("/device/verify", response_model=BindResult)
def device_verify(payload: DeviceBindRequest, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    """Parent scans QR or enters bind code to bind a device to a child profile."""
    # Resolve token
    qr_token = payload.qr_token
    if not qr_token and payload.bind_code:
        qr_token = lookup_bind_code(payload.bind_code)
        if not qr_token:
            raise HTTPException(status_code=400, detail="綁定碼無效或已過期")
    if not qr_token:
        raise HTTPException(status_code=400, detail="請提供 QR 碼或綁定碼")

    data = verify_device_bind_token(qr_token)
    if data is None:
        raise HTTPException(status_code=400, detail="綁定碼無效或已過期")

    device_uuid = data["device_uuid"]

    # Check max children per parent (3) — no device limit
    child_count = db.query(Child).filter(Child.parent_id == parent.id).count()
    if child_count >= settings.MAX_CHILDREN_PER_PARENT:
        raise HTTPException(status_code=400, detail=f"已達最大子女數限制（{settings.MAX_CHILDREN_PER_PARENT}名）")

    # Create child profile
    now = datetime.now(timezone.utc)
    child = Child(
        parent_id=parent.id,
        name=payload.child_name,
        grade=payload.grade,
        grade_start_date=now,
        device_uuid=device_uuid,
        bound_at=now,
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    g_label = grade_label(payload.grade)
    return BindResult(
        success=True,
        child_id=child.id,
        child_name=child.name,
        grade=payload.grade,
        grade_label=g_label,
        device_uuid=device_uuid,
        welcome_message=f"已成功綁定！{child.name}（{g_label}）可以開始學習了！🎉",
    )


# ─── Parent: unbind a child ───

@router.delete("/unbind/{child_id}")
def parent_unbind_child(child_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    """Parent unbinds (deletes) a child profile."""
    child = db.query(Child).filter(Child.id == child_id, Child.parent_id == parent.id).first()
    if not child:
        raise HTTPException(status_code=404, detail="找不到子女")
    child_name = child.name
    db.delete(child)
    db.commit()
    return {"success": True, "message": f"已解除 {child_name} 的綁定"}


# ─── Child device: unbind self ───

@router.post("/device/unbind")
def device_unbind(payload: DeviceUnbindRequest, db: Session = Depends(get_db)):
    """Child device removes a specific child profile binding."""
    child = db.query(Child).filter(
        Child.id == payload.child_id,
        Child.device_uuid == payload.device_uuid,
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="找不到綁定記錄")
    db.delete(child)
    db.commit()
    return {"success": True, "message": "已解除綁定"}
