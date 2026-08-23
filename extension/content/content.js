/**
 * Universal Resume Pipeline - Content Script Injector
 * Detects ATS platforms (Greenhouse, Lever, Workday, Ashby, SmartRecruiters, Taleo)
 * and generic job forms, then intelligently populates fields using UniversalResumePayload JSON.
 */

(() => {
  if (window.__UNIVERSAL_RESUME_INJECTOR_LOADED__) return;
  window.__UNIVERSAL_RESUME_INJECTOR_LOADED__ = true;

  console.log("⚡ [Universal Resume Injector] Content script active and listening.");

  // Listen for messages from popup or background script
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "AUTOFILL_RESUME" && request.payload) {
      const result = injectResumeData(request.payload);
      sendResponse(result);
    }
    return true;
  });

  /**
   * Main form injection engine
   */
  function injectResumeData(payload) {
    const info = payload.personal_information || {};
    const firstJob = (payload.work_history && payload.work_history[0]) || {};
    const firstEdu = (payload.education && payload.education[0]) || {};
    const skillsList = payload.skills || [];
    const skillsStr = skillsList.join(", ");

    let fieldsFilledCount = 0;

    // Field match rules with priority selectors and semantic keywords
    const fieldRules = [
      {
        key: "first_name",
        value: info.first_name,
        selectors: ["input#first_name", "input[name='first_name']", "input[name='firstName']", "input[id*='first_name']", "input[autocomplete='given-name']", "input[data-automation-id*='firstName']"],
        keywords: ["first name", "given name", "first_name", "fname"]
      },
      {
        key: "last_name",
        value: info.last_name,
        selectors: ["input#last_name", "input[name='last_name']", "input[name='lastName']", "input[id*='last_name']", "input[autocomplete='family-name']", "input[data-automation-id*='lastName']"],
        keywords: ["last name", "family name", "surname", "last_name", "lname"]
      },
      {
        key: "full_name",
        value: info.full_name || `${info.first_name} ${info.last_name}`.trim(),
        selectors: ["input#name", "input[name='name']", "input[name='fullName']", "input[id*='full_name']", "input[autocomplete='name']"],
        keywords: ["full name", "your name", "candidate name", "name"]
      },
      {
        key: "email",
        value: info.email,
        selectors: ["input#email", "input[name='email']", "input[type='email']", "input[id*='email']", "input[autocomplete='email']", "input[data-automation-id*='email']"],
        keywords: ["email", "e-mail", "email address", "email_address"]
      },
      {
        key: "phone",
        value: info.phone,
        selectors: ["input#phone", "input[name='phone']", "input[type='tel']", "input[name*='phone']", "input[id*='phone']", "input[autocomplete='tel']", "input[data-automation-id*='phone']"],
        keywords: ["phone", "telephone", "mobile", "phone number", "cell"]
      },
      {
        key: "linkedin",
        value: info.linkedin_url,
        selectors: [
          "input[name='urls[LinkedIn]']",
          "input[id*='linkedin']",
          "input[name*='linkedin']",
          "input[placeholder*='linkedin.com']",
          "input[id*='job_application_answers_attributes_'][id*='linkedin']"
        ],
        keywords: ["linkedin", "linkedin profile", "linkedin url"]
      },
      {
        key: "github",
        value: info.github_url,
        selectors: [
          "input[name='urls[GitHub]']",
          "input[id*='github']",
          "input[name*='github']",
          "input[placeholder*='github.com']"
        ],
        keywords: ["github", "github profile", "github url", "git"]
      },
      {
        key: "portfolio",
        value: info.portfolio_url || info.github_url,
        selectors: [
          "input[name='urls[Portfolio]']",
          "input[name='urls[Other]']",
          "input[id*='website']",
          "input[name*='website']",
          "input[id*='portfolio']",
          "input[placeholder*='portfolio']"
        ],
        keywords: ["website", "portfolio", "personal site", "other website"]
      },
      {
        key: "location",
        value: info.location || `${info.city || ''} ${info.state || ''}`.trim(),
        selectors: ["input#location", "input[name='location']", "input[id*='location']", "input[placeholder*='location']", "input[data-automation-id*='addressSection_addressLine1']"],
        keywords: ["location", "current city", "address", "residence"]
      },
      {
        key: "city",
        value: info.city,
        selectors: ["input#city", "input[name='city']", "input[id*='city']", "input[data-automation-id*='city']"],
        keywords: ["city", "town"]
      },
      {
        key: "state",
        value: info.state,
        selectors: ["input#state", "input[name='state']", "input[id*='state']", "input[data-automation-id*='state']"],
        keywords: ["state", "province", "region"]
      },
      {
        key: "postal_code",
        value: info.postal_code,
        selectors: ["input#postal_code", "input[name='postal_code']", "input[name='zip']", "input[id*='zip']", "input[data-automation-id*='postalCode']"],
        keywords: ["postal code", "zip code", "zip"]
      },
      {
        key: "current_company",
        value: firstJob.company || "",
        selectors: ["input[name='org']", "input#company", "input[name='company']", "input[id*='company']", "input[name*='current_company']"],
        keywords: ["current company", "employer", "organization", "company"]
      },
      {
        key: "current_title",
        value: firstJob.title || info.headline || "",
        selectors: ["input#title", "input[name='title']", "input[id*='title']", "input[name*='current_title']"],
        keywords: ["current title", "job title", "headline", "current role"]
      },
      {
        key: "education_school",
        value: firstEdu.institution || "",
        selectors: ["input#school", "input[name='school']", "input[id*='school']", "input[name*='education']", "input[name*='university']"],
        keywords: ["school", "university", "college", "institution"]
      },
      {
        key: "skills",
        value: skillsStr,
        selectors: ["input[name*='skills']", "textarea[name*='skills']", "input[id*='skills']", "textarea[id*='skills']"],
        keywords: ["skills", "key skills", "technologies", "proficiencies"]
      },
      {
        key: "summary",
        value: info.summary || (firstJob.description) || "",
        selectors: ["textarea#summary", "textarea[name='summary']", "textarea[name*='cover_letter']", "textarea[name='comments']"],
        keywords: ["summary", "additional comments", "cover letter", "about you", "notes"]
      }
    ];

    // Track populated DOM elements to avoid duplicate writes
    const populatedElements = new Set();

    // 1. Direct CSS Selector Pass
    for (const rule of fieldRules) {
      if (!rule.value) continue;

      for (const selector of rule.selectors) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
          if (!populatedElements.has(el) && isVisible(el)) {
            setElementValue(el, rule.value);
            populatedElements.add(el);
            highlightElement(el);
            fieldsFilledCount++;
          }
        });
      }
    }

    // 2. Semantic Heuristic Fallback Pass on all inputs and textareas
    const allInputs = document.querySelectorAll("input:not([type='hidden']):not([type='submit']):not([type='button']), textarea");
    allInputs.forEach(input => {
      if (populatedElements.has(input) || !isVisible(input)) return;

      const descriptor = getElementDescriptor(input).toLowerCase();
      
      for (const rule of fieldRules) {
        if (!rule.value) continue;

        const isMatch = rule.keywords.some(kw => {
          const regex = new RegExp(`\\b${kw}\\b`, 'i');
          return regex.test(descriptor);
        });

        if (isMatch) {
          setElementValue(input, rule.value);
          populatedElements.add(input);
          highlightElement(input);
          fieldsFilledCount++;
          break;
        }
      }
    });

    // 3. Dropdown / Select Auto-Select (e.g., Work Authorization, Veteran Status)
    const preferences = payload.preferences || {};
    const allSelects = document.querySelectorAll("select");
    allSelects.forEach(select => {
      if (!isVisible(select)) return;
      const desc = getElementDescriptor(select).toLowerCase();

      if (desc.includes("authorized") || desc.includes("legal") || desc.includes("work in")) {
        selectOptionMatching(select, ["yes", "authorized", "eligible"]);
        highlightElement(select);
        fieldsFilledCount++;
      } else if (desc.includes("sponsorship") || desc.includes("visa")) {
        selectOptionMatching(select, ["no", "not require", "does not require"]);
        highlightElement(select);
        fieldsFilledCount++;
      } else if (desc.includes("veteran")) {
        selectOptionMatching(select, ["not a veteran", "not protected", "i am not"]);
        highlightElement(select);
        fieldsFilledCount++;
      }
    });

    // Show floating toast on host page
    showInjectedToast(fieldsFilledCount, info.full_name || "Candidate");

    return {
      success: true,
      fieldsFilled: fieldsFilledCount,
      candidate: info.full_name
    };
  }

  /**
   * Dispatches synthetic events so React, Vue, and Angular register the programmatic input change.
   */
  function setElementValue(element, value) {
    if (!element || value === undefined || value === null) return;

    element.focus();

    // Call native prototype value setter for React 16+ synthetic events
    const prototype = Object.getPrototypeOf(element);
    const valueSetter = Object.getOwnPropertyDescriptor(prototype, "value")?.set;

    if (valueSetter) {
      valueSetter.call(element, value);
    } else {
      element.value = value;
    }

    // Trigger standard DOM events
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
    element.dispatchEvent(new Event("blur", { bubbles: true }));
  }

  /**
   * Helper to select option in standard HTML select element
   */
  function selectOptionMatching(selectEl, keywords) {
    for (let i = 0; i < selectEl.options.length; i++) {
      const optText = selectEl.options[i].text.toLowerCase();
      const optVal = selectEl.options[i].value.toLowerCase();
      if (keywords.some(k => optText.includes(k) || optVal.includes(k))) {
        selectEl.selectedIndex = i;
        selectEl.dispatchEvent(new Event("change", { bubbles: true }));
        break;
      }
    }
  }

  /**
   * Returns a consolidated semantic descriptor for an input (id, name, placeholder, label text, aria-label)
   */
  function getElementDescriptor(el) {
    let text = `${el.id || ''} ${el.name || ''} ${el.placeholder || ''} ${el.getAttribute('aria-label') || ''} ${el.getAttribute('autocomplete') || ''}`;
    
    // Check for associated <label for="...">
    if (el.id) {
      const label = document.querySelector(`label[for='${el.id}']`);
      if (label) text += ` ${label.innerText}`;
    }
    
    // Check parent label
    const parentLabel = el.closest("label");
    if (parentLabel) {
      text += ` ${parentLabel.innerText}`;
    }

    // Check previous sibling or parent header
    const parentContainer = el.closest(".form-group, .field, .input-container, div");
    if (parentContainer) {
      const labelInContainer = parentContainer.querySelector("label, span.label, p.label, strong");
      if (labelInContainer) text += ` ${labelInContainer.innerText}`;
    }

    return text;
  }

  function isVisible(el) {
    return !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  }

  function highlightElement(el) {
    el.classList.add("universal-resume-autofilled");
  }

  /**
   * Displays an interactive floating toast on the host job application page
   */
  function showInjectedToast(count, candidateName) {
    const existing = document.getElementById("universal-resume-toast");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.id = "universal-resume-toast";
    toast.className = "universal-resume-toast-banner";
    toast.innerHTML = `
      <div class="uri-toast-content">
        <div class="uri-toast-icon">⚡</div>
        <div class="uri-toast-text">
          <strong>Universal Resume Autofill</strong>
          <span>Successfully filled <b>${count} fields</b> for ${candidateName}</span>
        </div>
        <button class="uri-toast-close" type="button">&times;</button>
      </div>
    `;

    document.body.appendChild(toast);

    toast.querySelector(".uri-toast-close").addEventListener("click", () => {
      toast.remove();
    });

    setTimeout(() => {
      if (toast.parentNode) {
        toast.classList.add("uri-toast-fadeout");
        setTimeout(() => toast.remove(), 400);
      }
    }, 4500);
  }
})();
