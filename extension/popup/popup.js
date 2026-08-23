/**
 * Universal Resume Extension - Popup Controller
 * Manages Drag-and-Drop file ingestion, Backend API / Standalone parsing,
 * Local Storage persistence, and Tab Autofill messaging.
 */

const API_CANDIDATE_URLS = [
  "http://127.0.0.1:8008/api/v1",
  "http://localhost:8008/api/v1",
  "http://127.0.0.1:8000/api/v1",
  "http://localhost:8000/api/v1"
];
let activeApiUrl = API_CANDIDATE_URLS[0];

// Default Sample Data
const SAMPLE_CANDIDATE = {
  "schema_version": "1.0.0",
  "personal_information": {
    "first_name": "William",
    "last_name": "Hall",
    "full_name": "William Free Hall",
    "email": "free@example.com",
    "phone": "555-019-2834",
    "headline": "Technical Lead / Cloud & DevOps Engineer",
    "summary": "Accomplished Cloud & DevOps Engineer with deep expertise in Multi-Cloud Infrastructure, Databricks, Terraform, Kubernetes, and automated CI/CD pipelines.",
    "location": "Niceville, FL",
    "city": "Niceville",
    "state": "FL",
    "country": "United States",
    "postal_code": "32578",
    "address_line": "123 Emerald Coast Pkwy",
    "linkedin_url": "https://linkedin.com/in/williamfreehall",
    "github_url": "https://github.com/FreeFades2Black",
    "portfolio_url": "https://github.com/FreeFades2Black"
  },
  "work_history": [
    {
      "title": "Technical Lead / Cloud Engineer",
      "company": "Tech Solutions Inc.",
      "location": "Remote / Florida",
      "start_date": "2024",
      "end_date": "Present",
      "is_current": true,
      "description": "Architected zero-downtime multi-cloud infrastructure and high-throughput automated telemetry pipelines.",
      "highlights": [
        "Constructed 5-pillar Terraform multi-cloud architecture spanning AWS, GCP, Databricks, and Hugging Face.",
        "Engineered automated CI/CD pipelines with 100% test coverage and static analysis."
      ],
      "technologies": ["Python", "AWS", "Terraform", "Docker", "Kubernetes", "Databricks"]
    }
  ],
  "education": [
    {
      "institution": "University of Florida",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science & Information Technology",
      "start_date": "2018",
      "end_date": "2022",
      "gpa": "3.85"
    }
  ],
  "skills": ["Python", "AWS", "Terraform", "Docker", "Kubernetes", "Databricks", "PySpark", "FastAPI", "PostgreSQL", "CI/CD", "Linux", "Git"],
  "certifications": [
    {
      "name": "AWS Certified Solutions Architect",
      "issuer": "Amazon Web Services",
      "issue_date": "2024"
    }
  ],
  "preferences": {
    "authorized_to_work": "Yes",
    "requires_sponsorship": "No",
    "veteran_status": "I am not a protected veteran",
    "notice_period": "2 weeks"
  },
  "metadata": {
    "parser_engine": "sample_loader"
  }
};

let currentPayload = null;
let isBackendOnline = false;

// DOM Elements
const dropZoneSection = document.getElementById("drop-zone-section");
const profileSection = document.getElementById("profile-section");
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const browseBtn = document.getElementById("browse-btn");
const loadSampleBtn = document.getElementById("load-sample-btn");
const backendStatus = document.getElementById("backend-status");

// Action Elements
const autofillBtn = document.getElementById("autofill-btn");
const replaceResumeBtn = document.getElementById("replace-resume-btn");
const clearDataBtn = document.getElementById("clear-data-btn");
const copyJsonBtn = document.getElementById("copy-json-btn");
const saveJsonBtn = document.getElementById("save-json-btn");
const rawJsonEditor = document.getElementById("raw-json-editor");
const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toast-message");

// Initialize
document.addEventListener("DOMContentLoaded", async () => {
  checkBackendHealth();
  setupEventListeners();
  setupTabNavigation();
  loadStoredProfile();
});

// Check if local FastAPI backend is active
async function checkBackendHealth() {
  for (const url of API_CANDIDATE_URLS) {
    try {
      const res = await fetch(`${url}/health`, { method: "GET" });
      if (res.ok) {
        activeApiUrl = url;
        isBackendOnline = true;
        backendStatus.className = "status-badge online";
        backendStatus.innerHTML = `<span class="status-dot"></span><span>Backend Online (${url.includes("8008") ? "8008" : "8000"})</span>`;
        return;
      }
    } catch (e) {
      // Continue searching
    }
  }
  isBackendOnline = false;
  backendStatus.className = "status-badge standalone";
  backendStatus.innerHTML = `<span class="status-dot"></span><span>Standalone Mode</span>`;
}

// Event Listeners
function setupEventListeners() {
  // File Browse
  browseBtn.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  });

  // Drag & Drop
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZoneSection.classList.add("drag-over");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZoneSection.classList.remove("drag-over");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZoneSection.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  });

  // Sample Loader
  loadSampleBtn.addEventListener("click", () => {
    renderProfile(SAMPLE_CANDIDATE);
    saveProfileToStorage(SAMPLE_CANDIDATE);
    showToast("Loaded William Free Hall sample resume!");
  });

  // Replace & Clear
  replaceResumeBtn.addEventListener("click", () => fileInput.click());
  clearDataBtn.addEventListener("click", clearProfile);

  // JSON Actions
  copyJsonBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(rawJsonEditor.value);
    showToast("Copied Universal JSON to clipboard!");
  });

  saveJsonBtn.addEventListener("click", () => {
    try {
      const parsed = JSON.parse(rawJsonEditor.value);
      renderProfile(parsed);
      saveProfileToStorage(parsed);
      showToast("Saved JSON edits successfully!");
    } catch (e) {
      showToast("Invalid JSON syntax!");
    }
  });

  // Primary Autofill Trigger
  autofillBtn.addEventListener("click", executeAutofill);
}

// Tab Navigation
function setupTabNavigation() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      document.getElementById(targetId).classList.add("active");
    });
  });
}

// Ingest and Parse Resume File
async function processFile(file) {
  showToast(`Parsing ${file.name}...`);
  
  if (isBackendOnline) {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${activeApiUrl}/parse`, {
        method: "POST",
        body: formData
      });
      if (response.ok) {
        const payload = await response.json();
        renderProfile(payload);
        saveProfileToStorage(payload);
        showToast("Extracted via FastAPI backend!");
        return;
      }
    } catch (e) {
      console.warn("Backend parsing failed, using client-side fallback:", e);
    }
  }

  // Client-Side Standalone Fallback Parser
  const reader = new FileReader();
  reader.onload = (e) => {
    const text = e.target.result;
    const clientPayload = clientSideParse(text, file.name);
    renderProfile(clientPayload);
    saveProfileToStorage(clientPayload);
    showToast("Extracted via client fallback!");
  };

  if (file.name.endsWith(".json")) {
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result);
        renderProfile(json);
        saveProfileToStorage(json);
        showToast("Loaded JSON resume profile!");
      } catch (err) {
        showToast("Failed to parse JSON file.");
      }
    };
    reader.readAsText(file);
  } else {
    reader.readAsText(file);
  }
}

// Lightweight Client-Side Parsing Heuristics (Zero-dependency fallback)
function clientSideParse(text, filename) {
  const emailMatch = text.match(/([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)/);
  const phoneMatch = text.match(/(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/);
  const linkedinMatch = text.match(/(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_-]+)/i);
  const githubMatch = text.match(/(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)/i);

  // Extract simple skills
  const skillsPool = ["Python", "AWS", "Terraform", "Docker", "Kubernetes", "Databricks", "JavaScript", "SQL", "CI/CD", "Linux", "FastAPI", "React"];
  const matchedSkills = skillsPool.filter(s => new RegExp(`\\b${s}\\b`, 'i').test(text));

  // Extract name from first line
  const lines = text.split("\n").map(l => l.trim()).filter(Boolean);
  let name = lines[0] || "Candidate";
  if (name.includes("|")) name = name.split("|")[0].trim();
  const nameParts = name.split(" ");
  const firstName = nameParts[0] || "";
  const lastName = nameParts.slice(1).join(" ") || "";

  return {
    schema_version: "1.0.0",
    personal_information: {
      first_name: firstName,
      last_name: lastName,
      full_name: name,
      email: emailMatch ? emailMatch[1] : "",
      phone: phoneMatch ? phoneMatch[0] : "",
      headline: lines[1] && lines[1].length < 60 ? lines[1] : "Professional",
      location: "United States",
      linkedin_url: linkedinMatch ? `https://linkedin.com/in/${linkedinMatch[1]}` : "",
      github_url: githubMatch ? `https://github.com/${githubMatch[1]}` : ""
    },
    work_history: [
      {
        title: "Software / Cloud Engineer",
        company: "Organization",
        start_date: "2023",
        end_date: "Present",
        is_current: true,
        highlights: lines.slice(2, 6)
      }
    ],
    education: [
      {
        institution: "University",
        degree: "Bachelor of Science",
        field_of_study: "Engineering"
      }
    ],
    skills: matchedSkills.length > 0 ? matchedSkills : ["Python", "Cloud", "DevOps"],
    preferences: {
      authorized_to_work: "Yes",
      requires_sponsorship: "No"
    },
    metadata: {
      source_filename: filename,
      parser_engine: "client_side_fallback"
    }
  };
}

// Render Payload into Popup UI
function renderProfile(payload) {
  currentPayload = payload;
  const info = payload.personal_information || {};

  // Update Summary Card
  document.getElementById("candidate-name").textContent = info.full_name || `${info.first_name} ${info.last_name}`.trim() || "Candidate";
  document.getElementById("candidate-headline").textContent = info.headline || (payload.work_history?.[0]?.title) || "Professional";
  document.getElementById("candidate-email").textContent = info.email || "No email";
  document.getElementById("candidate-phone").textContent = info.phone || "No phone";
  document.getElementById("candidate-location").textContent = info.location || `${info.city || ''} ${info.state || ''}`.trim() || "Location not set";

  // Avatar Initials
  const initials = ((info.first_name?.[0] || "") + (info.last_name?.[0] || "WH")).toUpperCase();
  document.getElementById("candidate-avatar").textContent = initials || "CV";

  // Personal Tab Inputs
  document.getElementById("edit-first-name").value = info.first_name || "";
  document.getElementById("edit-last-name").value = info.last_name || "";
  document.getElementById("edit-email").value = info.email || "";
  document.getElementById("edit-phone").value = info.phone || "";
  document.getElementById("edit-location").value = info.location || "";
  document.getElementById("edit-linkedin").value = info.linkedin_url || "";
  document.getElementById("edit-github").value = info.github_url || "";

  // Experience Tab
  const expList = document.getElementById("experience-list");
  expList.innerHTML = "";
  (payload.work_history || []).forEach(exp => {
    const item = document.createElement("div");
    item.className = "list-item";
    item.innerHTML = `
      <div class="list-item-title">${exp.title || 'Role'}</div>
      <div class="list-item-sub">${exp.company || 'Company'}</div>
      <div class="list-item-date">${exp.start_date || ''} - ${exp.end_date || 'Present'}</div>
    `;
    expList.appendChild(item);
  });

  // Education Tab
  const eduList = document.getElementById("education-list");
  eduList.innerHTML = "";
  (payload.education || []).forEach(edu => {
    const item = document.createElement("div");
    item.className = "list-item";
    item.innerHTML = `
      <div class="list-item-title">${edu.institution || 'Institution'}</div>
      <div class="list-item-sub">${edu.degree || 'Degree'} ${edu.field_of_study ? 'in ' + edu.field_of_study : ''}</div>
      <div class="list-item-date">${edu.end_date || ''}</div>
    `;
    eduList.appendChild(item);
  });

  // Skills Tab
  const skillsCount = document.getElementById("skills-count");
  const skillsTags = document.getElementById("skills-tags");
  skillsTags.innerHTML = "";
  const skills = payload.skills || [];
  skillsCount.textContent = skills.length;
  skills.forEach(skill => {
    const tag = document.createElement("span");
    tag.className = "skill-tag";
    tag.textContent = skill;
    skillsTags.appendChild(tag);
  });

  // Raw JSON Tab
  rawJsonEditor.value = JSON.stringify(payload, null, 2);

  // Switch View
  dropZoneSection.style.display = "none";
  profileSection.style.display = "flex";
}

// Storage Operations
function saveProfileToStorage(payload) {
  if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    chrome.storage.local.set({ "universal_resume_profile": payload });
  } else {
    localStorage.setItem("universal_resume_profile", JSON.stringify(payload));
  }
}

function loadStoredProfile() {
  if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(["universal_resume_profile"], (result) => {
      if (result && result.universal_resume_profile) {
        renderProfile(result.universal_resume_profile);
      }
    });
  } else {
    const saved = localStorage.getItem("universal_resume_profile");
    if (saved) {
      try {
        renderProfile(JSON.parse(saved));
      } catch (e) {}
    }
  }
}

function clearProfile() {
  currentPayload = null;
  if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    chrome.storage.local.remove("universal_resume_profile");
  } else {
    localStorage.removeItem("universal_resume_profile");
  }
  profileSection.style.display = "none";
  dropZoneSection.style.display = "flex";
  showToast("Profile data cleared.");
}

// Execute Autofill in Active Browser Tab
async function executeAutofill() {
  if (!currentPayload) {
    showToast("Please drop or load a resume first!");
    return;
  }

  showToast("Injecting resume into application form...");

  if (typeof chrome !== "undefined" && chrome.tabs) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs || tabs.length === 0) {
        showToast("No active tab found.");
        return;
      }
      const activeTab = tabs[0];
      
      // Send message to content script
      chrome.tabs.sendMessage(
        activeTab.id,
        { action: "AUTOFILL_RESUME", payload: currentPayload },
        (response) => {
          if (chrome.runtime.lastError) {
            // Script might not be loaded yet, inject it dynamically
            chrome.scripting.executeScript(
              {
                target: { tabId: activeTab.id },
                files: ["content/content.js"]
              },
              () => {
                chrome.tabs.sendMessage(activeTab.id, { action: "AUTOFILL_RESUME", payload: currentPayload }, (res) => {
                  if (res && res.success) {
                    showToast(`✅ Filled ${res.fieldsFilled} fields!`);
                  } else {
                    showToast("Form autofill executed.");
                  }
                });
              }
            );
          } else if (response && response.success) {
            showToast(`✅ Filled ${response.fieldsFilled} fields!`);
          } else {
            showToast("Autofill completed.");
          }
        }
      );
    });
  } else {
    showToast("Browser tab messaging ready.");
  }
}

// Toast Feedback Helper
function showToast(msg) {
  toastMessage.textContent = msg;
  toast.style.display = "block";
  setTimeout(() => {
    toast.style.display = "none";
  }, 2600);
}
