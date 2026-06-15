"""Children and progress endpoint tests."""


def test_list_children(client, auth_headers, child_id):
    resp = client.get("/api/children", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "TestKid"


def test_get_child_detail(client, auth_headers, child_id):
    resp = client.get(f"/api/children/{child_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "TestKid"


def test_update_child(client, auth_headers, child_id):
    resp = client.put(f"/api/children/{child_id}", json={"name": "新名字", "grade": 3}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "新名字"
    assert resp.json()["grade"] == 3


def test_delete_child(client, auth_headers, child_id):
    resp = client.delete(f"/api/children/{child_id}", headers=auth_headers)
    assert resp.status_code == 200
    # Verify deleted
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


def test_today_progress(client, auth_headers, child_id):
    resp = client.get(f"/api/progress/today/{child_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["completed_count"] == 0
    assert data["target_count"] >= 1
