import pytest
from fastapi.testclient import TestClient

def test_rate_limiting(client: TestClient):
    from app.api.v1.router import RATE_LIMIT_STORE
    RATE_LIMIT_STORE.clear()
    # Anonymous client is allowed 10 searches per minute
    # Make 10 requests successfully, then the 11th should be rate-limited
    for i in range(10):
        res = client.post("/api/v1/search", json={"query": "27ABCDE1234F1Z5"})
        assert res.status_code == 200

    # 11th request triggers rate limit
    res_blocked = client.post("/api/v1/search", json={"query": "27ABCDE1234F1Z5"})
    assert res_blocked.status_code == 429
    detail = res_blocked.json()["detail"]
    assert detail["code"] == "SOURCE_RATE_LIMITED"

def test_sql_injection_resilience(client: TestClient):
    sqli_payload = "' OR '1'='1' --"
    res = client.post("/api/v1/search", json={"query": sqli_payload})
    # Should safely return 200 with UNRESOLVED or 429 without database error or 500
    assert res.status_code in [200, 429]

def test_xss_payload_resilience(client: TestClient):
    xss_payload = "<script>alert('xss')</script>"
    res = client.post("/api/v1/search", json={"query": xss_payload})
    assert res.status_code in [200, 429]
