"""Binding routes: QR code generation and verification."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.parent import Parent
from app.models.child import Child
from app.schemas.binding import QRGenerateResponse, QRVerifyRequest, BindResult
from app.utils.qr import generate_qr_token, verify_qr_token
from app.routers.deps import get_current_parent

router = APIRouter(prefix="/api/binding", tags=["binding"])


@router.post("/qr/generate", response_model=QRGenerateResponse)
def generate_qr(parent: Parent = Depends(get_current_parent)):
    token, expires_at = generate_qr_token(parent.id)
    return QRGenerateResponse(
        qr_token=token,
        expires_at=expires_at.isoformat(),
        parent_id=parent.id,
    )


@router.post("/qr/verify", response_model=BindResult)
def verify_qr(payload: QRVerifyRequest, db: Session = Depends(get_db)):
    data = verify_qr_token(payload.qr_token)
    if data is None:
        raise HTTPException(status_code=400, detail="QR碼無效或已過期")

    parent_id = data["parent_id"]
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="家長帳號不存在")

    # Check max children limit
    existing_count = db.query(Child).filter(Child.parent_id == parent_id).count()
    if existing_count >= settings.MAX_CHILDREN_PER_PARENT:
        raise HTTPException(status_code=400, detail=f"已達最大子女數限制（{settings.MAX_CHILDREN_PER_PARENT}名）")

    # Check device UUID not already bound
    existing_child = db.query(Child).filter(Child.device_uuid == payload.device_uuid).first()
    if existing_child:
        raise HTTPException(status_code=400, detail="此設備已綁定其他子女帳號")

    child = Child(
        parent_id=parent_id,
        name=payload.child_name,
        device_uuid=payload.device_uuid,
        bound_at=datetime.now(timezone.utc),
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    return BindResult(
        success=True,
        child_id=child.id,
        child_name=child.name,
        welcome_message=f"哇！{child.name}已成功綁定～讓我們開始學習吧！🎉",
    )
