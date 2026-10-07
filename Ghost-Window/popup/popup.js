// Ghost Mode Popup Script

const DEFAULT_CONFIG = {
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

let currentConfig = { ...DEFAULT_CONFIG };

// DOM Elements
const masterToggle = document.getElementById('masterToggle');
const opacitySlider = document.getElementById('opacitySlider');
const opacityVal = document.getElementById('opacityVal');
const brightnessSlider = document.getElementById('brightnessSlider');
const brightnessVal = document.getElementById('brightnessVal');
const contrastSlider = document.getElementById('contrastSlider');
const contrastVal = document.getElementById('contrastVal');
const blurSlider = document.getElementById('blurSlider');
const blurVal = document.getElementById('blurVal');

const blurMediaToggle = document.getElementById('blurMediaToggle');
const grayscaleToggle = document.getElementById('grayscaleToggle');
const spotlightToggle = document.getElementById('spotlightToggle');
const idleFadeToggle = document.getElementById('idleFadeToggle');
const stealthFontToggle = document.getElementById('stealthFontToggle');

const panicTypeSelect = document.getElementById('panicTypeSelect');
const testPanicBtn = document.getElementById('testPanicBtn');
const presetButtons = document.querySelectorAll('.preset-btn');
const blurChips = document.querySelectorAll('.chip-btn');
const resetBtn = document.getElementById('resetBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.local.get(DEFAULT_CONFIG, (stored) => {
    currentConfig = { ...DEFAULT_CONFIG, ...stored };
    updateUI();
    attachEventListeners();
  });
});

// Update UI elements based on currentConfig
function updateUI() {
  masterToggle.checked = currentConfig.enabled;

  opacitySlider.value = currentConfig.opacity;
  opacityVal.textContent = `${currentConfig.opacity}%`;

  brightnessSlider.value = currentConfig.brightness;
  brightnessVal.textContent = `${currentConfig.brightness}%`;

  contrastSlider.value = currentConfig.contrast;
  contrastVal.textContent = `${currentConfig.contrast}%`;

  blurSlider.value = currentConfig.blur;
  blurVal.textContent = `${currentConfig.blur}px`;

  blurMediaToggle.checked = !!currentConfig.blurMedia;
  grayscaleToggle.checked = !!currentConfig.grayscale;
  spotlightToggle.checked = !!currentConfig.spotlightMode;
  idleFadeToggle.checked = !!currentConfig.idleFade;
  stealthFontToggle.checked = !!currentConfig.stealthFont;

  panicTypeSelect.value = currentConfig.panicScreenType || 'fake_docs';

  updatePresetHighlight();
  updateBlurChipHighlight();
}

// Save config and notify active tab
function saveAndNotify() {
  chrome.storage.local.set(currentConfig);
  notifyActiveTab();
}

// Send update to content script immediately
async function notifyActiveTab() {
  try {
    const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (activeTab && activeTab.id) {
      chrome.tabs.sendMessage(activeTab.id, {
        action: 'update_config',
        config: currentConfig
      }).catch(() => {});
    }
  } catch (e) {
    // Ignore error if tab is chrome:// or unsupported
  }
}

// Attach Event Listeners
function attachEventListeners() {
  // Master Toggle
  masterToggle.addEventListener('change', () => {
    currentConfig.enabled = masterToggle.checked;
    saveAndNotify();
  });

  // Opacity Slider (1% - 100%)
  opacitySlider.addEventListener('input', () => {
    currentConfig.opacity = parseInt(opacitySlider.value, 10);
    opacityVal.textContent = `${currentConfig.opacity}%`;
    if (!currentConfig.enabled) {
      currentConfig.enabled = true;
      masterToggle.checked = true;
    }
    updatePresetHighlight();
    saveAndNotify();
  });

  // Brightness Slider
  brightnessSlider.addEventListener('input', () => {
    currentConfig.brightness = parseInt(brightnessSlider.value, 10);
    brightnessVal.textContent = `${currentConfig.brightness}%`;
    saveAndNotify();
  });

  // Contrast Slider
  contrastSlider.addEventListener('input', () => {
    currentConfig.contrast = parseInt(contrastSlider.value, 10);
    contrastVal.textContent = `${currentConfig.contrast}%`;
    saveAndNotify();
  });

  // Blur Slider (0px - 30px)
  blurSlider.addEventListener('input', () => {
    currentConfig.blur = parseFloat(blurSlider.value);
    blurVal.textContent = `${currentConfig.blur}px`;
    if (!currentConfig.enabled && currentConfig.blur > 0) {
      currentConfig.enabled = true;
      masterToggle.checked = true;
    }
    updateBlurChipHighlight();
    updatePresetHighlight();
    saveAndNotify();
  });

  // Blur Quick Chips
  blurChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      const bVal = parseFloat(chip.getAttribute('data-blur'));
      currentConfig.blur = bVal;
      blurSlider.value = bVal;
      blurVal.textContent = `${bVal}px`;
      if (!currentConfig.enabled) {
        currentConfig.enabled = true;
        masterToggle.checked = true;
      }
      updateBlurChipHighlight();
      updatePresetHighlight();
      saveAndNotify();
    });
  });

  // Feature Toggles
  blurMediaToggle.addEventListener('change', () => {
    currentConfig.blurMedia = blurMediaToggle.checked;
    saveAndNotify();
  });

  grayscaleToggle.addEventListener('change', () => {
    currentConfig.grayscale = grayscaleToggle.checked;
    saveAndNotify();
  });

  spotlightToggle.addEventListener('change', () => {
    currentConfig.spotlightMode = spotlightToggle.checked;
    saveAndNotify();
  });

  idleFadeToggle.addEventListener('change', () => {
    currentConfig.idleFade = idleFadeToggle.checked;
    saveAndNotify();
  });

  stealthFontToggle.addEventListener('change', () => {
    currentConfig.stealthFont = stealthFontToggle.checked;
    saveAndNotify();
  });

  // Panic Screen Type
  panicTypeSelect.addEventListener('change', () => {
    currentConfig.panicScreenType = panicTypeSelect.value;
    saveAndNotify();
  });

  // Preset Buttons
  presetButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const opacityValInt = parseInt(btn.getAttribute('data-opacity'), 10);
      currentConfig.opacity = opacityValInt;
      currentConfig.enabled = true;
      opacitySlider.value = opacityValInt;
      opacityVal.textContent = `${opacityValInt}%`;

      if (btn.hasAttribute('data-blur')) {
        const blurValFloat = parseFloat(btn.getAttribute('data-blur'));
        currentConfig.blur = blurValFloat;
        blurSlider.value = blurValFloat;
        blurVal.textContent = `${blurValFloat}px`;
      }

      masterToggle.checked = true;
      updateBlurChipHighlight();
      updatePresetHighlight();
      saveAndNotify();
    });
  });

  // Test Panic Button
  testPanicBtn.addEventListener('click', async () => {
    currentConfig.panicMode = !currentConfig.panicMode;
    chrome.storage.local.set({ panicMode: currentConfig.panicMode });
    try {
      const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (activeTab && activeTab.id) {
        chrome.tabs.sendMessage(activeTab.id, {
          action: 'panic_boss_key'
        }).catch(() => {});
      }
    } catch (e) {}
    window.close(); // Close popup so user sees the panic screen immediately
  });

  // Reset Button
  resetBtn.addEventListener('click', () => {
    currentConfig = { ...DEFAULT_CONFIG };
    chrome.storage.local.set(DEFAULT_CONFIG);
    updateUI();
    saveAndNotify();
  });
}

function updatePresetHighlight() {
  presetButtons.forEach((btn) => {
    const btnOpacity = parseInt(btn.getAttribute('data-opacity'), 10);
    const hasBlur = btn.hasAttribute('data-blur');
    if (hasBlur) {
      const btnBlur = parseFloat(btn.getAttribute('data-blur'));
      btn.classList.toggle('active', btnOpacity === currentConfig.opacity && Math.abs(btnBlur - currentConfig.blur) < 0.1);
    } else {
      btn.classList.toggle('active', btnOpacity === currentConfig.opacity && currentConfig.blur === 0);
    }
  });
}

function updateBlurChipHighlight() {
  blurChips.forEach((chip) => {
    const chipVal = parseFloat(chip.getAttribute('data-blur'));
    chip.classList.toggle('active', Math.abs(chipVal - currentConfig.blur) < 0.1);
  });
}
