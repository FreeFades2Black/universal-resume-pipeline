"""
LLM-Powered Universal Resume Extractor
Uses structured JSON outputs (OpenAI, Gemini, Ollama, Anthropic) to parse complex or non-standard resumes.
Gracefully handles missing keys by logging and deferring to RegexNormalizer.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from ..models.schema import UniversalResumePayload

logger = logging.getLogger("universal_resume_pipeline.llm_parser")

EXTRACTION_SYSTEM_PROMPT = """You are an expert ATS (Applicant Tracking System) resume parser.
Your task is to convert unstructured resume text into a standard, clean JSON schema for automated job application filling.

Rules:
1. Extract first_name, last_name, email, phone, location (city, state, country, postal_code), LinkedIn URL, GitHub URL, portfolio URL.
2. Extract work_history with title, company, location, start_date (YYYY-MM or YYYY), end_date ('Present' or date), is_current, highlights, and technologies.
3. Extract education with institution, degree, field_of_study, start_date, end_date, GPA.
4. Extract skills as a clean, deduped list of strings.
5. Extract certifications and personal projects if present.
6. Return strictly valid JSON complying with the requested schema. Do not include markdown code block formatting (```json) in your direct output.
"""


class LLMParser:
    @staticmethod
    def is_available() -> bool:
        """Checks if an LLM provider API key or local endpoint is configured."""
        return bool(
            os.getenv("OPENAI_API_KEY") or
            os.getenv("GEMINI_API_KEY") or
            os.getenv("ANTHROPIC_API_KEY") or
            os.getenv("OLLAMA_HOST")
        )

    @classmethod
    def parse_with_llm(cls, raw_text: str, provider: Optional[str] = None) -> Optional[UniversalResumePayload]:
        """
        Attempts structured JSON extraction using available LLM provider.
        Returns UniversalResumePayload on success, or None on failure/unconfigured.
        """
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        ollama_host = os.getenv("OLLAMA_HOST")

        # 1. Try OpenAI
        if openai_key and (provider in [None, "openai"]):
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                        {"role": "user", "content": f"Parse this resume into the universal JSON schema:\n\n{raw_text}"}
                    ],
                    temperature=0.1
                )
                raw_json = response.choices[0].message.content
                data = json.loads(raw_json)
                data["metadata"] = {"parser_engine": "llm_openai_gpt4o_mini"}
                return UniversalResumePayload(**data)
            except Exception as e:
                logger.warning(f"OpenAI extraction failed: {e}")

        # 2. Try Gemini
        if gemini_key and (provider in [None, "gemini"]):
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"{EXTRACTION_SYSTEM_PROMPT}\n\nResume:\n{raw_text}\n\nOutput JSON:"
                response = model.generate_content(prompt)
                clean_json = response.text.strip().removeprefix("```json").removesuffix("```").strip()
                data = json.loads(clean_json)
                data["metadata"] = {"parser_engine": "llm_gemini_1.5_flash"}
                return UniversalResumePayload(**data)
            except Exception as e:
                logger.warning(f"Gemini extraction failed: {e}")

        # 3. Try Ollama (Local)
        if ollama_host and (provider in [None, "ollama"]):
            try:
                import requests
                url = f"{ollama_host.rstrip('/')}/api/generate"
                payload = {
                    "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
                    "prompt": f"{EXTRACTION_SYSTEM_PROMPT}\n\nResume:\n{raw_text}\n\nReturn ONLY JSON:",
                    "stream": False,
                    "format": "json"
                }
                res = requests.post(url, json=payload, timeout=30)
                if res.status_code == 200:
                    data = json.loads(res.json().get("response", "{}"))
                    data["metadata"] = {"parser_engine": "llm_ollama_local"}
                    return UniversalResumePayload(**data)
            except Exception as e:
                logger.warning(f"Ollama local extraction failed: {e}")

        return None
