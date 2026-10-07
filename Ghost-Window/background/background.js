// Ghost Mode Background Service Worker (Manifest V3)

const DEFAULT_SETTINGS = {
  enabled: true,
  opacity: 35,
  brightness: 85,
  contrast: 80,
  blur: 0,
  grayscale: false,
  blurMedia: true,
  stealthFont: false,
  idleFade: false,
  idleFadeTimeout: 5,
  spotlightMode: false,
  spotlightRadius: 180,
  panicMode: false,
  panicScreenType: 'fake_docs'
};

// Initialize settings on installation
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(null, (existing) => {
    const toSet = {};
    for (const key in DEFAULT_SETTINGS) {
      if (existing[key] === undefined) {
        toSet[key] = DEFAULT_SETTINGS[key];
      }
    }
    if (Object.keys(toSet).length > 0) {
      chrome.storage.local.set(toSet);
    }
  });
});

// Handle global keyboard shortcuts
chrome.commands.onCommand.addListener(async (command) => {
  try {
    const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!activeTab || !activeTab.id || activeTab.url?.startsWith('chrome://') || activeTab.url?.startsWith('edge://')) {
      return;
    }

    chrome.tabs.sendMessage(activeTab.id, { action: command }, (response) => {
      if (chrome.runtime.lastError) {
        // Tab might not have content script yet or is restricted page
      }
    });
  } catch (err) {
    console.error('Error dispatching command:', err);
  }
});
