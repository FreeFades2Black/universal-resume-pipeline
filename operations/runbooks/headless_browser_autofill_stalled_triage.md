# Operational Runbook: Diagnosing Headless Browser ATS Form Autofill Failures

**Severity:** P2 / Autofill Stalled  
**Target Systems:** Playwright Headless Worker, ATS Extension, Extraction Engine

## Diagnostic Workflow

### 1. Inspect Failed DOM Selectors in Debug Mode
```bash
python -m cli.main --debug-autofill --url "https://jobs.lever.co/example/123"
```

### 2. Verify React Prototype Setter Injection
Inspect browser console logs for `ReactInputSetterHookApplied` confirmation:
```javascript
// Test in browser console
let input = document.querySelector('input[name="email"]');
let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
nativeSetter.call(input, 'test@domain.com');
input.dispatchEvent(new Event('input', { bubbles: true }));
```

### 3. Step-by-Step Remediation
1. If ATS page updated form structure, update field selector mappings in `extension/selectors.json`.
2. Run automated verification suite:
   ```bash
   python -m pytest tests/test_extractors.py -v
   ```
