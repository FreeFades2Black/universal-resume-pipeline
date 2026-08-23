# Universal Resume Autofill Extension (Manifest V3)

A Chrome & Edge extension that extracts unstructured resumes into structured JSON and injects candidate data directly into ATS application forms.

## Directory Layout
- `manifest.json`: Manifest V3 declaration.
- `popup/`: Popup UI with Drop Zone, structured review tabs, and autofill triggers.
- `content/`: Injected content script matching DOM selectors and firing synthetic events.
- `background/`: Service worker for badge states and context menus.
- `icons/`: Extension icon set (16x16, 48x48, 128x128).

## Quickstart
1. Go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and choose this folder.
