"""
Live System & API Integration Test Suite
Executes real HTTP requests against the active FastAPI backend (http://127.0.0.1:8008),
validating PDF extraction, TXT normalization, ATS selector matching, and Web testbench serving.
"""

import sys
import os
import requests
import json

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE_URL = "http://127.0.0.1:8008"
API_URL = f"{BASE_URL}/api/v1"
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "samples")


def log_step(name):
    print(f"\n>> [TEST STEP] {name}")


def assert_true(condition, msg):
    if condition:
        print(f"  [PASS] {msg}")
    else:
        print(f"  [FAIL] {msg}")
        sys.exit(1)


def main():
    print("=" * 60)
    print("RUNNING LIVE UNIVERSAL RESUME PIPELINE SYSTEM TEST")
    print(f"Target Endpoint: {BASE_URL}")
    print("=" * 60)

    # 1. Test Health Endpoint
    log_step("Testing Health Endpoint (GET /api/v1/health)")
    res = requests.get(f"{API_URL}/health")
    assert_true(res.status_code == 200, f"Status code is 200 (got {res.status_code})")
    health = res.json()
    assert_true(health.get("status") == "healthy", f"Status is healthy: {health}")

    # 2. Test Root Endpoint & OpenAPI Docs
    log_step("Testing Root & Swagger Metadata (GET /)")
    res = requests.get(f"{BASE_URL}/")
    assert_true(res.status_code == 200, "Root metadata accessible")
    assert_true(res.json().get("docs") == "/docs", "OpenAPI docs available at /docs")

    # 3. Test Schema Endpoint
    log_step("Testing Universal JSON Schema Endpoint (GET /api/v1/schema)")
    res = requests.get(f"{API_URL}/schema")
    assert_true(res.status_code == 200, "Schema returned")
    schema = res.json()
    assert_true("personal_information" in schema.get("properties", {}), "Schema defines personal_information")
    assert_true("work_history" in schema.get("properties", {}), "Schema defines work_history")

    # 4. Test PDF Resume Upload & Ingestion
    log_step("Testing Real PDF Resume Extraction (POST /api/v1/parse with sample_resume_cloud_engineer.pdf)")
    pdf_path = os.path.join(SAMPLES_DIR, "sample_resume_cloud_engineer.pdf")
    with open(pdf_path, "rb") as f:
        files = {"file": ("sample_resume_cloud_engineer.pdf", f, "application/pdf")}
        res = requests.post(f"{API_URL}/parse", files=files, data={"prefer_llm": "false"})
    assert_true(res.status_code == 200, f"PDF parsed successfully (status: {res.status_code})")
    pdf_payload = res.json()
    info = pdf_payload.get("personal_information", {})
    assert_true(info.get("first_name") == "William", f"Extracted first_name: {info.get('first_name')}")
    assert_true(info.get("email") == "free@example.com", f"Extracted email: {info.get('email')}")
    assert_true(len(pdf_payload.get("skills", [])) > 5, f"Extracted {len(pdf_payload.get('skills', []))} skills from PDF")
    print(f"     Skills sample: {pdf_payload.get('skills', [])[:6]}")

    # 5. Test TXT Resume Upload & Ingestion
    log_step("Testing TXT Resume Extraction (POST /api/v1/parse with sample_resume_software_engineer.txt)")
    txt_path = os.path.join(SAMPLES_DIR, "sample_resume_software_engineer.txt")
    with open(txt_path, "rb") as f:
        files = {"file": ("sample_resume_software_engineer.txt", f, "text/plain")}
        res = requests.post(f"{API_URL}/parse", files=files, data={"prefer_llm": "false"})
    assert_true(res.status_code == 200, f"TXT parsed successfully (status: {res.status_code})")
    txt_payload = res.json()
    assert_true(len(txt_payload.get("work_history", [])) >= 2, f"Extracted {len(txt_payload.get('work_history', []))} work experience blocks")
    first_job = txt_payload.get("work_history", [])[0]
    assert_true("Tech Solutions" in first_job.get("company", ""), f"Extracted company: {first_job.get('company')}")
    assert_true(len(first_job.get("highlights", [])) >= 1, f"Extracted {len(first_job.get('highlights', []))} nested highlight bullets")

    # 6. Test JSON Body Parsing (Extension / API Direct)
    log_step("Testing JSON Body Parse (POST /api/v1/parse/json)")
    raw_str = "William Free Hall | free@example.com | 555-019-2834 | Python, AWS, Terraform, Docker"
    res = requests.post(f"{API_URL}/parse/json", json={"raw_text": raw_str, "prefer_llm": False})
    assert_true(res.status_code == 200, "JSON body parsed successfully")
    assert_true(res.json()["personal_information"]["email"] == "free@example.com", "Email matched correctly")

    # 7. Test ATS Selector Matching Engine
    log_step("Testing ATS Selector Matching Engine (POST /api/v1/match-selectors)")
    res = requests.post(f"{API_URL}/match-selectors", json=txt_payload)
    assert_true(res.status_code == 200, "ATS Selector mapping computed successfully")
    mappings = res.json()
    assert_true("ats_profiles" in mappings, "ATS profiles returned")
    assert_true("greenhouse" in mappings["ats_profiles"], "Greenhouse profile mapped")
    assert_true("lever" in mappings["ats_profiles"], "Lever profile mapped")
    assert_true("workday" in mappings["ats_profiles"], "Workday profile mapped")
    print("     Greenhouse Email Selector:", mappings["ats_profiles"]["greenhouse"]["email"])
    print("     Lever LinkedIn Selector:", mappings["ats_profiles"]["lever"]["urls_linkedin"])

    # 8. Test Web Testbench Static Serving
    log_step("Testing Web Testbench Static Mount (GET /app/)")
    res = requests.get(f"{BASE_URL}/app/")
    assert_true(res.status_code == 200, "Web testbench HTML loaded")
    assert_true("Universal Resume" in res.text, "Web testbench title verified")

    print("\n" + "=" * 60)
    print("ALL LIVE SYSTEM INTEGRATION TESTS PASSED 100%!")
    print("=" * 60)


if __name__ == "__main__":
    main()
