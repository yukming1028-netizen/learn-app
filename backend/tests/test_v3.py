"""V3 feature tests: AI question generation (admin), teacher/classroom, insights."""
import pytest
from app.models.question import Question
from app.models.admin import Admin
from app.services.auth_service import hash_password, create_access_token


# ─── Admin fixture ───

@pytest.fixture
def admin_headers(client, db_session):
    """Create an admin and return auth headers."""
    admin = Admin(
        username="testadmin",
        password_hash=hash_password("admin123"),
        display_name="測試管理員",
        is_super=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    token = create_access_token({"sub": admin.id, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}


# ─── AI Question Generation (Admin only) ───

class TestAIQuestionGeneration:
    def test_generate_math_questions(self, client, admin_headers):
        """Admin generates math questions for grade 2."""
        resp = client.post("/api/ai-questions/generate", json={
            "subject": "math",
            "grade": 2,
            "count": 5,
            "topic": "addition",
        }, headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "questions" in data
        assert len(data["questions"]) == 5
        for q in data["questions"]:
            assert q["subject"] == "math"
            assert q["grade"] == 2
            assert q["status"] == "pending"

    def test_generate_chinese_idiom(self, client, admin_headers):
        """Generate Chinese idiom questions."""
        resp = client.post("/api/ai-questions/generate", json={
            "subject": "chinese",
            "grade": 4,
            "count": 3,
            "topic": "idiom",
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert len(resp.json()["questions"]) == 3

    def test_generate_english_vocab(self, client, admin_headers):
        """Generate English vocabulary questions."""
        resp = client.post("/api/ai-questions/generate", json={
            "subject": "english",
            "grade": 3,
            "count": 4,
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert len(resp.json()["questions"]) == 4

    def test_generate_no_auth(self, client):
        """Cannot generate without admin auth."""
        resp = client.post("/api/ai-questions/generate", json={
            "subject": "math", "grade": 1, "count": 1,
        })
        assert resp.status_code == 401

    def test_generate_parent_not_allowed(self, client, auth_headers):
        """Parent cannot generate AI questions — admin only."""
        resp = client.post("/api/ai-questions/generate", json={
            "subject": "math", "grade": 1, "count": 1,
        }, headers=auth_headers)
        assert resp.status_code == 401

    def test_list_pending_questions(self, client, admin_headers, db_session):
        """Admin lists pending questions."""
        db_session.add(Question(
            subject="math", grade=1, difficulty=1, type="choice",
            content="AI q", options=["a", "b"], answer="a",
            status="pending",
        ))
        db_session.commit()
        resp = client.get("/api/admin/questions/pending", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert all(q["status"] == "pending" for q in data)

    def test_approve_question(self, client, admin_headers, db_session):
        """Admin approves a pending question."""
        q = Question(
            subject="math", grade=1, difficulty=1, type="choice",
            content="Approve me", options=["a", "b"], answer="a",
            status="pending",
        )
        db_session.add(q)
        db_session.commit()
        db_session.refresh(q)

        resp = client.post("/api/admin/questions/review", json={
            "question_ids": [q.id], "action": "approve",
        }, headers=admin_headers)
        assert resp.status_code == 200
        db_session.refresh(q)
        assert q.status == "approved"

    def test_reject_question(self, client, admin_headers, db_session):
        """Admin rejects a pending question."""
        q = Question(
            subject="math", grade=1, difficulty=1, type="choice",
            content="Reject me", options=["a", "b"], answer="a",
            status="pending",
        )
        db_session.add(q)
        db_session.commit()
        db_session.refresh(q)

        resp = client.post("/api/admin/questions/review", json={
            "question_ids": [q.id], "action": "reject",
        }, headers=admin_headers)
        assert resp.status_code == 200
        db_session.refresh(q)
        assert q.status == "rejected"

    def test_review_no_auth(self, client, db_session):
        """Cannot review without admin auth."""
        q = Question(
            subject="math", grade=1, difficulty=1, type="choice",
            content="q", options=["a"], answer="a", status="pending",
        )
        db_session.add(q)
        db_session.commit()
        resp = client.post("/api/admin/questions/review", json={
            "question_ids": [q.id], "action": "approve",
        })
        assert resp.status_code == 401

    def test_list_all_questions(self, client, admin_headers, db_session):
        """Admin lists all questions with optional filter."""
        db_session.add(Question(
            subject="math", grade=1, difficulty=1, type="choice",
            content="approved q", options=["a"], answer="a", status="approved",
        ))
        db_session.add(Question(
            subject="math", grade=1, difficulty=1, type="choice",
            content="pending q", options=["a"], answer="a", status="pending",
        ))
        db_session.commit()
        resp = client.get("/api/admin/questions/all", headers=admin_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

        resp2 = client.get("/api/admin/questions/all?status_filter=approved", headers=admin_headers)
        assert resp2.status_code == 200
        assert all(q["status"] == "approved" for q in resp2.json())

    def test_delete_question(self, client, admin_headers, db_session):
        """Admin deletes a question."""
        q = Question(
            subject="math", grade=1, difficulty=1, type="choice",
            content="delete me", options=["a"], answer="a", status="pending",
        )
        db_session.add(q)
        db_session.commit()
        db_session.refresh(q)
        resp = client.delete(f"/api/admin/questions/{q.id}", headers=admin_headers)
        assert resp.status_code == 200


# ─── Admin Login ───

class TestAdminAuth:
    def test_admin_login(self, client, db_session):
        db_session.add(Admin(
            username="loginadmin",
            password_hash=hash_password("pass123"),
            display_name="登入測試",
        ))
        db_session.commit()
        resp = client.post("/api/admin/login", json={
            "username": "loginadmin",
            "password": "pass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["admin"]["username"] == "loginadmin"

    def test_admin_login_wrong_password(self, client, db_session):
        db_session.add(Admin(
            username="wrongadmin",
            password_hash=hash_password("correct"),
            display_name="錯誤測試",
        ))
        db_session.commit()
        resp = client.post("/api/admin/login", json={
            "username": "wrongadmin",
            "password": "wrong",
        })
        assert resp.status_code == 401

    def test_admin_me(self, client, admin_headers):
        resp = client.get("/api/admin/me", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == "testadmin"


# ─── Teacher / Classroom ───

class TestTeacher:
    def test_teacher_register(self, client):
        resp = client.post("/api/teacher/register", json={
            "email": "teacher@test.com",
            "password": "teacher123",
            "name": "陳老師",
            "school": "測試小學",
        })
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["teacher"]["name"] == "陳老師"

    def test_teacher_login(self, client):
        client.post("/api/teacher/register", json={
            "email": "teacher2@test.com",
            "password": "teacher123",
            "name": "李老師",
            "school": "測試小學",
        })
        resp = client.post("/api/teacher/login", json={
            "email": "teacher2@test.com",
            "password": "teacher123",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_create_classroom(self, client):
        reg = client.post("/api/teacher/register", json={
            "email": "t3@test.com", "password": "123456",
            "name": "王老師", "school": "小學",
        })
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.post("/api/teacher/classrooms", json={
            "name": "三年甲班",
            "grade": 3,
            "subject": "math",
        }, headers=headers)
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "三年甲班"
        assert len(data["invite_code"]) == 6

    def test_list_classrooms(self, client):
        reg = client.post("/api/teacher/register", json={
            "email": "t4@test.com", "password": "123456",
            "name": "張老師", "school": "小學",
        })
        headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
        client.post("/api/teacher/classrooms", json={
            "name": "一年甲班", "grade": 1, "subject": "chinese",
        }, headers=headers)

        resp = client.get("/api/teacher/classrooms", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_create_assignment(self, client, db_session):
        reg = client.post("/api/teacher/register", json={
            "email": "t5@test.com", "password": "123456",
            "name": "劉老師", "school": "小學",
        })
        headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
        cr = client.post("/api/teacher/classrooms", json={
            "name": "五年甲班", "grade": 5, "subject": "math",
        }, headers=headers)
        cr_id = cr.json()["id"]

        for i in range(3):
            db_session.add(Question(
                subject="math", grade=5, difficulty=2, type="choice",
                content=f"Q{i}", options=["a", "b"], answer="a",
                status="approved",
            ))
        db_session.commit()
        qids = [q.id for q in db_session.query(Question).filter(Question.status == "approved").all()]

        resp = client.post("/api/teacher/assignments", json={
            "classroom_id": cr_id,
            "title": "數學作業一",
            "question_ids": qids[:2],
        }, headers=headers)
        assert resp.status_code in (200, 201)
        assert resp.json()["title"] == "數學作業一"

    def test_teacher_no_auth(self, client):
        resp = client.get("/api/teacher/classrooms")
        assert resp.status_code == 401


# ─── Insights ───

class TestInsights:
    def test_platform_insights(self, client, auth_headers):
        resp = client.get("/api/insights/overview", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_questions" in data
        assert "total_answers" in data

    def test_heatmap(self, client, auth_headers):
        resp = client.get("/api/insights/heatmap?days=7", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_topic_wrong_rate(self, client, auth_headers):
        resp = client.get("/api/insights/heatmap?days=30", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
