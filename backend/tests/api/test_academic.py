from fastapi.testclient import TestClient

def test_list_exams(client: TestClient, test_user):
    # Student/Unauthenticated can access GET APIs based on RBAC? 
    # Actually GET /api/v1/academic/exams is public or needs user? In our router it doesn't have Depends(get_current_user).
    
    response = client.get("/api/v1/academic/exams")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_get_exam_not_found(client: TestClient):
    import uuid
    dummy_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/academic/exams/{dummy_id}")
    assert response.status_code == 404

def test_search_exams(client: TestClient):
    response = client.get("/api/v1/academic/exams?search=Police")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    # Since we seeded Telangana Police, we might see it here
    if data["total"] > 0:
        assert "Police" in data["items"][0]["name"]
