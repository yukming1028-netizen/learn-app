"""Children and progress endpoint tests."""


def test_list_children(client, auth_headers, child_id):
    resp = client.get("/api/children", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "TestKid"


def test_create_child(client, auth_headers):
    resp = client.post("/api/children", json={"name": "Alice", "grade": 2}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice"
    assert resp.json()["grade"] == 2


def test_max_children(client, auth_headers, child_id):
    client.post("/api/children", json={"name": "B", "grade": 1}, headers=auth_headers)
    client.post("/api/children", json={"name": "C", "grade": 1}, headers=auth_headers)
    resp = client.post("/api/children", json={"name": "D", "grade": 1}, headers=auth_headers)
    assert resp.status_code == 400


def test_get_child_detail(client, auth_headers, child_id):
    resp = client.get(f"/api/children/{child_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "TestKid"


def test_update_child(client, auth_headers, child_id):
    resp = client.put(f"/api/children/{child_id}", json={"name": "新名字", "grade": 3}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "新名字"
    assert resp.json()["grade"] == 3


def test_update_grade_resets_set_at(client, auth_headers, child_id):
    """Updating grade should reset grade_set_at and clear dismissal."""
    resp = client.put(f"/api/children/{child_id}", json={"grade": 3}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["grade"] == 3
    assert resp.json()["grade_set_at"] is not None


def test_delete_child(client, auth_headers, child_id):
    resp = client.delete(f"/api/children/{child_id}", headers=auth_headers)
    assert resp.status_code == 200
    resp = client.get(f"/api/children/{child_id}", headers=auth_headers)
    assert resp.status_code == 404


def test_child_not_found(client, auth_headers):
    resp = client.get("/api/children/9999", headers=auth_headers)
    assert resp.status_code == 404


def test_child_stats(client, auth_headers, child_id):
    resp = client.get(f"/api/children/{child_id}/stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "daily_trend" in data
    assert "weekly_trend" in data
    assert "subject_breakdown" in data
    assert len(data["daily_trend"]) == 7
    assert len(data["weekly_trend"]) == 4


def test_grade_check_no_prompt(client, auth_headers, child_id):
    """Fresh child should not need grade prompt."""
    resp = client.get(f"/api/children/{child_id}/grade-check", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["needs_prompt"] is False


def test_grade_dismiss(client, auth_headers, child_id):
    resp = client.post(f"/api/children/{child_id}/grade/dismiss", headers=auth_headers)
    assert resp.status_code == 200
