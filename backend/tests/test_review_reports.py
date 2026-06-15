"""Review (spaced repetition) and Report endpoint tests."""
from app.models.question import Question
from app.models.review import ReviewSchedule


def test_review_empty(client, device_headers, child_id):
    resp = client.get("/api/review", headers=device_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_review_count_zero(client, device_headers, child_id):
    resp = client.get("/api/review/count", headers=device_headers)
    assert resp.status_code == 200
    assert resp.json()["due_count"] == 0


def test_review_created_on_wrong_answer(client, device_headers, child_id, db_session):
    q = Question(subject="math", grade=1, difficulty=2, type="choice",
                 content="7+8=?", options=["13", "14", "15", "16"], answer="15")
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)

    # Answer incorrectly
    client.post("/api/questions/answer", json={
        "question_id": q.id,
        "selected_answer": "14",
        "time_taken_sec": 25.0,
    }, headers=device_headers)

    # Expire cache so we see API's committed data
    db_session.expire_all()

    review = db_session.query(ReviewSchedule).filter(
        ReviewSchedule.child_id == child_id,
        ReviewSchedule.question_id == q.id,
    ).first()
    assert review is not None
    assert review.ease_factor < 2.5


def test_report_pdf_download(client, auth_headers, child_id):
    resp = client.get(f"/api/reports/{child_id}/pdf?period_days=30", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "attachment" in resp.headers.get("content-disposition", "")
    content = resp.content
    assert len(content) > 100
    assert content[:4] == b"%PDF"


def test_report_nonexistent_child(client, auth_headers):
    resp = client.get("/api/reports/9999/pdf", headers=auth_headers)
    assert resp.status_code == 404
