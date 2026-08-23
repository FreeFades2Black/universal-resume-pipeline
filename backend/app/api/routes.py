"""
API Route Definitions
"""

import time
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, Body, HTTPException
from pydantic import BaseModel

from ..models.schema import UniversalResumePayload
from ..extractors.pipeline import UniversalResumePipeline
from ..extractors.llm_parser import LLMParser

router = APIRouter()
pipeline = UniversalResumePipeline()


class TextParseRequest(BaseModel):
    raw_text: str
    filename: Optional[str] = "direct_text_input.txt"
    prefer_llm: Optional[bool] = False
    provider: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    llm_available: bool
    timestamp: float


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Returns the operational status of the parser engine."""
    return HealthResponse(
        status="healthy",
        app_name="Universal Resume Extraction & Injection Pipeline",
        version="1.0.0",
        llm_available=LLMParser.is_available(),
        timestamp=time.time()
    )


@router.get("/schema")
async def get_universal_schema():
    """Returns the JSON Schema definition for the Universal Resume Payload."""
    return UniversalResumePayload.model_json_schema()


@router.post("/parse", response_model=UniversalResumePayload)
async def parse_resume_file(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    prefer_llm: bool = Form(False),
    provider: Optional[str] = Form(None)
):
    """
    Universal Parsing Endpoint.
    Accepts multipart file upload (PDF, DOCX, TXT, JSON) or form raw_text.
    """
    try:
        if file is not None:
            content_bytes = await file.read()
            if not content_bytes:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")
            
            pipe = UniversalResumePipeline(prefer_llm=prefer_llm)
            payload = pipe.process(
                file_input=content_bytes,
                filename=file.filename or "uploaded_resume",
                override_provider=provider
            )
            return payload

        elif raw_text:
            pipe = UniversalResumePipeline(prefer_llm=prefer_llm)
            payload = pipe.process(
                file_input=raw_text,
                filename="text_input.txt",
                override_provider=provider
            )
            return payload

        else:
            raise HTTPException(status_code=400, detail="Must provide either 'file' or 'raw_text'.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


@router.post("/parse/json", response_model=UniversalResumePayload)
async def parse_resume_json_body(request: TextParseRequest = Body(...)):
    """
    JSON Body Parsing Endpoint for programmatic API clients and extensions.
    """
    try:
        pipe = UniversalResumePipeline(prefer_llm=request.prefer_llm or False)
        payload = pipe.process(
            file_input=request.raw_text,
            filename=request.filename or "json_input.txt",
            override_provider=request.provider
        )
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process text: {str(e)}")


@router.post("/match-selectors")
async def get_ats_selector_mappings(payload: UniversalResumePayload):
    """
    Returns pre-computed DOM selector values and ATS mapping dictionaries
    for Greenhouse, Lever, Workday, and Ashby.
    """
    info = payload.personal_information
    first_job = payload.work_history[0] if payload.work_history else None
    first_edu = payload.education[0] if payload.education else None

    return {
        "candidate_summary": {
            "name": info.full_name,
            "email": info.email,
            "phone": info.phone,
            "top_skills_count": len(payload.skills),
            "experience_count": len(payload.work_history)
        },
        "ats_profiles": {
            "greenhouse": {
                "first_name": {"selector": "input#first_name, input[id*='first_name']", "value": info.first_name},
                "last_name": {"selector": "input#last_name, input[id*='last_name']", "value": info.last_name},
                "email": {"selector": "input#email, input[id*='email']", "value": info.email},
                "phone": {"selector": "input#phone, input[id*='phone']", "value": info.phone},
                "linkedin": {"selector": "input[id*='job_application_answers_attributes_'][id*='linkedin'], input[autocomplete*='linkedin']", "value": info.linkedin_url},
                "website": {"selector": "input[id*='website'], input[autocomplete*='website']", "value": info.portfolio_url or info.github_url}
            },
            "lever": {
                "name": {"selector": "input[name='name']", "value": info.full_name},
                "email": {"selector": "input[name='email']", "value": info.email},
                "phone": {"selector": "input[name='phone']", "value": info.phone},
                "org": {"selector": "input[name='org']", "value": first_job.company if first_job else ""},
                "urls_linkedin": {"selector": "input[name='urls[LinkedIn]']", "value": info.linkedin_url},
                "urls_github": {"selector": "input[name='urls[GitHub]']", "value": info.github_url},
                "urls_portfolio": {"selector": "input[name='urls[Portfolio]'], input[name='urls[Other]']", "value": info.portfolio_url}
            },
            "workday": {
                "legal_name_first": {"selector": "input[data-automation-id*='legalNameSection_firstName']", "value": info.first_name},
                "legal_name_last": {"selector": "input[data-automation-id*='legalNameSection_lastName']", "value": info.last_name},
                "email": {"selector": "input[data-automation-id*='email']", "value": info.email},
                "phone": {"selector": "input[data-automation-id*='phone-number']", "value": info.phone},
                "address_line1": {"selector": "input[data-automation-id*='addressSection_addressLine1']", "value": info.address_line or info.location},
                "city": {"selector": "input[data-automation-id*='addressSection_city']", "value": info.city},
                "postal_code": {"selector": "input[data-automation-id*='addressSection_postalCode']", "value": info.postal_code}
            }
        }
    }
