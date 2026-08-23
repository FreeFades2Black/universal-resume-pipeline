"""
Tests for Universal Resume CLI
"""

import os
import sys
import subprocess
import json
import tempfile


def test_cli_execution_with_file():
    sample_file = os.path.join(os.path.dirname(__file__), "..", "samples", "sample_resume_software_engineer.txt")
    
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        cmd = [
            sys.executable,
            "-m", "cli.resume_pipeline_cli",
            sample_file,
            "-o", tmp_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), ".."))
        assert res.returncode == 0
        assert "[SUCCESS] Normalized resume" in res.stdout

        with open(tmp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["personal_information"]["email"] == "free@example.com"
            assert "Python" in data["skills"]
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_cli_execution_with_string():
    raw_str = "William Free Hall | free@example.com | 555-019-2834 | Python, AWS"
    cmd = [
        sys.executable,
        "-m", "cli.resume_pipeline_cli",
        raw_str,
        "--compact"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), ".."))
    assert res.returncode == 0
    assert "free@example.com" in res.stdout
