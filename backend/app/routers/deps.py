"""Auth dependencies.
- get_current_parent: JWT for parent app
- get_child_from_device_token: device_token + X-Child-Id for child app
- get_current_admin: JWT for admin (backend management)
"""
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.parent import Parent
from app.models.child import Child
from app.models.device import Device
from app.models.admin import Admin
from app.services.auth_service import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_parent(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Parent:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    parent_id = payload.get("sub")
    if parent_id is None:
        raise credentials_exception
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if parent is None:
        raise credentials_exception
    return parent


def get_child_from_device_token(
    x_device_token: Optional[str] = Header(None),
    x_child_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Child:
    """Authenticate child app requests using device_token + X-Child-Id.
    
    Every child API call must include:
      X-Device-Token: <32-char hex from device binding>
      X-Child-Id: <child_id selected on user selection page>
    
    Returns the Child object if valid. Raises 401 if token invalid/expired.
    """
    if not x_device_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少設備令牌",
        )
    
    # Find active device by token
    device = db.query(Device).filter(
        Device.device_token == x_device_token,
        Device.is_active == True,
    ).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="設備令牌已失效，請重新綁定",
        )
    
    # Must have a child selected
    if not x_child_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="請先選擇用戶",
        )
    
    # Validate child belongs to the device's parent
    child = db.query(Child).filter(
        Child.id == int(x_child_id),
        Child.parent_id == device.parent_id,
    ).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權訪問此子女資料",
        )
    return child


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    """Authenticate admin requests via JWT with role='admin'."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="管理員憑證無效",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    payload = decode_access_token(token)
    if payload is None or payload.get("role") != "admin":
        raise credentials_exception
    admin_id = payload.get("sub")
    if admin_id is None:
        raise credentials_exception
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        raise credentials_exception
    return admin
