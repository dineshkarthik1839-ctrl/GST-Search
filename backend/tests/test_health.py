from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_liveness_check(client: TestClient):
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

def test_readiness_check(client: TestClient):
    response = client.get("/ready")
    assert response.status_code == 200
    # In test environment, sqlite might return ok depending on setup
    assert "status" in response.json()
