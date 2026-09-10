"""
Automated Integration Tests: FastAPI Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"

def test_current_index_endpoint():
    resp = client.get("/api/index/current")
    assert resp.status_code == 200
    data = resp.json()
    assert "apix_value" in data
    assert "daily_change_pct" in data
    assert "average_domestic_fare" in data

def test_daily_index_endpoint():
    resp = client.get("/api/index/daily")
    assert resp.status_code == 200
    data = resp.json()
    assert data["frequency"] == "DAILY"
    assert len(data["points"]) > 0

def test_fares_endpoint():
    resp = client.get("/api/fares?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert "fares" in data
    assert len(data["fares"]) <= 5

def test_routes_endpoint():
    resp = client.get("/api/routes")
    assert resp.status_code == 200
    routes = resp.json()
    assert len(routes) >= 20

def test_lead_time_elasticity_endpoint():
    resp = client.get("/api/analytics/lead-time")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    assert data[0]["window_label"] in ["T+45", "T+1"]

def test_cpi_augmentation_endpoint():
    resp = client.get("/api/cpi-augmentation")
    assert resp.status_code == 200
    data = resp.json()
    assert "comparison_matrix" in data
    assert len(data["comparison_matrix"]) >= 5

def test_scraper_status_endpoint():
    resp = client.get("/api/scraper/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_sources"] == 11
