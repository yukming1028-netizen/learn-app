"""Question and answer endpoint tests."""
from app.models.question import Question


def test_list_questions_empty(client):
    resp = client.get("/api/questions")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_questions_with_data(client, db_session):
    q = Question(subject="math", grade=1, difficulty=1, type="choice",
                 content="1+1=?", options=["1", "2", "3", "4"], answer="2",
                 explanation="1+1=2", tags=["addition"])
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)

    resp = client.get("/api/questions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["content"] == "1+1=?"


def test_filter_questions(client, db_session):
    db_session.add(Question(subject="math", grade=1, difficulty=1, content="q1", options=["a"], answer="a"))
    db_session.add(Question(subject="english", grade=2, difficulty=2, content="q2", options=["a"], answer="a"))
    db_session.add(Question(subject="math", grade=2, difficulty=3, content="q3", options=["a"], answer="a"))
    db_session.commit()

    resp = client.get("/api/questions?subject=math")
    assert len(resp.json()) == 2

    resp = client.get("/api/questions?grade=2")
    assert len(resp.json()) == 2

    resp = client.get("/api/questions?difficulty=3")
    assert len(resp.json()) == 1


def test_get_next_question(client, device_headers, child_id, db_session):
    q = Question(subject="math", grade=1, difficulty=2, type="choice",
                content="3+4=?", options=["5", "6", "7", "8"], answer="7")
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)

    resp = client.post("/api/questions/next", json={"subject": "math"}, headers=device_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data is not None
    assert data["content"] == "3+4=?"
    assert "answer" not in data


def test_submit_answer_correct(client, device_headers, child_id, db_session):
    """Server should determine correctness from selected_answer."""
    q = Question(subject="math", grade=1, difficulty=1, type="choice",
                 content="2+2=?", options=["3", "4", "5", "6"], answer="4",
                 explanation="2+2=4")
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)

    resp = client.post("/api/questions/answer", json={
        "question_id": q.id,
        "selected_answer": "4",
        "time_taken_sec": 5.0,
    }, headers=device_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_correct"] is True
    assert data["correct_answer"] == "4"


def test_submit_answer_wrong(client, device_headers, child_id, db_session):
    q = Question(subject="math", grade=1, difficulty=1, type="choice",
                 content="5+5=?", options=["8", "9", "10", "11"], answer="10")
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)

    resp = client.post("/api/questions/answer", json={
        "question_id": q.id,
        "selected_answer": "9",
        "time_taken_sec": 20.0,
    }, headers=device_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_correct"] is False
    assert data["correct_answer"] == "10"


def test_submit_answer_nonexistent_question(client, device_headers, child_id):
    resp = client.post("/api/questions/answer", json={
        "question_id": 9999,
        "selected_answer": "42",
    }, headers=device_headers)
    assert resp.status_code == 404


def test_next_question_no_auth(client):
    resp = client.post("/api/questions/next", json={"subject": "math"})
    assert resp.status_code == 401


def test_answer_no_auth(client):
    resp = client.post("/api/questions/answer", json={
        "question_id": 1,
        "selected_answer": "42",
    })
    assert resp.status_code == 401
