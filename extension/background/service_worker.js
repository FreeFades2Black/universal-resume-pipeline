/**
 * Universal Resume Extension - Background Service Worker (Manifest V3)
 */

chrome.runtime.onInstalled.addListener((details) => {
  console.log("⚡ [Universal Resume Service Worker] Extension installed successfully.", details);

  // Set default badge state
  chrome.action.setBadgeText({ text: "⚡" });
  chrome.action.setBadgeBackgroundColor({ color: "#1f6feb" });

  // Create context menu for quick autofill
  if (chrome.contextMenus) {
    chrome.contextMenus.create({
      id: "universal-resume-autofill-menu",
      title: "⚡ Autofill Application with Universal Resume",
      contexts: ["page", "editable"]
    });
  }
});

// Handle context menu clicks
if (chrome.contextMenus) {
  chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "universal-resume-autofill-menu" && tab && tab.id) {
      chrome.storage.local.get(["universal_resume_profile"], (res) => {
        const payload = res.universal_resume_profile;
        if (payload) {
          chrome.tabs.sendMessage(tab.id, {
            action: "AUTOFILL_RESUME",
            payload: payload
          });
        } else {
          console.warn("No resume profile stored in extension yet.");
        }
      });
    }
  });
}
