"""
Unit Tests for Universal Resume Pydantic Schema
"""

import json
from backend.app.models.schema import (
    UniversalResumePayload,
    PersonalInformation,
    WorkExperience,
    Education,
    Certification,
    Project,
    ApplicationPreferences
)


def test_schema_defaults():
    payload = UniversalResumePayload()
    assert payload.schema_version == "1.0.0"
    assert payload.personal_information.country == "United States"
    assert payload.preferences.authorized_to_work == "Yes"
    assert payload.preferences.requires_sponsorship == "No"
    assert isinstance(payload.work_history, list)
    assert isinstance(payload.education, list)
    assert isinstance(payload.skills, list)


def test_schema_serialization():
    payload = UniversalResumePayload(
        personal_information=PersonalInformation(
            first_name="William",
            last_name="Hall",
            email="free@example.com",
            phone="555-019-2834"
        ),
        skills=["Python", "AWS", "Terraform"]
    )
    
    json_str = payload.model_dump_json()
    data = json.loads(json_str)
    
    assert data["personal_information"]["first_name"] == "William"
    assert data["personal_information"]["email"] == "free@example.com"
    assert data["skills"] == ["Python", "AWS", "Terraform"]


def test_schema_deserialization():
    raw_dict = {
        "schema_version": "1.0.0",
        "personal_information": {
            "first_name": "William",
            "last_name": "Hall",
            "email": "free@example.com"
        },
        "work_history": [
            {
                "title": "Cloud Architect",
                "company": "Tech Solutions",
                "start_date": "2024",
                "end_date": "Present",
                "is_current": True
            }
        ],
        "skills": ["Databricks", "Docker"]
    }
    
    payload = UniversalResumePayload(**raw_dict)
    assert payload.personal_information.first_name == "William"
    assert len(payload.work_history) == 1
    assert payload.work_history[0].title == "Cloud Architect"
    assert payload.work_history[0].is_current is True
