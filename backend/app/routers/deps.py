"""Auth dependency: get current parent from JWT, or child via X-Child-Id."""
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.parent import Parent
from app.models.child import Child
from app.services.auth_service import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_parent(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Parent:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )
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


def get_child_or_parent(
    x_child_id: Optional[str] = Header(None),
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Auth that works for both child app (X-Child-Id header) and parent app (JWT).
    Returns a dict: {"type": "parent"/"child", "parent_id": int, "child_id": int|None}
    """
    # Try child auth first
    if x_child_id:
        child = db.query(Child).filter(Child.id == int(x_child_id)).first()
        if child:
            return {"type": "child", "parent_id": child.parent_id, "child_id": child.id}

    # Fall back to JWT parent auth
    if token:
        payload = decode_access_token(token)
        if payload and payload.get("sub"):
            parent = db.query(Parent).filter(Parent.id == payload["sub"]).first()
            if parent:
                return {"type": "parent", "parent_id": parent.id, "child_id": None}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證憑證",
    )
