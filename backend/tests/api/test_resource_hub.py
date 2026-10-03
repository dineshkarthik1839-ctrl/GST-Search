import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestResourceHubAndExamCalendar:
    def test_search_resource_library(self):
        res = client.get("/api/v1/content/library?page=1&page_size=10")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data

    def test_save_and_get_continue_learning(self):
        # 1. Fetch library items to get a valid item id
        lib_res = client.get("/api/v1/content/library")
        assert lib_res.status_code == 200
        items = lib_res.json()["items"]
        assert len(items) > 0
        item_id = items[0]["id"]

        # 2. Save progress
        prog_res = client.post(f"/api/v1/content/library/{item_id}/progress?last_page_read=15&completion_pct=30.0")
        assert prog_res.status_code == 200
        assert prog_res.json()["status"] == "SUCCESS"

        # 3. Get continue learning list
        cont_res = client.get("/api/v1/content/library/continue-learning")
        assert cont_res.status_code == 200
        cont_items = cont_res.json()
        assert len(cont_items) > 0

    def test_track_resource_download(self):
        lib_res = client.get("/api/v1/content/library")
        item_id = lib_res.json()["items"][0]["id"]

        dl_res = client.post(f"/api/v1/content/library/{item_id}/download")
        assert dl_res.status_code == 200
        assert dl_res.json()["status"] == "DOWNLOADED"

    def test_resource_ai_chat(self):
        lib_res = client.get("/api/v1/content/library")
        item_id = lib_res.json()["items"][0]["id"]

        ai_res = client.post(f"/api/v1/content/library/{item_id}/ai-chat?query=Explain chapter 1 trick")
        assert ai_res.status_code == 200
        data = ai_res.json()
        assert "ai_response" in data
        assert "grounded_resource_title" in data

    def test_list_exam_notifications(self):
        res = client.get("/api/v1/engagement/exam-notifications")
        assert res.status_code == 200
        items = res.json()
        assert len(items) >= 2
        assert "official_pdf_url" in items[0]

    def test_get_exam_calendar(self):
        res = client.get("/api/v1/engagement/exam-calendar")
        assert res.status_code == 200
        events = res.json()
        assert len(events) >= 2
        assert "event_type" in events[0]
