"""
Integration Tests for FastAPI Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["docs"] == "/docs"


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_schema_endpoint():
    response = client.get("/api/v1/schema")
    assert response.status_code == 200
    data = response.json()
    assert "properties" in data
    assert "personal_information" in data["properties"]


def test_parse_raw_text_form():
    sample_text = "William Free Hall | free@example.com | 555-019-2834 | Python, AWS, Terraform"
    response = client.post(
        "/api/v1/parse",
        data={"raw_text": sample_text, "prefer_llm": "false"}
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["personal_information"]["email"] == "free@example.com"
    assert "Python" in payload["skills"]


def test_parse_json_body():
    sample_text = "William Free Hall | free@example.com | 555-019-2834 | Python, AWS, Terraform"
    response = client.post(
        "/api/v1/parse/json",
        json={"raw_text": sample_text, "prefer_llm": False}
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["personal_information"]["email"] == "free@example.com"
    assert "AWS" in payload["skills"]


def test_match_selectors_endpoint():
    sample_payload = {
        "schema_version": "1.0.0",
        "personal_information": {
            "first_name": "William",
            "last_name": "Hall",
            "full_name": "William Free Hall",
            "email": "free@example.com",
            "phone": "555-019-2834",
            "linkedin_url": "https://linkedin.com/in/williamfreehall"
        },
        "skills": ["Python", "AWS"]
    }
    response = client.post("/api/v1/match-selectors", json=sample_payload)
    assert response.status_code == 200
    data = response.json()
    assert "ats_profiles" in data
    assert "greenhouse" in data["ats_profiles"]
    assert "lever" in data["ats_profiles"]
    assert data["ats_profiles"]["greenhouse"]["first_name"]["value"] == "William"
