"""
Unit Tests for Text Extractor and Regex Normalizer
"""

import os
import pytest
from backend.app.extractors.text_extractor import TextExtractor
from backend.app.extractors.regex_normalizer import RegexNormalizer
from backend.app.extractors.pipeline import UniversalResumePipeline


SAMPLE_RAW_TEXT = """William Free Hall | Lead Cloud & DevOps Engineer
free@example.com | (555) 019-2834 | Niceville, FL 32578
https://linkedin.com/in/williamfreehall | https://github.com/FreeFades2Black

SUMMARY
Senior Cloud & DevOps Engineer with 6+ years of experience engineering high-scale multi-cloud architectures.

SKILLS
Python, AWS, Terraform, Docker, Kubernetes, Databricks, PySpark, FastAPI, SQL, Linux, Git

WORK EXPERIENCE
Lead Cloud Engineer at Tech Solutions Inc.
2024 - Present | Remote / Florida
- Architected enterprise multi-cloud infrastructure spanning AWS and Databricks.
- Engineered automated CI/CD pipelines with GitHub Actions.

EDUCATION
University of Florida
Bachelor of Science in Computer Science
2017 - 2021 | GPA: 3.85

CERTIFICATIONS
- AWS Certified Solutions Architect (2024)
"""


def test_text_extractor_plaintext():
    text = TextExtractor.extract(SAMPLE_RAW_TEXT)
    assert "William Free Hall" in text
    assert "free@example.com" in text


def test_text_extractor_pdf():
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "samples", "sample_resume_cloud_engineer.pdf")
    if os.path.exists(pdf_path):
        text = TextExtractor.extract(pdf_path)
        assert len(text) > 50
        assert "William" in text or "Cloud" in text or "free@example.com" in text


def test_regex_normalizer_personal_info():
    payload = RegexNormalizer.normalize(SAMPLE_RAW_TEXT)
    info = payload.personal_information
    
    assert info.first_name == "William"
    assert info.last_name == "Free Hall" or "Hall" in info.last_name
    assert info.email == "free@example.com"
    assert "555-019-2834" in info.phone or "555" in info.phone
    assert info.city == "Niceville"
    assert info.state == "FL"
    assert "linkedin.com/in/williamfreehall" in info.linkedin_url
    assert "github.com/FreeFades2Black" in info.github_url


def test_regex_normalizer_skills():
    payload = RegexNormalizer.normalize(SAMPLE_RAW_TEXT)
    assert "Python" in payload.skills
    assert "AWS" in payload.skills
    assert "Terraform" in payload.skills
    assert "Kubernetes" in payload.skills
    assert "Databricks" in payload.skills


def test_regex_normalizer_work_history():
    payload = RegexNormalizer.normalize(SAMPLE_RAW_TEXT)
    assert len(payload.work_history) >= 1
    job = payload.work_history[0]
    assert "Tech Solutions" in job.company or "Lead Cloud" in job.title
    assert "2024" in job.start_date


def test_regex_normalizer_education():
    payload = RegexNormalizer.normalize(SAMPLE_RAW_TEXT)
    assert len(payload.education) >= 1
    edu = payload.education[0]
    assert "University of Florida" in edu.institution
    assert "Bachelor" in edu.degree


def test_pipeline_orchestrator():
    pipeline = UniversalResumePipeline(prefer_llm=False)
    payload = pipeline.process(SAMPLE_RAW_TEXT, filename="sample.txt")
    assert payload.schema_version == "1.0.0"
    assert payload.personal_information.email == "free@example.com"
    assert payload.metadata["engine_used"] == "regex_normalizer"
    assert "parsing_duration_ms" in payload.metadata
