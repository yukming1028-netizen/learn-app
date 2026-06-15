"""Auth endpoint tests."""
from app.models.parent import Parent


def test_register_success(client):
    resp = client.post("/api/auth/register", json={"email": "new@test.com", "password": "testpass123"})
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={"email": "dup@test.com", "password": "testpass123"})
    resp = client.post("/api/auth/register", json={"email": "dup@test.com", "password": "testpass123"})
    assert resp.status_code == 400
    assert "已註冊" in resp.json()["detail"]


def test_register_short_password(client):
    resp = client.post("/api/auth/register", json={"email": "short@test.com", "password": "123"})
    assert resp.status_code == 422


def test_register_invalid_email(client):
    resp = client.post("/api/auth/register", json={"email": "notanemail", "password": "testpass123"})
    assert resp.status_code == 422


def test_login_success(client):
    client.post("/api/auth/register", json={"email": "login@test.com", "password": "testpass123"})
    resp = client.post("/api/auth/login", json={"email": "login@test.com", "password": "testpass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"email": "wrong@test.com", "password": "testpass123"})
    resp = client.post("/api/auth/login", json={"email": "wrong@test.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_login_nonexistent(client):
    resp = client.post("/api/auth/login", json={"email": "nobody@test.com", "password": "testpass123"})
    assert resp.status_code == 401


def test_me_success(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "parent@test.com"


def test_me_no_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_invalid_token(client):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401


def test_password_hashed_in_db(client, db_session):
    client.post("/api/auth/register", json={"email": "hash@test.com", "password": "plaintext123"})
    parent = db_session.query(Parent).filter(Parent.email == "hash@test.com").first()
    assert parent is not None
    assert parent.password_hash != "plaintext123"
    assert "$2" in parent.password_hash
