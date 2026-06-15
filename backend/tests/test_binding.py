"""Binding endpoint tests."""


def test_generate_qr(client, auth_headers):
    resp = client.post("/api/binding/qr/generate", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "qr_token" in data
    assert "expires_at" in data
    assert data["parent_id"] == 1


def test_generate_qr_no_auth(client):
    resp = client.post("/api/binding/qr/generate")
    assert resp.status_code == 401


def test_verify_qr_success(client, auth_headers):
    qr = client.post("/api/binding/qr/generate", headers=auth_headers)
    token = qr.json()["qr_token"]
    resp = client.post("/api/binding/qr/verify", json={
        "qr_token": token,
        "device_uuid": "device-001",
        "child_name": "小明",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["child_id"] is not None
    assert "小明" in data["welcome_message"]


def test_verify_qr_invalid_token(client):
    resp = client.post("/api/binding/qr/verify", json={
        "qr_token": "invalid_token",
        "device_uuid": "device-002",
        "child_name": "小華",
    })
    assert resp.status_code == 400


def test_verify_qr_duplicate_device(client, auth_headers):
    qr = client.post("/api/binding/qr/generate", headers=auth_headers)
    token = qr.json()["qr_token"]
    # First bind
    client.post("/api/binding/qr/verify", json={
        "qr_token": token,
        "device_uuid": "dup-device",
        "child_name": "第一個",
    })
    # Second bind with same device
    qr2 = client.post("/api/binding/qr/generate", headers=auth_headers)
    token2 = qr2.json()["qr_token"]
    resp = client.post("/api/binding/qr/verify", json={
        "qr_token": token2,
        "device_uuid": "dup-device",
        "child_name": "第二個",
    })
    assert resp.status_code == 400


def test_bind_three_children_max(client, auth_headers):
    """One parent can bind up to 3 children."""
    for i in range(3):
        qr = client.post("/api/binding/qr/generate", headers=auth_headers)
        token = qr.json()["qr_token"]
        resp = client.post("/api/binding/qr/verify", json={
            "qr_token": token,
            "device_uuid": f"device-{i}",
            "child_name": f"child{i}",
        })
        assert resp.status_code == 200

    # 4th should fail
    qr = client.post("/api/binding/qr/generate", headers=auth_headers)
    token = qr.json()["qr_token"]
    resp = client.post("/api/binding/qr/verify", json={
        "qr_token": token,
        "device_uuid": "device-4",
        "child_name": "child4",
    })
    assert resp.status_code == 400
