# Incident Post-Mortem: React Controlled Component State Discarding Autofilled Forms

**Incident Date:** 2026-07-06  
**Impact Duration:** 45 minutes  
**Severity:** SEV-3  
**Root Cause:** A Workday ATS frontend update migrated from standard HTML forms to React controlled components with state deduplication. Our autofill script populated form inputs visually, but submitting the form sent empty JSON bodies because React state remained uninitialized.

## Timeline
* **16:00 UTC:** Test autofill batch executed against 20 sample job listings.
* **16:08 UTC:** 18 of 20 applications failed with `Validation Error: First Name is required`.
* **16:22 UTC:** Engineer reproduced issue in Playwright headed mode; inputs appeared full on screen but empty on submit.
* **16:35 UTC:** Discovered React's `_valueTracker` was intercepting standard events.
* **16:45 UTC:** Deployed prototype setter override with custom dispatch hook; all 20 submissions verified clean.

## Corrective Actions
1. Standardized prototype setter hook across all extension and CLI form-filling modules.
2. Added mock React controlled component form in `tests/test_cli.py` to prevent regressions.
