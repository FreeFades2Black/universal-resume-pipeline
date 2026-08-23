"""
Universal Resume Schema Models
Defines the standard, normalized JSON data structure for autofilling ATS application forms.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PersonalInformation(BaseModel):
    first_name: str = Field(default="", description="Candidate's first/given name")
    last_name: str = Field(default="", description="Candidate's last/family name")
    full_name: str = Field(default="", description="Full display name")
    email: str = Field(default="", description="Contact email address")
    phone: str = Field(default="", description="Contact phone number in standard format")
    headline: str = Field(default="", description="Professional headline or title")
    summary: str = Field(default="", description="Executive summary or bio")
    location: str = Field(default="", description="Full location string (e.g., 'Niceville, FL, USA')")
    city: str = Field(default="", description="City name")
    state: str = Field(default="", description="State, province, or region")
    country: str = Field(default="United States", description="Country name")
    postal_code: str = Field(default="", description="ZIP or postal code")
    address_line: str = Field(default="", description="Street address line if available")
    linkedin_url: str = Field(default="", description="LinkedIn profile URL")
    github_url: str = Field(default="", description="GitHub profile URL")
    portfolio_url: str = Field(default="", description="Personal website or portfolio URL")
    twitter_url: str = Field(default="", description="Twitter/X profile URL")


class WorkExperience(BaseModel):
    title: str = Field(default="", description="Job title or role")
    company: str = Field(default="", description="Employer or company name")
    location: str = Field(default="", description="Job location (city/state or Remote)")
    start_date: str = Field(default="", description="Start date (YYYY-MM or YYYY)")
    end_date: str = Field(default="Present", description="End date (YYYY-MM, YYYY, or 'Present')")
    is_current: bool = Field(default=False, description="Whether this is the current job")
    description: str = Field(default="", description="Summary of responsibilities and achievements")
    highlights: List[str] = Field(default_factory=list, description="Bullet points of key accomplishments")
    technologies: List[str] = Field(default_factory=list, description="Tools, frameworks, and languages used")


class Education(BaseModel):
    institution: str = Field(default="", description="School, university, or academy name")
    degree: str = Field(default="", description="Degree level (e.g., Bachelor of Science, Master of Science)")
    field_of_study: str = Field(default="", description="Major, discipline, or field of study")
    start_date: str = Field(default="", description="Start date (YYYY or YYYY-MM)")
    end_date: str = Field(default="", description="Graduation date (YYYY or YYYY-MM)")
    gpa: str = Field(default="", description="Grade Point Average if listed")
    honors: List[str] = Field(default_factory=list, description="Honors, awards, or distinctions")


class Certification(BaseModel):
    name: str = Field(default="", description="Certification title")
    issuer: str = Field(default="", description="Issuing organization (AWS, Microsoft, Google, etc.)")
    issue_date: str = Field(default="", description="Issue date (YYYY or YYYY-MM)")
    expiry_date: str = Field(default="", description="Expiration date if applicable")
    credential_id: str = Field(default="", description="License or credential ID")
    credential_url: str = Field(default="", description="Verification URL")


class Project(BaseModel):
    title: str = Field(default="", description="Project name")
    description: str = Field(default="", description="Brief project description")
    link: str = Field(default="", description="Repository or live URL")
    technologies: List[str] = Field(default_factory=list, description="Technologies used in project")
    role: str = Field(default="", description="Role in the project")


class ApplicationPreferences(BaseModel):
    authorized_to_work: str = Field(default="Yes", description="Legally authorized to work in target country")
    requires_sponsorship: str = Field(default="No", description="Requires visa sponsorship now or in future")
    veteran_status: str = Field(default="I am not a protected veteran", description="Protected veteran status")
    disability_status: str = Field(default="I do not have a disability", description="Voluntary self-identification of disability")
    gender: str = Field(default="Decline to state", description="Gender identity")
    race_ethnicity: str = Field(default="Decline to state", description="Race / Ethnicity")
    notice_period: str = Field(default="2 weeks", description="Available notice period")
    desired_salary: str = Field(default="", description="Target salary or compensation range")
    willing_to_relocate: str = Field(default="Yes", description="Willingness to relocate")


class UniversalResumePayload(BaseModel):
    schema_version: str = Field(default="1.0.0", description="Universal schema specification version")
    personal_information: PersonalInformation = Field(default_factory=PersonalInformation)
    work_history: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    preferences: ApplicationPreferences = Field(default_factory=ApplicationPreferences)
    raw_text_preview: Optional[str] = Field(default=None, description="First 500 characters of raw parsed text for debugging")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Parsing provenance, timestamp, extractor engine used")
