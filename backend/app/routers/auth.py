"""Auth routes: register, login, me."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.parent import Parent
from app.schemas.auth import ParentCreate, ParentLogin, Token, ParentOut
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.routers.deps import get_current_parent

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=201)
def register(payload: ParentCreate, db: Session = Depends(get_db)):
    existing = db.query(Parent).filter(Parent.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="此郵箱已註冊")
    parent = Parent(
        email=payload.email,
        password_hash=hash_password(payload.password),
        email_verified=True,  # MVP: auto-verify
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)
    token = create_access_token({"sub": parent.id})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(payload: ParentLogin, db: Session = Depends(get_db)):
    parent = db.query(Parent).filter(Parent.email == payload.email).first()
    if not parent or not verify_password(payload.password, parent.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="郵箱或密碼錯誤",
        )
    token = create_access_token({"sub": parent.id})
    return Token(access_token=token)


@router.get("/me", response_model=ParentOut)
def me(parent: Parent = Depends(get_current_parent)):
    return parent
