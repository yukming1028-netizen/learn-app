"""Admin (管理員) model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), default="管理員")
    is_super = Column(Boolean, default=False)  # 超級管理員
    created_at = Column(DateTime, default=datetime.utcnow)
