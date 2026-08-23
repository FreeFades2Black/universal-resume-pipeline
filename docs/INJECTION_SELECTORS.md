# ATS Selector Catalog & Heuristic Mapping Guide

This reference document outlines the CSS selectors and semantic heuristics used by the **Universal Resume Content Script Injector** (`extension/content/content.js`) across major Applicant Tracking Systems (ATS).

---

## Supported ATS Platforms

### 1. Greenhouse (`boards.greenhouse.io`, `job-boards.greenhouse.io`)
| Target Field | Primary Selectors | Fallback Attributes |
|---|---|---|
| First Name | `input#first_name`, `input[id*='first_name']` | `autocomplete="given-name"` |
| Last Name | `input#last_name`, `input[id*='last_name']` | `autocomplete="family-name"` |
| Email | `input#email`, `input[id*='email']` | `type="email"` |
| Phone | `input#phone`, `input[id*='phone']` | `type="tel"` |
| LinkedIn | `input[id*='job_application_answers_attributes_'][id*='linkedin']` | `placeholder*="linkedin.com"` |
| Website / Portfolio | `input[id*='website']`, `input[id*='portfolio']` | `autocomplete="url"` |
| Location | `input#location`, `input[id*='location']` | `placeholder*="location"` |

---

### 2. Lever (`jobs.lever.co`)
| Target Field | Primary Selectors | Fallback Attributes |
|---|---|---|
| Full Name | `input[name='name']`, `input#name` | `autocomplete="name"` |
| Email | `input[name='email']`, `input#email` | `type="email"` |
| Phone | `input[name='phone']`, `input#phone` | `type="tel"` |
| Current Company | `input[name='org']`, `input#org` | `placeholder*="employer"` |
| LinkedIn URL | `input[name='urls[LinkedIn]']` | `placeholder*="linkedin"` |
| GitHub URL | `input[name='urls[GitHub]']` | `placeholder*="github"` |
| Portfolio URL | `input[name='urls[Portfolio]']`, `input[name='urls[Other]']` | `placeholder*="portfolio"` |
| Additional Comments | `textarea[name='comments']` | `textarea#comments` |

---

### 3. Workday (`*.myworkdayjobs.com`)
| Target Field | Primary Automation IDs |
|---|---|
| Legal First Name | `input[data-automation-id*='legalNameSection_firstName']` |
| Legal Last Name | `input[data-automation-id*='legalNameSection_lastName']` |
| Email Address | `input[data-automation-id*='email']` |
| Phone Number | `input[data-automation-id*='phone-number']` |
| Address Line 1 | `input[data-automation-id*='addressSection_addressLine1']` |
| City | `input[data-automation-id*='addressSection_city']` |
| Postal Code | `input[data-automation-id*='addressSection_postalCode']` |

---

### 4. Ashby (`jobs.ashbyhq.com`)
| Target Field | Primary Selectors |
|---|---|
| Name | `input[name*='name']`, `input[placeholder*='name' i]` |
| Email | `input[name*='email']`, `input[type='email']` |
| Phone | `input[name*='phone']`, `input[type='tel']` |
| LinkedIn | `input[name*='linkedin' i]`, `input[placeholder*='linkedin' i]` |
| GitHub | `input[name*='github' i]`, `input[placeholder*='github' i]` |

---

## 5. Universal Semantic Fallback Algorithm

When an application form does not match a known vendor selector, the injector executes a 3-stage heuristic:

1. **Descriptor Compilation**: Aggregates `id`, `name`, `placeholder`, `aria-label`, `autocomplete`, and parent `<label>` / `<legend>` text.
2. **Word-Boundary Regex Matching**: Tests semantic keywords (`first name`, `surname`, `e-mail`, `mobile`, `residence`, `technologies`).
3. **Synthetic Event Dispatch**: Triggers native prototype setters:
   ```javascript
   Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set.call(el, val);
   el.dispatchEvent(new Event('input', { bubbles: true }));
   el.dispatchEvent(new Event('change', { bubbles: true }));
   ```
