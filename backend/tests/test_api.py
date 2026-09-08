import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["methodology_version"] == "APIX_v1"

def test_api_routes():
    response = client.get("/api/routes")
    assert response.status_code == 200
    routes = response.json()
    assert isinstance(routes, list)
    assert len(routes) >= 10

def test_api_carriers():
    response = client.get("/api/carriers")
    assert response.status_code == 200
    carriers = response.json()
    assert isinstance(carriers, list)

def test_api_fares_pagination_and_filter():
    response = client.get("/api/fares?route=DEL-BOM&page=1&size=10")
    assert response.status_code == 200
    res = response.json()
    assert "data" in res
    assert res["page"] == 1

def test_api_index_summary():
    response = client.get("/api/index")
    assert response.status_code == 200
    summary = response.json()
    assert "national_apix" in summary
    assert "latest_date" in summary

def test_api_analytics_lead_time():
    response = client.get("/api/analytics/lead-time")
    assert response.status_code == 200
    lead_data = response.json()
    assert isinstance(lead_data, list)

def test_api_data_quality():
    response = client.get("/api/data-quality")
    assert response.status_code == 200
    q_data = response.json()
    assert "average_quality_score" in q_data
