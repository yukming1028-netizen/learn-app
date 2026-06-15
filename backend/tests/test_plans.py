"""Plan endpoint tests."""


def test_create_plan(client, auth_headers, child_id):
    resp = client.post("/api/plans", json={
        "child_id": child_id,
        "title": "數學強化",
        "subjects": ["math"],
        "daily_minutes": 30,
        "daily_task_count": 10,
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "數學強化"
    assert data["daily_minutes"] == 30


def test_list_plans(client, auth_headers, child_id):
    client.post("/api/plans", json={"child_id": child_id, "title": "計劃A", "subjects": ["math"]}, headers=auth_headers)
    client.post("/api/plans", json={"child_id": child_id, "title": "計劃B", "subjects": ["english"]}, headers=auth_headers)
    resp = client.get("/api/plans", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_plan(client, auth_headers, child_id):
    create = client.post("/api/plans", json={"child_id": child_id, "title": "原計劃", "subjects": ["math"]}, headers=auth_headers)
    plan_id = create.json()["id"]
    resp = client.put(f"/api/plans/{plan_id}", json={"title": "改過的計劃"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "改過的計劃"


def test_toggle_plan(client, auth_headers, child_id):
    create = client.post("/api/plans", json={"child_id": child_id, "title": "測試", "subjects": ["math"]}, headers=auth_headers)
    plan_id = create.json()["id"]
    assert create.json()["is_active"] is True

    resp = client.patch(f"/api/plans/{plan_id}/toggle", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    resp = client.patch(f"/api/plans/{plan_id}/toggle", headers=auth_headers)
    assert resp.json()["is_active"] is True


def test_delete_plan(client, auth_headers, child_id):
    create = client.post("/api/plans", json={"child_id": child_id, "title": "待刪除", "subjects": ["math"]}, headers=auth_headers)
    plan_id = create.json()["id"]
    resp = client.delete(f"/api/plans/{plan_id}", headers=auth_headers)
    assert resp.status_code == 200

    plans = client.get("/api/plans", headers=auth_headers).json()
    assert len(plans) == 0


def test_plan_not_found(client, auth_headers):
    resp = client.put("/api/plans/9999", json={"title": "x"}, headers=auth_headers)
    assert resp.status_code == 404
