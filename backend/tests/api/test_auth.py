from fastapi.testclient import TestClient

def test_login_success(client: TestClient, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser@example.com", "password": "StrongP@ss1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure_wrong_password(client: TestClient, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_brute_force_lockout(client: TestClient, test_user):
    # Attempt 5 wrong logins
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        
    # The 6th attempt should fail with the lockout message, even with correct password
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser@example.com", "password": "StrongP@ss1"}
    )
    assert response.status_code == 401
    assert "locked" in response.json()["detail"].lower()

def test_refresh_token_success(client: TestClient, test_user):
    # 1. Login to get refresh token
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser@example.com", "password": "StrongP@ss1"}
    )
    refresh_token = login_resp.json()["refresh_token"]
    
    # 2. Refresh token
    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()

def test_refresh_token_reuse_detection(client: TestClient, test_user):
    # 1. Login to get refresh token
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser@example.com", "password": "StrongP@ss1"}
    )
    refresh_token = login_resp.json()["refresh_token"]
    
    # 2. Refresh token successfully (this revokes the old refresh token)
    client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    # 3. Attempt to use the OLD refresh token again -> should trigger reuse detection
    reuse_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert reuse_resp.status_code == 401
    assert "reuse" in reuse_resp.json()["detail"].lower()
    
    # 4. Check if sessions were actually wiped via /sessions endpoint
    # (assuming we can get a new login to check)
    login_resp2 = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser@example.com", "password": "StrongP@ss1"}
    )
    access_token2 = login_resp2.json()["access_token"]
    
    sessions_resp = client.get(
        "/api/v1/auth/sessions",
        headers={"Authorization": f"Bearer {access_token2}"}
    )
    assert sessions_resp.status_code == 200
    # Should only have 1 active session (the one we just created) because all prior ones were revoked
    assert len(sessions_resp.json()) == 1
