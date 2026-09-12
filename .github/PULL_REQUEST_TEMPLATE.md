## Resume Pipeline Operational Overview
*Describe modifications to PDF extractors, autofill selectors, or schema models.*

- [ ] Spatial PDF / OCR Extractor (pdfplumber)
- [ ] ATS Autofill DOM Prototype Setter
- [ ] Candidate Pydantic Data Schema
- [ ] REST API & Headless Automation Worker

## Robustness & Layout Verification
- **Multi-Column Tested:** Confirmed two-column resumes maintain chronological reading order.
- **React Input Setter Tested:** Verified controlled inputs retain values on form submit.

## Verification Checklist
- [ ] Test suite passed (18/18 tests): `python -m pytest tests/ -v`
- [ ] Zero candidate PII committed to repository test fixtures
