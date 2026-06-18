"""V4 feature tests: gamification, offline sync, forum, i18n."""
import pytest
from app.models.question import Question
from app.models.answer_record import AnswerRecord
from app.models.gamification import Achievement, ChildPet, DailyStreak
from app.models.forum import ForumPost, ForumReply


# ─── Gamification ───

class TestGamification:
    def test_get_achievements(self, client, device_headers):
        """Child can list all achievements (with unlocked status)."""
        resp = client.get("/api/game/achievements", headers=device_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 11  # 11 predefined achievements
        assert "code" in data[0]
        assert "unlocked" in data[0]

    def test_get_pet_auto_create(self, client, device_headers):
        """Pet auto-created on first access."""
        resp = client.get("/api/game/pet", headers=device_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["pet_type"] == "cat"
        assert data["level"] == 1
        assert data["exp"] == 0
        assert data["happiness"] == 100

    def test_feed_pet(self, client, device_headers):
        """Feed pet increases hunger + happiness."""
        # Get pet first
        pet = client.get("/api/game/pet", headers=device_headers).json()
        resp = client.post("/api/game/pet/feed", json={"pet_id": pet["id"]}, headers=device_headers)
        assert resp.status_code == 200
        assert pet["hunger"] <= resp.json()["hunger"]

    def test_get_streak(self, client, device_headers):
        """Get current streak (0 if first time)."""
        resp = client.get("/api/game/streak", headers=device_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "current_streak" in data
        assert isinstance(data["current_streak"], int)
        assert "history" in data

    def test_achievement_unlocked_after_answer(self, client, device_headers, db_session):
        """After answering first question, 'first_answer' achievement should unlock."""
        # Add a question
        q = Question(
            subject="math", grade=1, difficulty=1, type="choice",
            content="1+1=?", options=["1", "2", "3"], answer="2",
            explanation="1+1=2", status="approved",
        )
        db_session.add(q)
        db_session.commit()
        db_session.refresh(q)

        # Answer it
        resp = client.post("/api/questions/answer", json={
            "question_id": q.id,
            "selected_answer": "2",
            "time_taken_sec": 5.0,
        }, headers=device_headers)
        assert resp.status_code == 200

        # Check achievements
        ach_resp = client.get("/api/game/achievements", headers=device_headers)
        unlocked = [a for a in ach_resp.json() if a["unlocked"]]
        codes = [a["code"] for a in unlocked]
        assert "first_answer" in codes

    def test_get_all_pets(self, client, device_headers):
        """List all pets."""
        # Create starter pet first
        client.get("/api/game/pet", headers=device_headers)
        resp = client.get("/api/game/pets", headers=device_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_game_no_auth(self, client):
        """Cannot access game endpoints without device token."""
        resp = client.get("/api/game/pet")
        assert resp.status_code == 401


# ─── Offline Sync ───

class TestOfflineSync:
    def test_sync_batch(self, client, device_headers, db_session):
        """Batch upload offline answers."""
        # Add questions
        qs = []
        for i in range(3):
            q = Question(
                subject="math", grade=1, difficulty=1, type="choice",
                content=f"sync q{i}", options=["a", "b"], answer="a",
                explanation="", status="approved",
            )
            db_session.add(q)
            qs.append(q)
        db_session.commit()
        for q in qs:
            db_session.refresh(q)

        resp = client.post("/api/sync/answers", json={
            "device_uuid": "test-device",
            "answers": [
                {"question_id": qs[0].id, "selected_answer": "a", "time_taken_sec": 5.0},
                {"question_id": qs[1].id, "selected_answer": "b", "time_taken_sec": 8.0},
                {"question_id": qs[2].id, "selected_answer": "a", "time_taken_sec": 3.0},
            ],
        }, headers=device_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] == 3
        assert data["rejected"] == 0
        assert data["batch_id"]  # UUID string

    def test_sync_dedup(self, client, device_headers, db_session):
        """Duplicate answers are rejected."""
        q = Question(
            subject="math", grade=1, difficulty=1, type="choice",
            content="dedup q", options=["a", "b"], answer="a",
            explanation="", status="approved",
        )
        db_session.add(q)
        db_session.commit()
        db_session.refresh(q)

        ts = "2025-01-01T12:00:00Z"
        # First upload
        resp1 = client.post("/api/sync/answers", json={
            "answers": [{"question_id": q.id, "selected_answer": "a", "answered_at": ts}],
        }, headers=device_headers)
        assert resp1.json()["accepted"] == 1

        # Second upload — same timestamp = duplicate
        resp2 = client.post("/api/sync/answers", json={
            "answers": [{"question_id": q.id, "selected_answer": "a", "answered_at": ts}],
        }, headers=device_headers)
        assert resp2.json()["rejected"] == 1

    def test_sync_status(self, client, device_headers):
        """Get sync history."""
        resp = client.get("/api/sync/status", headers=device_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_sync_no_auth(self, client):
        resp = client.post("/api/sync/answers", json={"answers": []})
        assert resp.status_code == 401


# ─── Forum ───

class TestForum:
    def test_create_post(self, client, auth_headers):
        resp = client.post("/api/forum/posts", json={
            "title": "分享：孩子數學進步了！",
            "content": "這週每天練習，孩子的加法正確率從 50% 提升到 80%！",
            "category": "分享",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "分享：孩子數學進步了！"

    def test_list_posts(self, client, auth_headers):
        client.post("/api/forum/posts", json={
            "title": "問題：如何提升專注力？",
            "content": "孩子做題時很容易分心，有什麼好方法嗎？",
            "category": "提問",
        }, headers=auth_headers)
        resp = client.get("/api/forum/posts", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_post_detail(self, client, auth_headers):
        create = client.post("/api/forum/posts", json={
            "title": "資源：推薦數學繪本",
            "content": "《數學冒險島》系列很適合小一生。",
            "category": "資源",
        }, headers=auth_headers)
        post_id = create.json()["id"]
        resp = client.get(f"/api/forum/posts/{post_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "資源：推薦數學繪本"

    def test_create_reply(self, client, auth_headers):
        create = client.post("/api/forum/posts", json={
            "title": "討論",
            "content": "test post for reply",
            "category": "分享",
        }, headers=auth_headers)
        post_id = create.json()["id"]

        resp = client.post(f"/api/forum/posts/{post_id}/replies", json={
            "content": "很有幫助！謝謝分享。",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["content"] == "很有幫助！謝謝分享。"

    def test_list_replies(self, client, auth_headers):
        create = client.post("/api/forum/posts", json={
            "title": "test replies",
            "content": "content here",
            "category": "分享",
        }, headers=auth_headers)
        post_id = create.json()["id"]
        client.post(f"/api/forum/posts/{post_id}/replies", json={"content": "reply 1"}, headers=auth_headers)
        client.post(f"/api/forum/posts/{post_id}/replies", json={"content": "reply 2"}, headers=auth_headers)

        resp = client.get(f"/api/forum/posts/{post_id}/replies", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_delete_own_post(self, client, auth_headers):
        create = client.post("/api/forum/posts", json={
            "title": "to delete",
            "content": "bye bye",
            "category": "分享",
        }, headers=auth_headers)
        post_id = create.json()["id"]
        resp = client.delete(f"/api/forum/posts/{post_id}", headers=auth_headers)
        assert resp.status_code == 200

    def test_delete_other_post_forbidden(self, client, db_session):
        """Cannot delete another parent's post."""
        from app.models.parent import Parent
        from app.services.auth_service import hash_password
        p = Parent(email="other@test.com", password_hash=hash_password("123456"))
        db_session.add(p)
        db_session.commit()
        post = ForumPost(parent_id=p.id, parent_name="other", title="other", content="content")
        db_session.add(post)
        db_session.commit()

        # Login as original parent
        client.post("/api/auth/register", json={"email": "me@test.com", "password": "123456"})
        login = client.post("/api/auth/login", json={"email": "me@test.com", "password": "123456"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        resp = client.delete(f"/api/forum/posts/{post.id}", headers=headers)
        assert resp.status_code == 403

    def test_forum_no_auth(self, client):
        resp = client.get("/api/forum/posts")
        assert resp.status_code == 401


# ─── i18n (language filter) ───

class TestI18n:
    def test_list_questions_by_language(self, client, db_session):
        """Questions can be filtered by language."""
        db_session.add(Question(
            subject="math", grade=1, difficulty=1, type="choice",
            content="zh question", options=["a"], answer="a",
            status="approved", language="zh-TW",
        ))
        db_session.add(Question(
            subject="math", grade=1, difficulty=1, type="choice",
            content="en question", options=["a"], answer="a",
            status="approved", language="en-US",
        ))
        db_session.commit()

        resp_zh = client.get("/api/questions?language=zh-TW")
        assert resp_zh.status_code == 200
        assert all(q["content"] == "zh question" for q in resp_zh.json() if q["content"] in ("zh question", "en question"))

        resp_en = client.get("/api/questions?language=en-US")
        assert resp_en.status_code == 200
