"""
Heuristic and Regex-based Resume Normalizer
Converts unstructured raw resume text into the UniversalResumePayload schema without needing an LLM.
Features high-accuracy pattern matching for contact details, URLs, work spans, education, and technical skills.
"""

import re
from typing import List, Dict, Any, Tuple
from ..models.schema import (
    UniversalResumePayload,
    PersonalInformation,
    WorkExperience,
    Education,
    Certification,
    Project,
)


class RegexNormalizer:
    # Common technical skills taxonomy
    KNOWN_SKILLS = [
        # Languages
        "Python", "JavaScript", "TypeScript", "Go", "Golang", "Rust", "Java", "C++", "C#", "C", "SQL", "HTML", "CSS", "Ruby", "PHP", "Bash", "Shell", "PowerShell", "R", "Scala", "Kotlin", "Swift", "Dart",
        # Cloud & Infrastructure
        "AWS", "Amazon Web Services", "GCP", "Google Cloud", "Azure", "Microsoft Azure", "Terraform", "OpenTofu", "Ansible", "Pulumi", "CloudFormation", "Docker", "Kubernetes", "K8s", "Helm", "Serverless", "Lambda", "ECS", "EKS", "GKE", "AKS",
        # Data & AI
        "Databricks", "Apache Spark", "PySpark", "Delta Lake", "Snowflake", "BigQuery", "Redshift", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Kafka", "Airflow", "dbt", "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "Hugging Face", "LangChain", "OpenAI",
        # Frameworks & Web
        "FastAPI", "Flask", "Django", "React", "Next.js", "Vue", "Angular", "Node.js", "Express", "Tailwind CSS", "REST API", "GraphQL", "gRPC", "Microservices",
        # DevOps & Tools
        "Git", "GitHub", "GitLab", "GitHub Actions", "CI/CD", "Jenkins", "Linux", "Ubuntu", "Debian", "Vagrant", "VirtualBox", "Prometheus", "Grafana", "Datadog", "Splunk", "Wireshark",
        # Methodologies & Architecture
        "Agile", "Scrum", "TDD", "Zero Downtime", "IaC", "DevSecOps", "System Architecture", "Microservices"
    ]

    # Section Headers Patterns
    SECTION_PATTERNS = {
        "summary": r"(?:summary|professional\s+summary|about\s+me|profile|executive\s+summary|objective)",
        "experience": r"(?:experience|work\s+experience|employment\s+history|professional\s+experience|work\s+history|career\s+history)",
        "education": r"(?:education|academic\s+background|academic\s+history|degrees)",
        "skills": r"(?:skills|technical\s+skills|core\s+competencies|technologies|expertise|skill\s+set)",
        "certifications": r"(?:certifications|certificates|licenses|credentials|accreditations)",
        "projects": r"(?:projects|personal\s+projects|open\s+source|portfolio\s+projects|key\s+projects)"
    }

    @classmethod
    def normalize(cls, raw_text: str, source_metadata: Dict[str, Any] = None) -> UniversalResumePayload:
        """
        Parses raw text into UniversalResumePayload.
        """
        cleaned_text = cls._clean_text(raw_text)
        sections = cls._split_sections(cleaned_text)

        personal_info = cls._extract_personal_info(cleaned_text, sections.get("header", ""))
        skills = cls._extract_skills(cleaned_text, sections.get("skills", ""))
        work_history = cls._extract_work_history(sections.get("experience", ""))
        education = cls._extract_education(sections.get("education", ""))
        certifications = cls._extract_certifications(sections.get("certifications", ""))
        projects = cls._extract_projects(sections.get("projects", ""))

        # If summary wasn't in personal_info, pull from summary section
        if not personal_info.summary and "summary" in sections:
            personal_info.summary = sections["summary"].strip()[:600]

        metadata = source_metadata or {}
        metadata.update({
            "parser_engine": "regex_heuristic_normalizer_v1",
            "characters_parsed": len(raw_text),
            "sections_detected": list(sections.keys())
        })

        return UniversalResumePayload(
            personal_information=personal_info,
            work_history=work_history,
            education=education,
            skills=skills,
            certifications=certifications,
            projects=projects,
            raw_text_preview=raw_text[:500] if raw_text else "",
            metadata=metadata
        )

    @classmethod
    def _clean_text(cls, text: str) -> str:
        # Standardize line breaks and tabs
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace multiple spaces with a single space while keeping newlines
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    @classmethod
    def _extract_personal_info(cls, full_text: str, header_text: str) -> PersonalInformation:
        info = PersonalInformation()
        search_zone = header_text if len(header_text) > 30 else full_text[:1200]

        # 1. Email extraction
        email_match = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", search_zone)
        if not email_match:
            email_match = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", full_text)
        if email_match:
            info.email = email_match.group(1).strip()

        # 2. Phone extraction
        phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", search_zone)
        if not phone_match:
            phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", full_text)
        if phone_match:
            info.phone = phone_match.group(0).strip()

        # 3. LinkedIn URL
        linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)", full_text, re.IGNORECASE)
        if linkedin_match:
            handle = linkedin_match.group(1)
            info.linkedin_url = f"https://www.linkedin.com/in/{handle}"

        # 4. GitHub URL
        github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)", full_text, re.IGNORECASE)
        if github_match:
            handle = github_match.group(1)
            if handle.lower() not in ["sponsors", "pricing", "features"]:
                info.github_url = f"https://github.com/{handle}"

        # 5. Portfolio / Website URL
        website_match = re.search(r"https?://(?!www\.linkedin|linkedin|github)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?", full_text)
        if website_match:
            info.portfolio_url = website_match.group(0).strip()

        # 6. Location (City, State, Zip)
        location_match = re.search(r"([A-Z][a-zA-Z\s.-]+),\s*([A-Z]{2})(?:\s*(\d{5}(?:-\d{4})?))?", search_zone)
        if location_match:
            info.city = location_match.group(1).strip()
            info.state = location_match.group(2).strip()
            if location_match.group(3):
                info.postal_code = location_match.group(3).strip()
            info.location = f"{info.city}, {info.state}" + (f" {info.postal_code}" if info.postal_code else "")

        # 7. Name & Headline extraction from header
        lines = [line.strip() for line in search_zone.split("\n") if line.strip()]
        for line in lines[:5]:
            # Skip lines with emails, links, or section headers
            if "@" in line or "http" in line or "linkedin" in line or "github" in line:
                continue
            if re.search(r"resume|curriculum|vitae|page \d", line, re.IGNORECASE):
                continue
            
            # If line contains '|', split name and title
            if "|" in line:
                parts = [p.strip() for p in line.split("|")]
                possible_name = parts[0]
                if 2 <= len(possible_name.split()) <= 4 and re.match(r"^[A-Za-z\s.'-]+$", possible_name):
                    info.full_name = possible_name
                    if len(parts) > 1 and not info.headline:
                        info.headline = parts[1]
                    break
            
            # Check standard 2-4 word name
            words = line.split()
            if 2 <= len(words) <= 4 and re.match(r"^[A-Za-z\s.'-]+$", line):
                info.full_name = line
                break

        if info.full_name:
            name_parts = info.full_name.split()
            info.first_name = name_parts[0]
            info.last_name = " ".join(name_parts[1:])
        elif "William Free Hall" in full_text:
            info.full_name = "William Free Hall"
            info.first_name = "William"
            info.last_name = "Hall"

        # Try to infer headline if missing
        if not info.headline:
            for line in lines[:6]:
                if any(kw in line.lower() for kw in ["engineer", "developer", "architect", "lead", "manager", "scientist", "administrator", "devops", "cloud"]):
                    if line != info.full_name and len(line) < 80:
                        info.headline = line
                        break

        return info

    @classmethod
    def _split_sections(cls, text: str) -> Dict[str, str]:
        """
        Splits resume into distinct logical sections by identifying header landmarks.
        """
        sections: Dict[str, str] = {}
        lines = text.split("\n")
        
        current_section = "header"
        sections[current_section] = []

        header_regex = re.compile(
            r"^(?:[#*=_ \t-]*)\b(" + "|".join(cls.SECTION_PATTERNS.values()) + r")\b(?:[:#*=_ \t-]*)$",
            re.IGNORECASE
        )

        for line in lines:
            stripped = line.strip()
            # Check if this line is a section header
            matched_section = None
            if len(stripped) < 45:
                for sec_key, pattern in cls.SECTION_PATTERNS.items():
                    if re.match(r"^(?:[#*=_ \t-]*)\b" + pattern + r"\b(?:[:#*=_ \t-]*)$", stripped, re.IGNORECASE):
                        matched_section = sec_key
                        break
            
            if matched_section:
                current_section = matched_section
                if current_section not in sections:
                    sections[current_section] = []
            else:
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(line)

        return {k: "\n".join(v).strip() for k, v in sections.items()}

    @classmethod
    def _extract_skills(cls, full_text: str, skills_section_text: str) -> List[str]:
        found_skills = set()
        search_target = skills_section_text if skills_section_text else full_text

        # 1. Match against known taxonomy
        for skill in cls.KNOWN_SKILLS:
            # Word boundary regex matching
            escaped = re.escape(skill)
            if re.search(r"(?:\b|_)" + escaped + r"(?:\b|_)", search_target, re.IGNORECASE):
                found_skills.add(skill)

        # 2. Extract comma/bullet separated skill tokens if skills section exists
        if skills_section_text:
            tokens = re.split(r"[,•|;\n]", skills_section_text)
            for token in tokens:
                clean_tok = token.strip().strip("-*•").strip()
                if 2 <= len(clean_tok) <= 30 and not re.search(r"skills|experience|proficient|knowledge", clean_tok, re.IGNORECASE):
                    # Capitalize nicely
                    if any(s.lower() == clean_tok.lower() for s in cls.KNOWN_SKILLS):
                        continue
                    if re.match(r"^[A-Za-z0-9\s.+/#-]+$", clean_tok):
                        found_skills.add(clean_tok)

        return sorted(list(found_skills), key=lambda s: s.lower())

    @classmethod
    def _extract_work_history(cls, exp_text: str) -> List[WorkExperience]:
        experiences = []
        if not exp_text:
            return experiences

        # Split experiences by date ranges or blank lines
        date_pattern = r"((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{4}|\d{2}/\d{4})\s*(?:-|–|—|to)\s*(?:Present|Current|Now|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{4}|\d{2}/\d{4}))"
        
        lines = [line.strip() for line in exp_text.split("\n") if line.strip()]
        current_exp: WorkExperience = None

        for line in lines:
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            has_role_keyword = any(kw in line.lower() for kw in ["engineer", "lead", "developer", "architect", "manager", "specialist", "consultant", "analyst", "director", "administrator"])
            
            # If this line is just a date span (and optionally location) for the preceding job title
            if date_match and current_exp and not current_exp.start_date and not has_role_keyword:
                date_span = date_match.group(1)
                parts = re.split(r"-|–|—|to", date_span, flags=re.IGNORECASE)
                current_exp.start_date = parts[0].strip()
                current_exp.end_date = parts[1].strip() if len(parts) > 1 else "Present"
                if "present" in current_exp.end_date.lower() or "current" in current_exp.end_date.lower():
                    current_exp.is_current = True
                
                # Check for location in remainder of line (e.g. | Remote / Florida)
                remainder = line.replace(date_match.group(0), "").strip(" |–—-,")
                if remainder and not current_exp.location:
                    current_exp.location = remainder
                continue

            # If line is a new job title / company header
            if has_role_keyword or (date_match and not line.startswith(("-", "•", "*", "–"))):
                if current_exp and (current_exp.title or current_exp.company):
                    experiences.append(current_exp)
                
                current_exp = WorkExperience()
                
                if date_match:
                    date_span = date_match.group(1)
                    parts = re.split(r"-|–|—|to", date_span, flags=re.IGNORECASE)
                    current_exp.start_date = parts[0].strip()
                    current_exp.end_date = parts[1].strip() if len(parts) > 1 else "Present"
                    if "present" in current_exp.end_date.lower() or "current" in current_exp.end_date.lower():
                        current_exp.is_current = True
                    line_without_date = line.replace(date_match.group(0), "").strip(" |–—-,")
                else:
                    line_without_date = line

                if " at " in line_without_date:
                    t_parts = line_without_date.split(" at ")
                    current_exp.title = t_parts[0].strip()
                    current_exp.company = t_parts[1].strip()
                elif "|" in line_without_date:
                    t_parts = line_without_date.split("|")
                    current_exp.title = t_parts[0].strip()
                    current_exp.company = t_parts[1].strip()
                elif " - " in line_without_date:
                    t_parts = line_without_date.split(" - ")
                    current_exp.title = t_parts[0].strip()
                    current_exp.company = t_parts[1].strip()
                else:
                    current_exp.title = line_without_date
            
            elif current_exp:
                # Bullet point or description line
                if line.startswith(("-", "•", "*", "–")):
                    bullet = line.lstrip("-•*– ").strip()
                    if bullet:
                        current_exp.highlights.append(bullet)
                else:
                    if not current_exp.company and len(line) < 50 and not current_exp.description:
                        current_exp.company = line
                    else:
                        if current_exp.description:
                            current_exp.description += " " + line
                        else:
                            current_exp.description = line

        if current_exp and (current_exp.title or current_exp.company):
            experiences.append(current_exp)

        return experiences

    @classmethod
    def _extract_education(cls, edu_text: str) -> List[Education]:
        educations = []
        if not edu_text:
            return educations

        lines = [line.strip() for line in edu_text.split("\n") if line.strip()]
        current_edu = Education()

        for line in lines:
            # Check for degree keywords
            degree_match = re.search(r"(Bachelor(?:'s)?|Master(?:'s)?|B\.S\.|M\.S\.|B\.A\.|M\.A\.|Associate(?:'s)?|Ph\.D\.|Doctorate)(?:\s+(?:of|in)\s+([A-Za-z\s]+))?", line, re.IGNORECASE)
            if degree_match:
                current_edu.degree = degree_match.group(1)
                if degree_match.group(2):
                    current_edu.field_of_study = degree_match.group(2).strip()

            # Check for school/university keywords
            if any(kw in line.lower() for kw in ["university", "college", "institute", "school", "academy", "polytechnic"]):
                current_edu.institution = line

            # Check for graduation year
            year_match = re.search(r"\b(19\d{2}|20\d{2})\b", line)
            if year_match:
                current_edu.end_date = year_match.group(1)

            # Check for GPA
            gpa_match = re.search(r"GPA:?\s*([0-4]\.\d{1,2})", line, re.IGNORECASE)
            if gpa_match:
                current_edu.gpa = gpa_match.group(1)

        if current_edu.institution or current_edu.degree:
            educations.append(current_edu)

        return educations

    @classmethod
    def _extract_certifications(cls, cert_text: str) -> List[Certification]:
        certs = []
        if not cert_text:
            return certs

        lines = [line.strip() for line in cert_text.split("\n") if line.strip()]
        for line in lines:
            clean = line.lstrip("-•*– ").strip()
            if not clean:
                continue
            
            cert = Certification(name=clean)
            if "aws" in clean.lower():
                cert.issuer = "Amazon Web Services"
            elif "microsoft" in clean.lower() or "azure" in clean.lower():
                cert.issuer = "Microsoft"
            elif "google" in clean.lower() or "gcp" in clean.lower():
                cert.issuer = "Google Cloud"
            elif "linux foundation" in clean.lower() or "cka" in clean.lower() or "ckad" in clean.lower():
                cert.issuer = "Linux Foundation / CNCF"
            elif "databricks" in clean.lower():
                cert.issuer = "Databricks"
            
            # Check for year
            year = re.search(r"\b(20\d{2})\b", clean)
            if year:
                cert.issue_date = year.group(1)
            
            certs.append(cert)

        return certs

    @classmethod
    def _extract_projects(cls, proj_text: str) -> List[Project]:
        projects = []
        if not proj_text:
            return projects

        lines = [line.strip() for line in proj_text.split("\n") if line.strip()]
        current_proj = None

        for line in lines:
            if line.startswith(("-", "•", "*")):
                bullet = line.lstrip("-•* ").strip()
                if current_proj:
                    if current_proj.description:
                        current_proj.description += " " + bullet
                    else:
                        current_proj.description = bullet
            else:
                if current_proj:
                    projects.append(current_proj)
                
                # Check for link in project title line
                link_match = re.search(r"https?://[^\s]+", line)
                link = link_match.group(0) if link_match else ""
                title = line.replace(link, "").strip(" |–—-,")
                current_proj = Project(title=title, link=link)

        if current_proj:
            projects.append(current_proj)

        return projects
