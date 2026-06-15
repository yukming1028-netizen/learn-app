"""Test fixtures and configuration."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.middleware.rate_limit import RateLimitMiddleware

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def reset_rate_limit():
    if RateLimitMiddleware._instance:
        RateLimitMiddleware._instance.reset()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    """Provide a test DB session for direct DB writes in tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_user(client):
    """Register + login, return {email, token, headers}."""
    client.post("/api/auth/register", json={"email": "parent@test.com", "password": "testpass123"})
    resp = client.post("/api/auth/login", json={"email": "parent@test.com", "password": "testpass123"})
    token = resp.json()["access_token"]
    return {
        "email": "parent@test.com",
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def auth_headers(auth_user):
    return auth_user["headers"]


@pytest.fixture
def child_id(client, auth_headers):
    """Create a child via QR binding, return child_id."""
    qr = client.post("/api/binding/qr/generate", headers=auth_headers)
    token = qr.json()["qr_token"]
    resp = client.post("/api/binding/qr/verify", json={
        "qr_token": token,
        "device_uuid": "test-uuid-001",
        "child_name": "TestKid",
    })
    return resp.json()["child_id"]
