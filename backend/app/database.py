"""Database engine and session management."""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables, apply SQLite optimizations, and ensure default admin exists."""
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA busy_timeout=5000"))
        conn.commit()
    _ensure_default_admin()


def _ensure_default_admin():
    """Create a default super admin if none exists."""
    from app.models.admin import Admin
    from app.services.auth_service import hash_password
    db = SessionLocal()
    try:
        if db.query(Admin).count() == 0:
            db.add(Admin(
                username="admin",
                password_hash=hash_password("admin123"),
                display_name="超級管理員",
                is_super=True,
            ))
            db.commit()
            print("✅ Default admin created: admin / admin123")
    finally:
        db.close()
