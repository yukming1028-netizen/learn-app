"""Binding endpoint tests — device links to parent with token, sees all children."""


def test_device_generate(client):
    resp = client.post("/api/binding/device/generate", json={"device_uuid": "dev-001"})
    assert resp.status_code == 200
    data = resp.json()
    assert "qr_token" in data
    assert "bind_code" in data
    assert len(data["bind_code"]) == 6


def test_device_verify_success(client, auth_headers):
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-002"})
    token = gen.json()["qr_token"]
    resp = client.post("/api/binding/device/verify", json={"qr_token": token}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert len(resp.json()["device_token"]) == 32


def test_device_verify_by_code(client, auth_headers):
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-003"})
    code = gen.json()["bind_code"]
    resp = client.post("/api/binding/device/verify", json={"bind_code": code}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_device_verify_no_auth(client):
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-004"})
    token = gen.json()["qr_token"]
    resp = client.post("/api/binding/device/verify", json={"qr_token": token})
    assert resp.status_code == 401


def test_device_verify_invalid_token(client, auth_headers):
    resp = client.post("/api/binding/device/verify", json={"qr_token": "bad"}, headers=auth_headers)
    assert resp.status_code == 400


def test_device_already_bound_to_other_parent(client, auth_headers):
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-exclusive"})
    token = gen.json()["qr_token"]
    client.post("/api/binding/device/verify", json={"qr_token": token}, headers=auth_headers)

    client.post("/api/auth/register", json={"email": "parent2@test.com", "password": "secret123"})
    resp = client.post("/api/auth/login", json={"email": "parent2@test.com", "password": "secret123"})
    headers2 = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    resp = client.post("/api/binding/device/verify", json={"qr_token": token}, headers=headers2)
    assert resp.status_code == 400
    assert "其他家長" in resp.json()["detail"]


def test_device_status_returns_token(client, auth_headers):
    """Device status endpoint returns device_token after binding."""
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-token"})
    token = gen.json()["qr_token"]
    verify_resp = client.post("/api/binding/device/verify", json={"qr_token": token}, headers=auth_headers)
    expected_token = verify_resp.json()["device_token"]

    resp = client.get("/api/binding/device/dev-token/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["bound"] is True
    assert data["device_token"] == expected_token


def test_device_bound_sees_all_children(client, auth_headers, child_id):
    """Device sees all children of the linked parent."""
    # Create another child
    client.post("/api/children", json={"name": "Alice", "grade": 1}, headers=auth_headers)

    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-children"})
    token = gen.json()["qr_token"]
    client.post("/api/binding/device/verify", json={"qr_token": token}, headers=auth_headers)

    resp = client.get("/api/binding/device/dev-children/children")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


def test_parent_list_devices(client, auth_headers):
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-list-1"})
    client.post("/api/binding/device/verify", json={"qr_token": gen.json()["qr_token"]}, headers=auth_headers)

    resp = client.get("/api/binding/devices", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_parent_unlink_invalidates_token(client, auth_headers):
    """Unlinking a device invalidates its token."""
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-invalidate"})
    token = gen.json()["qr_token"]
    verify_resp = client.post("/api/binding/device/verify", json={"qr_token": token}, headers=auth_headers)
    old_token = verify_resp.json()["device_token"]

    # Unlink
    resp = client.delete("/api/binding/device/dev-invalidate", headers=auth_headers)
    assert resp.status_code == 200

    # Status should show not bound
    resp = client.get("/api/binding/device/dev-invalidate/status")
    assert resp.json()["bound"] is False

    # Old device_token should no longer work (no active device found)
    # Using the token in a child API call should return 401
    resp = client.get("/api/progress/today", headers={"X-Device-Token": old_token, "X-Child-Id": "1"})
    assert resp.status_code == 401


def test_device_unbind_self(client, auth_headers):
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-self"})
    client.post("/api/binding/device/verify", json={"qr_token": gen.json()["qr_token"]}, headers=auth_headers)

    resp = client.post("/api/binding/device/unbind", json={"device_uuid": "dev-self"})
    assert resp.status_code == 200

    resp = client.get("/api/binding/device/dev-self/status")
    assert resp.json()["bound"] is False


def test_max_devices(client, auth_headers):
    for i in range(3):
        gen = client.post("/api/binding/device/generate", json={"device_uuid": f"dev-max-{i}"})
        resp = client.post("/api/binding/device/verify", json={"qr_token": gen.json()["qr_token"]}, headers=auth_headers)
        assert resp.status_code == 200

    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-max-4"})
    resp = client.post("/api/binding/device/verify", json={"qr_token": gen.json()["qr_token"]}, headers=auth_headers)
    assert resp.status_code == 400


# ─── Device token auth tests ───

def test_child_api_requires_device_token(client, child_id):
    """Child API calls without device token should fail."""
    resp = client.get("/api/progress/today")
    assert resp.status_code == 401


def test_child_api_with_valid_token(client, auth_headers, child_id):
    """Child API calls with valid device token should work."""
    # Bind device
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-api"})
    token = gen.json()["qr_token"]
    verify_resp = client.post("/api/binding/device/verify", json={"qr_token": token}, headers=auth_headers)
    device_token = verify_resp.json()["device_token"]

    # Use child API with device token
    resp = client.get("/api/progress/today", headers={
        "X-Device-Token": device_token,
        "X-Child-Id": str(child_id),
    })
    assert resp.status_code == 200
    assert resp.json()["child_id"] == child_id


def test_child_api_wrong_parent_child(client, auth_headers, child_id):
    """Device token from parent A cannot access parent B's child."""
    # Parent A binds device
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-cross"})
    token = gen.json()["qr_token"]
    verify_resp = client.post("/api/binding/device/verify", json={"qr_token": token}, headers=auth_headers)
    device_token = verify_resp.json()["device_token"]

    # Parent B creates a child
    client.post("/api/auth/register", json={"email": "parent2@test.com", "password": "secret123"})
    resp = client.post("/api/auth/login", json={"email": "parent2@test.com", "password": "secret123"})
    headers2 = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    resp = client.post("/api/children", json={"name": "OtherChild", "grade": 1}, headers=headers2)
    other_child_id = resp.json()["id"]

    # Try to access parent B's child with parent A's device token
    resp = client.get("/api/progress/today", headers={
        "X-Device-Token": device_token,
        "X-Child-Id": str(other_child_id),
    })
    assert resp.status_code == 403


def test_child_api_invalid_token(client, child_id):
    """Invalid device token should fail."""
    resp = client.get("/api/progress/today", headers={
        "X-Device-Token": "invalidtoken123456",
        "X-Child-Id": str(child_id),
    })
    assert resp.status_code == 401


def test_child_api_no_child_id(client, auth_headers, child_id):
    """Device token without X-Child-Id should fail."""
    gen = client.post("/api/binding/device/generate", json={"device_uuid": "dev-nochild"})
    token = gen.json()["qr_token"]
    verify_resp = client.post("/api/binding/device/verify", json={"qr_token": token}, headers=auth_headers)
    device_token = verify_resp.json()["device_token"]

    resp = client.get("/api/progress/today", headers={
        "X-Device-Token": device_token,
    })
    assert resp.status_code == 401
