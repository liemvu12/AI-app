// Ghost Mode Content Script
(() => {
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
  let idleTimer = null;
  let hudTimeout = null;

  // Initialize config
  function init() {
    chrome.storage.local.get(DEFAULT_CONFIG, (stored) => {
      currentConfig = { ...DEFAULT_CONFIG, ...stored };
      applyConfig();
      setupEventListeners();
    });
  }

  // Apply configuration to DOM
  function applyConfig() {
    const root = document.documentElement;
    if (!root) return;

    if (currentConfig.enabled) {
      root.classList.add('ghost-mode-enabled');
      root.style.setProperty('--ghost-opacity', (currentConfig.opacity / 100).toString());
      root.style.setProperty('--ghost-brightness', (currentConfig.brightness / 100).toString());
      root.style.setProperty('--ghost-contrast', (currentConfig.contrast / 100).toString());
      root.style.setProperty('--ghost-blur', `${currentConfig.blur}px`);
      root.style.setProperty('--ghost-spotlight-radius', `${currentConfig.spotlightRadius}px`);

      root.classList.toggle('ghost-grayscale', !!currentConfig.grayscale);
      root.classList.toggle('ghost-blur-media', !!currentConfig.blurMedia);
      root.classList.toggle('ghost-stealth-font', !!currentConfig.stealthFont);
      root.classList.toggle('ghost-spotlight-active', !!currentConfig.spotlightMode);

      // Ensure root background matches body background to avoid white flashes on low opacity
      if (document.body) {
        const bodyBg = window.getComputedStyle(document.body).backgroundColor;
        if (bodyBg && bodyBg !== 'rgba(0, 0, 0, 0)' && bodyBg !== 'transparent') {
          root.style.backgroundColor = bodyBg;
        }
      }
    } else {
      root.classList.remove(
        'ghost-mode-enabled',
        'ghost-grayscale',
        'ghost-blur-media',
        'ghost-stealth-font',
        'ghost-spotlight-active',
        'ghost-idle-active'
      );
      root.style.removeProperty('--ghost-opacity');
      root.style.removeProperty('--ghost-brightness');
      root.style.removeProperty('--ghost-contrast');
      root.style.removeProperty('--ghost-blur');
      root.style.removeProperty('--ghost-spotlight-radius');
      root.style.removeProperty('background-color');
    }

    handlePanicOverlay();
    resetIdleTimer();
  }

  // Manage Boss Key / Panic Screen Overlay
  function handlePanicOverlay() {
    let overlay = document.getElementById('ghost-panic-overlay');

    if (currentConfig.panicMode) {
      if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'ghost-panic-overlay';
        (document.documentElement || document.body).appendChild(overlay);

        overlay.addEventListener('dblclick', () => {
          currentConfig.panicMode = false;
          chrome.storage.local.set({ panicMode: false });
          applyConfig();
          showHud('🛡️ Đã thoát Boss Key', 1500);
        });
      }

      overlay.className = 'ghost-panic-active';
      overlay.innerHTML = getPanicContent(currentConfig.panicScreenType);
      
      switch (currentConfig.panicScreenType) {
        case 'blank_white':
          overlay.classList.add('ghost-screen-white');
          break;
        case 'blank_black':
          overlay.classList.add('ghost-screen-black');
          break;
        case 'fake_code':
          overlay.classList.add('ghost-screen-code');
          break;
        case 'fake_excel':
          overlay.classList.add('ghost-screen-excel');
          break;
        case 'fake_docs':
        default:
          overlay.classList.add('ghost-screen-docs');
          break;
      }
    } else {
      if (overlay) {
        overlay.className = '';
        overlay.style.display = 'none';
      }
    }
  }

  // Generate realistic camouflage template HTML
  function getPanicContent(type) {
    switch (type) {
      case 'blank_white':
      case 'blank_black':
        return '';

      case 'fake_code':
        return `
          <div class="ghost-fake-code-tab">📄 data_processor.py</div>
          <pre><code><span style="color:#569cd6;">import</span> sys
<span style="color:#569cd6;">import</span> os
<span style="color:#569cd6;">import</span> json
<span style="color:#569cd6;">import</span> logging
<span style="color:#569cd6;">from</span> datetime <span style="color:#569cd6;">import</span> datetime

<span style="color:#6a9955;"># Configure enterprise telemetry and analytics pipeline</span>
logging.basicConfig(level=logging.INFO, format=<span style="color:#ce9178;">'%(asctime)s - %(levelname)s - %(message)s'</span>)
logger = logging.getLogger(__name__)

<span style="color:#569cd6;">class</span> <span style="color:#4ec9b0;">EnterpriseDataPipeline</span>:
    <span style="color:#569cd6;">def</span> <span style="color:#dcdcaa;">__init__</span>(<span style="color:#9cdcfe;">self</span>, <span style="color:#9cdcfe;">config_path</span>: <span style="color:#4ec9b0;">str</span>):
        <span style="color:#9cdcfe;">self</span>.config_path = config_path
        <span style="color:#9cdcfe;">self</span>.is_active = <span style="color:#569cd6;">True</span>
        <span style="color:#9cdcfe;">self</span>.records_processed = 0

    <span style="color:#569cd6;">def</span> <span style="color:#dcdcaa;">load_and_validate</span>(<span style="color:#9cdcfe;">self</span>, <span style="color:#9cdcfe;">batch_size</span>: <span style="color:#4ec9b0;">int</span> = 1000):
        <span style="color:#6a9955;">\"\"\"Execute parallel ingestion and schema validation.\"\"\"</span>
        logger.info(<span style="color:#ce9178;">f"Initializing data stream sync with batch size: {batch_size}"</span>)
        <span style="color:#569cd6;">return</span> {<span style="color:#ce9178;">"status"</span>: <span style="color:#ce9178;">"OK"</span>, <span style="color:#ce9178;">"sync_time"</span>: datetime.now().isoformat()}

<span style="color:#569cd6;">if</span> __name__ == <span style="color:#ce9178;">'__main__'</span>:
    pipeline = EnterpriseDataPipeline(<span style="color:#ce9178;">"/etc/config/cluster_settings.yaml"</span>)
    pipeline.load_and_validate()
</code></pre>
        `;

      case 'fake_excel':
        return `
          <div class="ghost-excel-toolbar">📊 Microsoft Excel - Bao_Cao_Thong_Ke_Q3_2026.xlsx</div>
          <table class="ghost-excel-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Mã Dự Án</th>
                <th>Hạng Mục Công Việc</th>
                <th>Phòng Ban</th>
                <th>Ngân Sách (VND)</th>
                <th>Tiến Độ</th>
                <th>Trạng Thái</th>
                <th>Ghi Chú</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>1</td><td>PRJ-2026-001</td><td>Tối ưu hóa hạ tầng Cloud Kubernetes</td><td>Kỹ Thuật</td><td>185,000,000</td><td>85%</td><td>Đang triển khai</td><td>Đạt KPI Q3</td>
              </tr>
              <tr>
                <td>2</td><td>PRJ-2026-002</td><td>Bảo trì cơ sở dữ liệu định kỳ</td><td>Vận Hành</td><td>45,000,000</td><td>100%</td><td>Hoàn thành</td><td>Không lỗi phát sinh</td>
              </tr>
              <tr>
                <td>3</td><td>PRJ-2026-003</td><td>Kiểm toán bảo mật hệ thống thông tin</td><td>An Toàn</td><td>120,000,000</td><td>60%</td><td>Đang đánh giá</td><td>Báo cáo sơ bộ OK</td>
              </tr>
              <tr>
                <td>4</td><td>PRJ-2026-004</td><td>Nâng cấp máy chủ backup dự phòng</td><td>Hạ Tầng</td><td>95,000,000</td><td>40%</td><td>Chờ duyệt</td><td>Chờ phê duyệt từ BGĐ</td>
              </tr>
              <tr>
                <td>5</td><td>PRJ-2026-005</td><td>Đào tạo nghiệp vụ an ninh mạng</td><td>Nhân Sự</td><td>30,000,000</td><td>90%</td><td>Đang diễn ra</td><td>Tuần 3 tháng 8</td>
              </tr>
            </tbody>
          </table>
        `;

      case 'fake_docs':
      default:
        return `
          <div class="ghost-fake-doc-header">📝 Tài liệu nội bộ công ty - Kế hoạch công tác & Báo cáo tiến độ</div>
          <div class="ghost-fake-doc-body">
            <h1>BÁO CÁO TỔNG KẾT VẬN HÀNH & KẾ HOẠCH HÀNH ĐỘNG CHI TIẾT</h1>
            <p><strong>Người lập báo cáo:</strong> Ban Điều Hành Dự Án</p>
            <p><strong>Ngày cập nhật:</strong> ${new Date().toLocaleDateString('vi-VN')}</p>
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 16px 0;" />
            <p><strong>1. Đánh giá tổng quan quý hiện tại:</strong> Toàn bộ các chỉ tiêu chất lượng dịch vụ (SLA) đều đạt ngưỡng 99.8%. Các phòng ban chuyên môn phối hợp đồng bộ, giảm thiểu tối đa độ trễ trong quy trình xử lý văn bản và báo cáo định kỳ.</p>
            <p><strong>2. Nhiệm vụ trọng tâm trong tuần tiếp theo:</strong></p>
            <ul>
              <li>Tiếp tục rà soát các danh mục rủi ro hoạt động và đề xuất phương án dự phòng.</li>
              <li>Chuẩn hóa biểu mẫu quy trình kiểm toán nội bộ theo tiêu chuẩn mới.</li>
              <li>Hoàn tất hồ sơ nghiệm thu kỹ thuật các hạng mục đã hoàn thành.</li>
            </ul>
            <p><em>(Nhấn phím tắt Alt+Z hoặc bấm đúp chuột vào màn hình để quay lại chế độ duyệt web)</em></p>
          </div>
        `;
    }
  }

  // Idle Timer logic
  function resetIdleTimer() {
    if (idleTimer) clearTimeout(idleTimer);

    if (currentConfig.enabled && currentConfig.idleFade) {
      document.documentElement.classList.remove('ghost-idle-active');
      idleTimer = setTimeout(() => {
        if (currentConfig.enabled && currentConfig.idleFade) {
          document.documentElement.classList.add('ghost-idle-active');
        }
      }, (currentConfig.idleFadeTimeout || 5) * 1000);
    } else {
      document.documentElement.classList.remove('ghost-idle-active');
    }
  }

  // Show HUD toast in bottom corner
  function showHud(text, duration = 1500) {
    let hud = document.getElementById('ghost-mode-hud');
    if (!hud) {
      hud = document.createElement('div');
      hud.id = 'ghost-mode-hud';
      (document.documentElement || document.body).appendChild(hud);
    }

    hud.innerHTML = `<span class="ghost-hud-icon">👻</span><span>${text}</span>`;
    hud.classList.add('ghost-hud-visible');

    if (hudTimeout) clearTimeout(hudTimeout);
    hudTimeout = setTimeout(() => {
      hud.classList.remove('ghost-hud-visible');
    }, duration);
  }

  // Setup Event Listeners
  function setupEventListeners() {
    // Mouse movement for Spotlight & Idle reset
    window.addEventListener(
      'mousemove',
      (e) => {
        if (currentConfig.enabled && currentConfig.spotlightMode) {
          document.documentElement.style.setProperty('--ghost-spotlight-x', `${e.clientX}px`);
          document.documentElement.style.setProperty('--ghost-spotlight-y', `${e.clientY}px`);
        }
        resetIdleTimer();
      },
      { passive: true }
    );

    // Keyboard & scroll activity resets idle
    window.addEventListener('keydown', resetIdleTimer, { passive: true });
    window.addEventListener('scroll', resetIdleTimer, { passive: true });

    // In-page keyboard shortcuts
    window.addEventListener('keydown', (e) => {
      // Check Alt+X (Toggle Ghost Mode)
      if (e.altKey && (e.key === 'x' || e.key === 'X')) {
        e.preventDefault();
        toggleGhostMode();
      }
      // Check Alt+Z (Boss Key)
      else if (e.altKey && (e.key === 'z' || e.key === 'Z')) {
        e.preventDefault();
        togglePanicMode();
      }
      // Check Alt+Up (Increase Opacity / Tăng độ rõ)
      else if (e.altKey && e.key === 'ArrowUp') {
        e.preventDefault();
        changeOpacity(5);
      }
      // Check Alt+Down (Decrease Opacity / Giảm độ rõ - Trong suốt hơn)
      else if (e.altKey && e.key === 'ArrowDown') {
        e.preventDefault();
        changeOpacity(-5);
      }
      // Check Alt+M (Toggle Media Blur)
      else if (e.altKey && (e.key === 'm' || e.key === 'M')) {
        e.preventDefault();
        toggleMediaBlur();
      }
      // Check Alt+B (Toggle Heavy Blur / Sương mù)
      else if (e.altKey && (e.key === 'b' || e.key === 'B')) {
        e.preventDefault();
        toggleHeavyBlur();
      }
      // Check Alt+[ (Decrease Blur)
      else if (e.altKey && (e.key === '[' || e.key === '{')) {
        e.preventDefault();
        changeBlur(-2);
      }
      // Check Alt+] (Increase Blur)
      else if (e.altKey && (e.key === ']' || e.key === '}')) {
        e.preventDefault();
        changeBlur(2);
      }
    });

    // Listen to background service worker messages
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'toggle_ghost_mode') {
        toggleGhostMode();
      } else if (request.action === 'panic_boss_key') {
        togglePanicMode();
      } else if (request.action === 'decrease_opacity') {
        changeOpacity(-5);
      } else if (request.action === 'increase_opacity') {
        changeOpacity(5);
      } else if (request.action === 'toggle_media_blur') {
        toggleMediaBlur();
      } else if (request.action === 'toggle_blur') {
        toggleHeavyBlur();
      } else if (request.action === 'decrease_blur') {
        changeBlur(-2);
      } else if (request.action === 'increase_blur') {
        changeBlur(2);
      } else if (request.action === 'update_config') {
        currentConfig = { ...currentConfig, ...request.config };
        applyConfig();
      }
      sendResponse({ status: 'ok', config: currentConfig });
      return true;
    });

    // Sync storage changes across tabs
    chrome.storage.onChanged.addListener((changes, area) => {
      if (area === 'local') {
        let changed = false;
        for (const key of Object.keys(changes)) {
          if (key in currentConfig) {
            currentConfig[key] = changes[key].newValue;
            changed = true;
          }
        }
        if (changed) {
          applyConfig();
        }
      }
    });
  }

  // Quick Action Helpers
  function toggleGhostMode() {
    currentConfig.enabled = !currentConfig.enabled;
    chrome.storage.local.set({ enabled: currentConfig.enabled });
    applyConfig();
    showHud(currentConfig.enabled ? `Chế độ Tàng hình: BẬT (${currentConfig.opacity}%)` : 'Chế độ Tàng hình: TẮT');
  }

  function togglePanicMode() {
    currentConfig.panicMode = !currentConfig.panicMode;
    chrome.storage.local.set({ panicMode: currentConfig.panicMode });
    applyConfig();
    if (!currentConfig.panicMode) {
      showHud('🛡️ Đã tắt Boss Key');
    }
  }

  function changeOpacity(delta) {
    if (!currentConfig.enabled) {
      currentConfig.enabled = true;
    }
    let newOpacity = Math.max(1, Math.min(100, currentConfig.opacity + delta));
    currentConfig.opacity = newOpacity;
    chrome.storage.local.set({ opacity: newOpacity, enabled: true });
    applyConfig();
    showHud(`👁️ Độ rõ: ${newOpacity}%`);
  }

  function changeBlur(delta) {
    if (!currentConfig.enabled) {
      currentConfig.enabled = true;
    }
    let newBlur = Math.max(0, Math.min(30, Math.round((currentConfig.blur + delta) * 2) / 2));
    currentConfig.blur = newBlur;
    chrome.storage.local.set({ blur: newBlur, enabled: true });
    applyConfig();
    showHud(`🌫️ Làm mờ viền: ${newBlur}px`);
  }

  function toggleHeavyBlur() {
    if (!currentConfig.enabled) {
      currentConfig.enabled = true;
    }
    if (currentConfig.blur > 0) {
      currentConfig.blur = 0;
      showHud('🌫️ Mờ viền: TẮT (0px)');
    } else {
      currentConfig.blur = 12;
      showHud('🌫️ Mờ sương mù: BẬT (12px)');
    }
    chrome.storage.local.set({ blur: currentConfig.blur, enabled: true });
    applyConfig();
  }

  function toggleMediaBlur() {
    currentConfig.blurMedia = !currentConfig.blurMedia;
    chrome.storage.local.set({ blurMedia: currentConfig.blurMedia });
    applyConfig();
    showHud(currentConfig.blurMedia ? '🖼️ Làm mờ ảnh/video: BẬT' : '🖼️ Làm mờ ảnh/video: TẮT');
  }

  // Start extension logic
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
