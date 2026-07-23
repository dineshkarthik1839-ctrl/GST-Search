import uuid
import pytest
from fastapi.testclient import TestClient

from app.modules.users.models import User, Role
from app.modules.assessment.models import Question, QuestionOption, QuestionStatus, QuestionType, DifficultyLevel, BloomTaxonomy
from app.core.security import get_password_hash


@pytest.fixture(scope="function")
def admin_user(db):
    from app.modules.users.models import Role
    from sqlalchemy import select

    role = db.execute(select(Role).filter(Role.name == "Super Admin")).scalar_one_or_none()
    if not role:
        role = Role(name="Super Admin", description="All permissions")
        db.add(role)
        db.flush()

    unique_email = f"question_admin_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        password_hash=get_password_hash("Admin@123!"),
        full_name="Question Admin",
        is_active=True,
    )
    user.roles.append(role)
    db.add(user)
    db.commit()
    return user


@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    resp = client.post("/api/v1/auth/login", data={
        "username": admin_user.email,
        "password": "Admin@123!",
    })
    if resp.status_code == 200:
        return resp.json().get("access_token", "")
    return ""


@pytest.fixture(scope="function")
def admin_hdrs(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="function")
def sample_draft_question(db, admin_user):
    q = Question(
        content="What is the chemical formula of Water?",
        question_type=QuestionType.MCQ,
        difficulty=DifficultyLevel.EASY,
        bloom_taxonomy=BloomTaxonomy.REMEMBER,
        status=QuestionStatus.DRAFT,
        author_id=admin_user.id,
        explanation="Water is composed of hydrogen and oxygen.",
    )
    db.add(q)
    db.flush()

    opt1 = QuestionOption(question_id=q.id, content="H2O", option_index=1, is_correct=True)
    opt2 = QuestionOption(question_id=q.id, content="CO2", option_index=2, is_correct=False)
    db.add_all([opt1, opt2])
    db.commit()
    return q


@pytest.fixture(scope="function")
def sample_published_question(db, admin_user):
    q = Question(
        content="Which planet is known as the Red Planet?",
        question_type=QuestionType.MCQ,
        difficulty=DifficultyLevel.EASY,
        bloom_taxonomy=BloomTaxonomy.REMEMBER,
        status=QuestionStatus.PUBLISHED,
        author_id=admin_user.id,
        explanation="Mars appears red due to iron oxide on its surface.",
    )
    db.add(q)
    db.flush()

    opt1 = QuestionOption(question_id=q.id, content="Mars", option_index=1, is_correct=True)
    opt2 = QuestionOption(question_id=q.id, content="Venus", option_index=2, is_correct=False)
    db.add_all([opt1, opt2])
    db.commit()
    return q


class TestQuestionListing:
    def test_list_questions_public(self, client: TestClient):
        resp = client.get("/api/v1/questions")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    def test_list_filters_by_difficulty(self, client: TestClient, sample_published_question):
        resp = client.get("/api/v1/questions", params={"difficulty": "EASY"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_list_filters_by_bloom_taxonomy(self, client: TestClient, sample_published_question):
        resp = client.get("/api/v1/questions", params={"bloom_taxonomy": "REMEMBER"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_get_question_by_id(self, client: TestClient, sample_published_question):
        resp = client.get(f"/api/v1/questions/{sample_published_question.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == str(sample_published_question.id)
        assert len(data["options"]) == 2

    def test_get_question_not_found(self, client: TestClient):
        resp = client.get(f"/api/v1/questions/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestQuestionAuthAndDuplicate:
    def test_create_requires_auth(self, client: TestClient):
        resp = client.post("/api/v1/questions", json={
            "content": "Unauthenticated Question",
            "question_type": "MCQ"
        })
        assert resp.status_code == 401

    def test_create_question_success(self, client: TestClient, admin_hdrs):
        payload = {
            "content": f"Unique Test Question Content {uuid.uuid4().hex[:6]}",
            "question_type": "MCQ",
            "difficulty": "MEDIUM",
            "bloom_taxonomy": "APPLY",
            "explanation": "Test basic explanation",
            "detailed_explanation": "Test detailed explanation",
            "options": [
                {"content": "Option A", "option_index": 1, "is_correct": True},
                {"content": "Option B", "option_index": 2, "is_correct": False}
            ]
        }
        resp = client.post("/api/v1/questions", json=payload, headers=admin_hdrs)
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == payload["content"]
        assert data["status"] == "DRAFT"
        assert len(data["options"]) == 2

    def test_duplicate_question_rejected(self, client: TestClient, sample_draft_question, admin_hdrs):
        payload = {
            "content": sample_draft_question.content,
            "question_type": "MCQ",
            "options": [{"content": "Opt 1", "is_correct": True}]
        }
        resp = client.post("/api/v1/questions", json=payload, headers=admin_hdrs)
        assert resp.status_code == 409
        assert "Duplicate" in resp.json()["detail"]


class TestQuestionWorkflowAndVersioning:
    def test_valid_transition_draft_to_submitted(self, client: TestClient, sample_draft_question, admin_hdrs):
        resp = client.post(f"/api/v1/questions/{sample_draft_question.id}/transition", json={
            "new_status": "SUBMITTED",
            "notes": "Submitting for editorial review"
        }, headers=admin_hdrs)
        assert resp.status_code == 200
        assert resp.json()["status"] == "SUBMITTED"

    def test_invalid_transition_draft_to_published_rejected(self, client: TestClient, sample_draft_question, admin_hdrs):
        resp = client.post(f"/api/v1/questions/{sample_draft_question.id}/transition", json={
            "new_status": "PUBLISHED"
        }, headers=admin_hdrs)
        assert resp.status_code == 422

    def test_edit_published_question_blocked(self, client: TestClient, sample_published_question, admin_hdrs):
        resp = client.patch(f"/api/v1/questions/{sample_published_question.id}", json={
            "content": "Attempting illegal direct edit on published question"
        }, headers=admin_hdrs)
        assert resp.status_code == 422

    def test_spawn_draft_from_published(self, client: TestClient, sample_published_question, admin_hdrs):
        resp = client.post(f"/api/v1/questions/{sample_published_question.id}/spawn-draft", headers=admin_hdrs)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "DRAFT"
        assert data["id"] != str(sample_published_question.id)
        assert data["content"] == sample_published_question.content


class TestQuestionReportingAndBulk:
    def test_user_can_report_question(self, client: TestClient, sample_published_question):
        payload = {
            "report_type": "TYPO",
            "description": "Found a small typo in the question text."
        }
        resp = client.post(f"/api/v1/questions/{sample_published_question.id}/reports", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["report_type"] == "TYPO"

    def test_bulk_import(self, client: TestClient, admin_hdrs):
        payload = {
            "items": [
                {
                    "content": f"Bulk Question 1 {uuid.uuid4().hex[:6]}",
                    "question_type": "MCQ",
                    "options": [{"content": "A", "is_correct": True}]
                },
                {
                    "content": f"Bulk Question 2 {uuid.uuid4().hex[:6]}",
                    "question_type": "MCQ",
                    "options": [{"content": "B", "is_correct": True}]
                }
            ],
            "skip_duplicates": True
        }
        resp = client.post("/api/v1/questions/bulk/import", json=payload, headers=admin_hdrs)
        assert resp.status_code == 200
        data = resp.json()
        assert data["created"] == 2

    def test_export_csv(self, client: TestClient, admin_hdrs):
        resp = client.get("/api/v1/questions/export/csv", headers=admin_hdrs)
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")
        assert "id,content,question_type" in resp.text
