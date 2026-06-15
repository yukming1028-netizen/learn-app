"""Binding routes: QR code / bind code generation and verification."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.parent import Parent
from app.models.child import Child
from app.schemas.binding import QRGenerateResponse, QRVerifyRequest, CodeVerifyRequest, BindResult
from app.utils.qr import generate_qr_token, verify_qr_token
from app.utils.bind_code import store_bind_code, lookup_bind_code
from app.routers.deps import get_current_parent

router = APIRouter(prefix="/api/binding", tags=["binding"])


@router.post("/qr/generate", response_model=QRGenerateResponse)
def generate_qr(parent: Parent = Depends(get_current_parent)):
    token, expires_at = generate_qr_token(parent.id)
    expires_ts = expires_at.timestamp()
    code = store_bind_code(token, parent.id, expires_ts)
    return QRGenerateResponse(
        qr_token=token,
        bind_code=code,
        expires_at=expires_at.isoformat(),
        parent_id=parent.id,
    )


def _do_bind(qr_token: str, device_uuid: str, child_name: str, db: Session) -> BindResult:
    """Shared binding logic for both QR token and bind code."""
    data = verify_qr_token(qr_token)
    if data is None:
        raise HTTPException(status_code=400, detail="綁定碼無效或已過期")

    parent_id = data["parent_id"]
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="家長帳號不存在")

    # Check max children limit
    existing_count = db.query(Child).filter(Child.parent_id == parent_id).count()
    if existing_count >= settings.MAX_CHILDREN_PER_PARENT:
        raise HTTPException(status_code=400, detail=f"已達最大子女數限制（{settings.MAX_CHILDREN_PER_PARENT}名）")

    # Check device UUID not already bound
    existing_child = db.query(Child).filter(Child.device_uuid == device_uuid).first()
    if existing_child:
        raise HTTPException(status_code=400, detail="此設備已綁定其他子女帳號")

    child = Child(
        parent_id=parent_id,
        name=child_name,
        device_uuid=device_uuid,
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


@router.post("/qr/verify", response_model=BindResult)
def verify_qr(payload: QRVerifyRequest, db: Session = Depends(get_db)):
    return _do_bind(payload.qr_token, payload.device_uuid, payload.child_name, db)


@router.post("/code/verify", response_model=BindResult)
def verify_code(payload: CodeVerifyRequest, db: Session = Depends(get_db)):
    qr_token = lookup_bind_code(payload.bind_code)
    if qr_token is None:
        raise HTTPException(status_code=400, detail="綁定碼無效或已過期")
    return _do_bind(qr_token, payload.device_uuid, payload.child_name, db)
