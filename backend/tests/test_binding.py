"""Binding endpoint tests — reversed flow: device generates code, parent consumes."""


def test_device_generate(client):
    """Device can generate QR token + bind code without auth."""
    resp = client.post("/api/binding/device/generate", json={"device_uuid": "dev-001"})
    assert resp.status_code == 200
    data = resp.json()
    assert "qr_token" in data
    assert "bind_code" in data
    assert len(data["bind_code"]) == 6
    assert "expires_at" in data


def test_device_verify_success(client, auth_headers):
    """Parent can bind a device by scanning QR token."""
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-002"})
    token = gen.json()["qr_token"]
    resp = client.post("/api/binding/device/verify", json={
        "qr_token": token,
        "child_name": "小明",
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["child_id"] is not None
    assert "小明" in data["welcome_message"]


def test_device_verify_by_bind_code(client, auth_headers):
    """Parent can bind via 6-char bind code."""
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-003"})
    code = gen.json()["bind_code"]
    resp = client.post("/api/binding/device/verify", json={
        "bind_code": code,
        "child_name": "小華",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_device_verify_no_auth(client):
    """Binding requires auth."""
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-004"})
    token = gen.json()["qr_token"]
    resp = client.post("/api/binding/device/verify", json={
        "qr_token": token,
        "child_name": "NoAuth",
    })
    assert resp.status_code == 401


def test_device_verify_invalid_token(client, auth_headers):
    resp = client.post("/api/binding/device/verify", json={
        "qr_token": "invalid_token",
        "child_name": "Bad",
    }, headers=auth_headers)
    assert resp.status_code == 400


def test_same_device_multiple_children(client, auth_headers):
    """Same device can be bound to multiple children under same parent."""
    for i in range(3):
        gen = client.post("/api/binding/device/generate", json={"device_uuid": "shared-device"})
        token = gen.json()["qr_token"]
        resp = client.post("/api/binding/device/verify", json={
            "qr_token": token,
            "child_name": f"child{i}",
        }, headers=auth_headers)
        assert resp.status_code == 200

    # Verify 3 children on same device
    resp = client.get("/api/binding/device/shared-device/children")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_max_children_per_parent(client, auth_headers):
    """Parent can bind at most 3 children."""
    for i in range(3):
        gen = client.post("/api/binding/device/generate", json={"device_uuid": f"dev-max-{i}"})
        token = gen.json()["qr_token"]
        resp = client.post("/api/binding/device/verify", json={
            "qr_token": token,
            "child_name": f"child{i}",
        }, headers=auth_headers)
        assert resp.status_code == 200

    # 4th should fail
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-max-4"})
    token = gen.json()["qr_token"]
    resp = client.post("/api/binding/device/verify", json={
        "qr_token": token,
        "child_name": "child4",
    }, headers=auth_headers)
    assert resp.status_code == 400


def test_parent_unbind_child(client, auth_headers):
    """Parent can unbind a child."""
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-unbind"})
    token = gen.json()["qr_token"]
    resp = client.post("/api/binding/device/verify", json={
        "qr_token": token,
        "child_name": "ToUnbind",
    }, headers=auth_headers)
    child_id = resp.json()["child_id"]

    resp = client.delete(f"/api/binding/unbind/{child_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_device_unbind_self(client, auth_headers):
    """Device can unbind a child profile."""
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-self-unbind"})
    token = gen.json()["qr_token"]
    resp = client.post("/api/binding/device/verify", json={
        "qr_token": token,
        "child_name": "SelfUnbind",
    }, headers=auth_headers)
    child_id = resp.json()["child_id"]

    resp = client.post("/api/binding/device/unbind", json={
        "device_uuid": "dev-self-unbind",
        "child_id": child_id,
    })
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_device_list_children(client, auth_headers):
    """List children bound to a device."""
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-list"})
    token = gen.json()["qr_token"]
    client.post("/api/binding/device/verify", json={
        "qr_token": token,
        "child_name": "Listed",
    }, headers=auth_headers)

    resp = client.get("/api/binding/device/dev-list/children")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Listed"
