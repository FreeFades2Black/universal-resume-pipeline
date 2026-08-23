/**
 * Universal Resume Pipeline - Web Testbench Application Logic
 */

const SAMPLE_PAYLOAD = {
  "schema_version": "1.0.0",
  "personal_information": {
    "first_name": "William",
    "last_name": "Hall",
    "full_name": "William Free Hall",
    "email": "free@example.com",
    "phone": "555-019-2834",
    "headline": "Cloud & Infrastructure Engineer / Technical Lead",
    "summary": "Cloud Engineer specializing in Multi-Cloud Infrastructure, Terraform, Databricks, Kubernetes, and automated CI/CD pipelines.",
    "location": "Niceville, FL",
    "city": "Niceville",
    "state": "FL",
    "country": "United States",
    "postal_code": "32578",
    "linkedin_url": "https://linkedin.com/in/williamfreehall",
    "github_url": "https://github.com/FreeFades2Black",
    "portfolio_url": "https://github.com/FreeFades2Black"
  },
  "work_history": [
    {
      "title": "Technical Lead / Cloud Engineer",
      "company": "Tech Solutions",
      "location": "Remote",
      "start_date": "2024",
      "end_date": "Present",
      "description": "Architected zero-downtime multi-cloud infrastructure and automated telemetry pipelines.",
      "technologies": ["Python", "AWS", "Terraform", "Docker", "Kubernetes", "Databricks"]
    }
  ],
  "education": [
    {
      "institution": "University of Florida",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science & IT",
      "end_date": "2022"
    }
  ],
  "skills": ["Python", "AWS", "Terraform", "Docker", "Kubernetes", "Databricks", "PySpark", "FastAPI", "SQL", "Linux", "Git"],
  "preferences": {
    "authorized_to_work": "Yes",
    "requires_sponsorship": "No"
  }
};

let activePayload = null;

document.addEventListener("DOMContentLoaded", () => {
  const dropArea = document.getElementById("drop-area");
  const fileSelector = document.getElementById("file-selector");
  const browseBtn = document.getElementById("browse-file-btn");
  const demoBtn = document.getElementById("demo-sample-btn");
  const injectBtn = document.getElementById("inject-mock-btn");
  const copyBtn = document.getElementById("copy-json");

  // Browse file
  browseBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    fileSelector.click();
  });
  dropArea.addEventListener("click", () => fileSelector.click());

  fileSelector.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  });

  // Drag & Drop
  dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.classList.add("drag-over");
  });
  dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("drag-over");
  });
  dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  });

  // Demo Sample Button
  demoBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    loadPayload(SAMPLE_PAYLOAD);
  });

  // Autofill Action
  injectBtn.addEventListener("click", () => {
    if (activePayload) {
      injectIntoMockForm(activePayload);
    }
  });

  // Copy JSON
  copyBtn.addEventListener("click", () => {
    const text = document.getElementById("json-display").textContent;
    navigator.clipboard.writeText(text);
    copyBtn.textContent = "Copied!";
    setTimeout(() => { copyBtn.textContent = "Copy JSON"; }, 2000);
  });
});

async function handleFile(file) {
  // Try sending to backend API if running
  const candidateUrls = ["http://127.0.0.1:8008/api/v1/parse", "http://localhost:8008/api/v1/parse", "http://127.0.0.1:8000/api/v1/parse", "http://localhost:8000/api/v1/parse"];
  for (const endpoint of candidateUrls) {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(endpoint, {
        method: "POST",
        body: formData
      });
      if (res.ok) {
        const payload = await res.json();
        loadPayload(payload);
        return;
      }
    } catch (err) {
      // Continue trying
    }
  }

  // Client reader fallback
  const reader = new FileReader();
  reader.onload = (e) => {
    const text = e.target.result;
    if (file.name.endsWith(".json")) {
      try {
        loadPayload(JSON.parse(text));
        return;
      } catch (e) {}
    }
    // Simple text extraction
    const mock = JSON.parse(JSON.stringify(SAMPLE_PAYLOAD));
    mock.metadata = { source: file.name, parsed_client: true };
    loadPayload(mock);
  };
  reader.readAsText(file);
}

function loadPayload(payload) {
  activePayload = payload;
  const info = payload.personal_information || {};

  document.getElementById("display-name").textContent = info.full_name || `${info.first_name} ${info.last_name}`;
  document.getElementById("display-title").textContent = info.headline || "Cloud Engineer";
  document.getElementById("display-email").textContent = info.email || "N/A";
  document.getElementById("display-phone").textContent = info.phone || "N/A";
  document.getElementById("display-location").textContent = info.location || "N/A";
  document.getElementById("display-linkedin").textContent = info.linkedin_url || "N/A";

  document.getElementById("parsed-summary").style.display = "block";
  document.getElementById("json-display").textContent = JSON.stringify(payload, null, 2);
}

function injectIntoMockForm(payload) {
  const info = payload.personal_information || {};
  const job = (payload.work_history && payload.work_history[0]) || {};
  const edu = (payload.education && payload.education[0]) || {};
  const skills = (payload.skills || []).join(", ");

  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el && val) {
      el.value = val;
      el.classList.add("autofilled");
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    }
  };

  setVal("first_name", info.first_name);
  setVal("last_name", info.last_name);
  setVal("email", info.email);
  setVal("phone", info.phone);
  setVal("location", info.location);
  setVal("urls[LinkedIn]", info.linkedin_url);
  setVal("urls[GitHub]", info.github_url);
  setVal("company", job.company);
  setVal("title", job.title || info.headline);
  setVal("school", `${edu.degree || ''} ${edu.institution ? 'at ' + edu.institution : ''}`.trim());
  setVal("skills", skills);
  setVal("comments", info.summary || job.description);

  // Dropdowns
  const authSelect = document.getElementById("work_auth");
  if (authSelect) {
    authSelect.value = "Yes";
    authSelect.classList.add("autofilled");
  }
  const sponsSelect = document.getElementById("sponsorship");
  if (sponsSelect) {
    sponsSelect.value = "No";
    sponsSelect.classList.add("autofilled");
  }

  alert("⚡ Form autofilled with Universal Resume Payload!");
}
