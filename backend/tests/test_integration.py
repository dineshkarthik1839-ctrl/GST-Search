import pytest
from fastapi.testclient import TestClient

def test_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_search_gstin_exact_match(client: TestClient):
    # Searching GSTIN of Company 1 (ABC Technologies)
    response = client.post("/api/v1/search", json={"query": "27ABCDE1234F1Z5"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["identifierType"] == "GSTIN"
    assert data["data"]["resolution"] == "EXACT_MATCH"
    assert len(data["data"]["companies"]) == 1
    company = data["data"]["companies"][0]
    assert company["legal_name"] == "ABC TECHNOLOGIES & SOLUTIONS PRIVATE LIMITED"
    assert company["cin"] == "U72200TG2018PTC123456"
    assert len(company["gst_registrations"]) == 3

def test_search_cin_exact_match(client: TestClient):
    # Searching CIN of Company 2 (Bharat Logistics)
    response = client.post("/api/v1/search", json={"query": "U60200TN2020PTC098765"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["identifierType"] == "CIN"
    assert data["data"]["resolution"] == "EXACT_MATCH"
    company = data["data"]["companies"][0]
    assert company["legal_name"] == "BHARAT LOGISTICS & INFRATECH PRIVATE LIMITED"
    assert len(company["gst_registrations"]) == 1

def test_search_pan_exact_match(client: TestClient):
    # Searching PAN of Company 3 (Himalaya Bio-Pharma Foundation)
    response = client.post("/api/v1/search", json={"query": "AAACH5432R"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["identifierType"] == "PAN"
    assert data["data"]["resolution"] in ["EXACT_MATCH", "HIGH_CONFIDENCE"]
    company = data["data"]["companies"][0]
    assert company["legal_name"] == "HIMALAYA BIO-PHARMA RESEARCH FOUNDATION"
    assert len(company["gst_registrations"]) == 0

def test_search_company_name_fuzzy(client: TestClient):
    response = client.post("/api/v1/search", json={"query": "ABC Technologies"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["identifierType"] == "COMPANY_NAME"
    assert len(data["data"]["companies"]) >= 1

def test_company_sub_resources(client: TestClient):
    # First search to get ID
    res = client.post("/api/v1/search", json={"query": "27ABCDE1234F1Z5"})
    cid = res.json()["data"]["companies"][0]["id"]

    # 1. Overview
    overview_res = client.get(f"/api/v1/companies/{cid}/overview")
    assert overview_res.status_code == 200
    assert overview_res.json()["data"]["legal_name"] == "ABC TECHNOLOGIES & SOLUTIONS PRIVATE LIMITED"

    # 2. GST
    gst_res = client.get(f"/api/v1/companies/{cid}/gst")
    assert gst_res.status_code == 200
    assert gst_res.json()["data"]["total_count"] == 3

    # 3. Management
    mgmt_res = client.get(f"/api/v1/companies/{cid}/management")
    assert mgmt_res.status_code == 200
    assert len(mgmt_res.json()["data"]) >= 2

    # 4. Financials (Has licensed audited statements)
    fin_res = client.get(f"/api/v1/companies/{cid}/financials")
    assert fin_res.status_code == 200
    assert fin_res.json()["data"]["status"] == "AVAILABLE"
    assert len(fin_res.json()["data"]["financial_years"]) == 3

    # 5. Filings
    fil_res = client.get(f"/api/v1/companies/{cid}/filings")
    assert fil_res.status_code == 200
    assert len(fil_res.json()["data"]) >= 3

    # 6. Timeline
    time_res = client.get(f"/api/v1/companies/{cid}/timeline")
    assert time_res.status_code == 200
    assert len(time_res.json()["data"]) >= 4

    # 7. Sources
    src_res = client.get(f"/api/v1/companies/{cid}/sources")
    assert src_res.status_code == 200
    assert len(src_res.json()["data"]) == 4

def test_financials_unavailable_on_company_3(client: TestClient):
    # Company 3 has no licensed financial source
    res = client.post("/api/v1/search", json={"query": "U85100DL2022NPL543210"})
    cid = res.json()["data"]["companies"][0]["id"]

    fin_res = client.get(f"/api/v1/companies/{cid}/financials")
    assert fin_res.status_code == 200
    # Rule 24 & 68: never fake financials
    assert fin_res.json()["data"]["status"] == "FINANCIAL_DATA_UNAVAILABLE"
    assert "unavailable" in fin_res.json()["data"]["message"].lower()

def test_watchlist_and_compare(client: TestClient):
    res = client.post("/api/v1/search", json={"query": "27ABCDE1234F1Z5"})
    c1_id = res.json()["data"]["companies"][0]["id"]
    res2 = client.post("/api/v1/search", json={"query": "U60200TN2020PTC098765"})
    c2_id = res2.json()["data"]["companies"][0]["id"]

    # Add to watchlist
    wl_add = client.post(f"/api/v1/companies/{c1_id}/watchlist")
    assert wl_add.status_code == 200

    # Compare
    cmp_res = client.post("/api/v1/compare", json={"company_ids": [c1_id, c2_id]})
    assert cmp_res.status_code == 200
    assert len(cmp_res.json()["data"]) == 2

    # Remove from watchlist
    wl_del = client.delete(f"/api/v1/companies/{c1_id}/watchlist")
    assert wl_del.status_code == 200

def test_admin_source_health_and_sync(client: TestClient):
    h_res = client.get("/api/v1/admin/source-health")
    assert h_res.status_code == 200
    assert len(h_res.json()["sources"]) == 4

    sync_res = client.post("/api/v1/admin/source-sync", json={"source_name": "source-health"})
    assert sync_res.status_code == 200
    assert sync_res.json()["success"] is True
