import uuid
import pytest
from fastapi.testclient import TestClient

from app.modules.assessment.models import Question, QuestionOption, MockTest, MockTestQuestion, QuestionStatus, QuestionType, DifficultyLevel
from app.modules.academic.models import Exam


@pytest.fixture(scope="function")
def sample_exam(db):
    exam = db.query(Exam).first()
    if not exam:
        exam = Exam(name="TS Police Constable Test Exam", code="TSPC2026")
        db.add(exam)
        db.commit()
        db.refresh(exam)
    return exam


@pytest.fixture(scope="function")
def sample_mock_test(db, sample_exam):
    q = Question(
        content="What is the capital of Telangana?",
        question_type=QuestionType.MCQ,
        difficulty=DifficultyLevel.EASY,
        status=QuestionStatus.PUBLISHED,
    )
    db.add(q)
    db.flush()

    opt1 = QuestionOption(question_id=q.id, content="Hyderabad", option_index=1, is_correct=True)
    opt2 = QuestionOption(question_id=q.id, content="Warangal", option_index=2, is_correct=False)
    db.add_all([opt1, opt2])
    db.flush()

    mt = MockTest(
        exam_id=sample_exam.id,
        title="Test Mock Test Suite",
        duration_minutes=60,
        total_marks=2.0
    )
    db.add(mt)
    db.flush()

    mtq = MockTestQuestion(mock_test_id=mt.id, question_id=q.id, marks=2.0, negative_marks=0.5)
    db.add(mtq)
    db.commit()
    return mt


class TestAssessmentPlatform:
    def test_start_practice_session(self, client: TestClient):
        resp = client.post("/api/v1/questions/practice/start", json={
            "mode": "PRACTICE",
            "num_questions": 5
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "IN_PROGRESS"
        assert "id" in data
        assert len(data["attempt_questions"]) > 0

    def test_start_and_submit_mock_test(self, client: TestClient, sample_mock_test):
        # 1. Start mock test
        start_resp = client.post(f"/api/v1/questions/tests/{sample_mock_test.id}/start")
        assert start_resp.status_code == 200
        attempt = start_resp.json()
        attempt_id = attempt["id"]
        aq = attempt["attempt_questions"][0]
        q_id = aq["question_id"]

        # Fetch option ID
        q_resp = client.get(f"/api/v1/questions/{q_id}")
        assert q_resp.status_code == 200
        correct_opt_id = [opt["id"] for opt in q_resp.json()["options"] if opt["is_correct"]][0]

        # 2. Save Answer
        ans_resp = client.post(f"/api/v1/questions/attempts/{attempt_id}/questions/{q_id}/answer", json={
            "selected_option_id": correct_opt_id,
            "status": "ANSWERED",
            "time_spent_seconds": 25
        })
        assert ans_resp.status_code == 200

        # 3. Submit Attempt
        sub_resp = client.post(f"/api/v1/questions/attempts/{attempt_id}/submit")
        assert sub_resp.status_code == 200
        sub_data = sub_resp.json()
        assert sub_data["status"] == "COMPLETED"
        assert sub_data["score"] > 0
        assert sub_data["accuracy_pct"] == 100.0

        # 4. Fetch Result Report
        res_resp = client.get(f"/api/v1/questions/attempts/{attempt_id}/result")
        assert res_resp.status_code == 200
        res_data = res_resp.json()
        assert res_data["score"] > 0

    def test_analytics_dashboard(self, client: TestClient):
        resp = client.get("/api/v1/questions/analytics/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert "overall_accuracy_pct" in data
        assert "learning_health_score" in data
        assert "retention_pct" in data

    def test_leaderboard(self, client: TestClient):
        resp = client.get("/api/v1/questions/analytics/leaderboard")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_unified_search(self, client: TestClient):
        resp = client.get("/api/v1/questions/search/unified", params={"q": "Hyderabad"})
        assert resp.status_code == 200
        data = resp.json()
        assert "questions" in data
        assert "exams" in data

    def test_bookmark_toggle(self, client: TestClient, sample_mock_test):
        q_id = str(sample_mock_test.questions[0].question_id)
        # Toggle ON
        resp1 = client.post("/api/v1/questions/bookmarks/toggle", json={
            "entity_type": "QUESTION",
            "entity_id": q_id
        })
        assert resp1.status_code == 200
        assert resp1.json()["bookmarked"] is True

        # Fetch Bookmarks
        list_resp = client.get("/api/v1/questions/bookmarks")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) > 0
