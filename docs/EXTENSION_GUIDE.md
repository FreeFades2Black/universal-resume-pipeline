# Browser Extension Installation & Developer Guide

This guide explains how to install, run, and test the **Universal Resume Autofill Engine** in Chrome, Microsoft Edge, Brave, and other Chromium-based browsers.

---

## 1. Quick Installation (Developer Mode)

1. Open your browser and navigate to the Extensions page:
   - **Google Chrome / Brave**: `chrome://extensions/`
   - **Microsoft Edge**: `edge://extensions/`
2. Enable **Developer mode** (toggle located at top-right on Chrome, or left sidebar on Edge).
3. Click the **"Load unpacked"** button.
4. Select the `extension/` directory from this repository:
   ```
   C:\Users\FreeF\projects\universal-resume-pipeline\extension
   ```
5. The **Universal Resume Autofill Engine** icon (⚡) will now appear in your browser toolbar!

---

## 2. Using the Extension

### Step 1: Ingest Your Resume
- Click the **⚡** icon in your browser toolbar to open the popup.
- **Drag and drop** your resume file (`.pdf`, `.docx`, `.txt`, `.json`) into the Drop Zone.
- *Alternatively, click **"Load William Free Hall Sample"** for instant demo data.*

### Step 2: Review & Edit
- Review your extracted details across the **Personal**, **Experience**, **Education**, **Skills**, and **JSON** tabs.
- Any edits made in the form or JSON editor are automatically persisted in `chrome.storage.local`.

### Step 3: One-Click Autofill
- Navigate to any job application page (Greenhouse, Lever, Workday, Ashby, or custom employer forms).
- Open the extension popup and click:
  ```
  🚀 Autofill Current Application Tab
  ```
- The fields on the host webpage will fill instantly with high-accuracy values, highlighted with a green outline and a confirmation toast banner.

---

## 3. Backend Mode vs Standalone Mode

- **Standalone Mode (Zero Setup)**: Works completely offline with zero servers running using the built-in client-side regex heuristics.
- **Backend Mode (High Accuracy)**: Start the Python FastAPI server (`python -m backend.app.main`) to enable deep multi-engine parsing and optional LLM neural extraction.
