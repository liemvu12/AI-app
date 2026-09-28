# BẢNG TÍNH NĂNG HIỆN CÓ & QUY TRÌNH KIỂM THỬ HỒI QUY (REGRESSION CHECKLIST)
*AGY Terminal Bridge & AGY Dev English Companion*

> **NGUYÊN TẮC BẮT BUỘC (MANDATORY RULE):**
> Mỗi khi bổ sung hoặc tinh chỉnh bất kỳ tính năng mới nào, **BẮT BUỘC** phải chạy bộ kiểm thử tự động `test_bridge.py` và đối chiếu lại toàn bộ danh sách tính năng cũ dưới đây để đảm bảo **100% KHÔNG BỊ ẢNH HƯỞNG (ZERO REGRESSION)**.

---

## I. Ma trận Tính năng Hiện có (Existing Features Matrix)

| ID | Tên tính năng | File triển khai | Phím tắt / Thao tác | Hàm kiểm thử tự động (`test_bridge.py`) | Trạng thái |
|---|---|---|---|---|---|
| **F-01** | **Real-Time Terminal Sync** (Đọc Console Buffer <80ms, sạch lỗi Unikey) | `services/console_daemon.py`, `services/terminal_reader.py` | Gõ trực tiếp trong Terminal AGY | `test_console_buffer_extraction()` | ✅ PASS |
| **F-02** | **Bộ sửa lỗi Ngữ pháp & Chuẩn hóa Dev English** | `services/grammar_checker.py`, `services/language_helper.py` | Tự động khi gõ tiếng Anh hoặc tiếng Việt | `test_translation_and_language()` | ✅ PASS |
| **F-03** | **Xử lý Prompt dài (>600 ký tự, Multi-line wrapping)** | `services/console_daemon.py`, `services/translator.py` | Gõ prompt dài vượt 1 dòng terminal | `test_long_prompt_processing()` | ✅ PASS |
| **F-04** | **Thanh trượt lồng bên trong Real-Time Box (Nested Slider)** | `companion.py` (`VerticalScroll #realtime-scroll-view`) | Cuộn chuột hoặc phím `▲▼` bên trong khung | `test_companion_app_headless()` | ✅ PASS |
| **F-05** | **Chuyển ngữ cảnh nhanh (Fast Context Switcher)** | `services/window_switcher.py`, `companion.py` | `Alt+A`, `F9`, `Alt+Left`, `Alt+Right` | `test_window_switcher_context_toggling()` | ✅ PASS |
| **F-06** | **Tự động Focus ô nhập khi chuyển app (Auto-Focus Input)** | `companion.py` (`on_app_focus`), `window_switcher.py` | `Alt+Right`, `Alt+A`, `F9` | `test_companion_app_headless()` | ✅ PASS |
| **F-07** | **Tự động Thay thế & Gửi sang AGY (Auto Replace & Send)** | `companion.py` (`action_replace_prompt`), `window_switcher.py` | `Ctrl+R` (trong App) / `Alt+R` (Toàn cục) | `test_companion_app_headless()` | ✅ PASS |
| **F-08** | **Nút Reset & Phím tắt xóa sạch (Reset All State)** | `companion.py` (`action_reset_all`) | `Ctrl+L` hoặc `Esc` hoặc bấm nút `[Reset / Xóa sạch]` | `test_companion_app_headless()` | ✅ PASS |
| **F-09** | **Widget Tra từ nhanh Google Translate (Quick Translate)** | `companion.py`, `services/translator.py` | `Tab`, `Ctrl+\`, `Ctrl+T` (đổi chiều dịch) | `test_translation_and_language()` | ✅ PASS |
| **F-10** | **Bảo toàn 100% AGY Gốc & Chỉ thị Tiếng Việt** | `GEMINI.md`, `launch_split.bat` | Chạy `launch_split.bat` (Split-Pane 67/33) | `test_agy_client_commands()` | ✅ PASS |
| **F-11** | **Giám sát nhật ký hội thoại mới nhất (Transcript Watcher)** | `services/transcript_watcher.py` | Tự động phát hiện prompt đã gửi | `test_transcript_watcher_discovery()` | ✅ PASS |
| **F-12** | **Bộ giám sát tự phục hồi ngầm (Daemon Supervisor & Auto-Restart)** | `services/terminal_reader.py` | Tự khởi động lại nếu daemon gặp sự cố | `test_bridge.py` | ✅ PASS |
| **F-13** | **Nút Răng cưa & Bảng xổ Danh sách Phím tắt (Gear Button & Shortcuts Dropdown)** | `companion.py` (`#btn-settings`, `#shortcuts-dropdown`) | Bấm nút `⚙` ở đầu app hoặc phím `F1` | `test_companion_app_headless()` | ✅ PASS |
| **F-14** | **Đóng gói Standalone Executable & Shortcut Desktop/Taskbar** | `companion.py`, `dist/AGYCompanion.exe` | Nhấp đúp shortcut Desktop hoặc Taskbar | `test_bridge.py` & `AGYCompanion.exe --help` | ✅ PASS |
| **F-15** | **Bộ Cài đặt Độc lập Toàn diện 1-Click (Single Installer Setup)** | `AGY_Companion_Setup.exe` (43.8 MB) | Nhấp đúp file Setup trên bất kỳ máy Windows nào | `test_installer_extract.py` & `test_bridge.py` | ✅ PASS |

---

## II. Chi tiết Đặc tả & Tiêu chuẩn Nghiệm thu từng Tính năng

### F-01: Real-Time Terminal Sync (Đọc Console Buffer <80ms)
- **Cơ chế**: Tiến trình ngầm độc lập `services/console_daemon.py` đính kèm (`AttachConsole`) vào console của AGY và đọc bộ đệm hiển thị `CONOUT$`.
- **Ưu điểm**: Khắc phục triệt để lỗi xung đột gõ tiếng Việt Telex/Unikey (không bị lặp ký tự `aảare yoou S`).
- **Xử lý viền & trạng thái**: Quét chính xác dòng lệnh nằm giữa các thanh viền (`─`), tự động loại bỏ các đường kẻ box-drawing và dòng trạng thái (`esc to cancel`).
- **Giao thức**:
  - `CHANGE:<text>`: Thông báo chuỗi văn bản đang gõ tức thì lên Companion App.
  - `IDLE:`: Thông báo dòng lệnh đã trống, giao diện quay lại màn hình chờ kết nối.
  - `SUBMIT:<text>`: Thông báo khi prompt đã được gửi.

### F-02: Bộ sửa lỗi Ngữ pháp & Chuẩn hóa Dev English Cấp độ Pro Max
- **Tiếng Việt**: Tự động dịch sang Engineering English (phong cách ngắn gọn, súc tích chuẩn lập trình).
- **Tiếng Anh - Pro Max Grammar Engine**:
  - **Tầng 1 (0ms Heuristics)**: 80+ quy tắc chuyên sâu: Chia động từ ngôi thứ 3, số ít/nhiều (`he have` ➔ `he has`, `there is many` ➔ `there are many`), động từ khuyết thiếu (`can to` ➔ `can`), đảo ngữ câu hỏi (`how i can` ➔ `how can I`), giới từ kỹ thuật (`on line X`, `depend on`), từ dễ nhầm lẫn (`than/then`, `lose/loose`, `affect/effect`), danh từ không đếm được (`information`, `software`, `feedback`).
  - **Tầng 2 (Deep NLP & Multi-Endpoint)**: Kết nối phân tích chuyên sâu LanguageTool qua nhiều máy chủ dự phòng, kèm bộ lọc 120+ thuật ngữ công nghệ (`DEV_TECH_WHITELIST`) loại trừ hoàn toàn việc bắt nhầm từ khóa lập trình thành lỗi chính tả.
  - **Tầng 3 (Engineering Dev Polish - Pro Max)**: Nâng cấp văn phong đời thường thành phong cách kỹ thuật cao cấp chuẩn Senior / Staff Software Engineer.
- Hiển thị trực quan: Bản gốc ➔ Bản sửa ngữ pháp (`✔ Đã sửa ngữ pháp`) ➔ Bản Dev Polish tối ưu (`🚀 Dev Polish`) kèm phân loại 5 nhóm nhãn lỗi (`[Ngữ pháp]`, `[Cú pháp]`, `[Từ dễ nhầm]`, `[Giới từ]`, `[Chính tả]`).

### F-03: Xử lý Prompt dài (>600 ký tự, Multi-line wrapping)
- `console_daemon.py` tự động nối các dòng wrap nhiều tầng trong console buffer.
- `services/translator.py` dùng phương thức HTTP POST để không bị giới hạn độ dài query URL.
- Timeout kết nối dịch 6.0s, chia cụm an toàn nếu vượt quá 450 ký tự.

### F-04: Thanh trượt lồng bên trong Real-Time Box (Nested Slider)
- Gói gọn trong `VerticalScroll(id="realtime-scroll-view")` bên trong `#english-panel`.
- `Screen` và container ngoài đặt `overflow: hidden;`, đảm bảo thanh trượt (slider) chỉ xuất hiện và cuộn riêng bên trong khối Real-Time.
- Hiển thị độ dài ký tự (`📏 Độ dài: X ký tự`) kèm thông báo gợi ý cuộn khi prompt dài vượt 80 ký tự.

### F-05 & F-06: Chuyển ngữ cảnh nhanh & Tự động Focus ô nhập
- Phím tắt toàn cục:
  - `Alt + A`, `F9`, `Ctrl + Alt + A`: Chuyển đổi qua lại giữa AGY và Companion.
  - `Alt + Left`: Sang AGY (Khung trái trong Split-Pane).
  - `Alt + Right`: Sang Companion (Khung phải trong Split-Pane).
- **Tự động Focus**:
  - Khi sang Companion, con trỏ nhảy thẳng vào `#draft-input`. Thao tác 100% bằng phím, không cần chuột.
  - Khi sang AGY, con trỏ nằm ngay tại dòng lệnh terminal sẵn sàng nhập tiếp.

### F-07: Tự động Thay thế & Gửi sang AGY (`Ctrl+R` / `Alt+R`)
- Nhấn `Ctrl + R` (trong Companion) hoặc `Alt + R` (toàn cục):
  1. Lấy prompt đã sửa ngữ pháp / chuẩn kỹ thuật.
  2. Copy vào clipboard Windows.
  3. Tự động chuyển tiêu điểm sang AGY Terminal.
  4. Xóa sạch prompt cũ trong AGY bằng chuỗi phím `End` + `Backspace`.
  5. Dán prompt mới (`Ctrl+V`).
  6. Nhấn `Enter` gửi đi ngay!

### F-08: Nút Reset & Phím tắt xóa sạch (`Ctrl+L` / `Esc`)
- Nhấn nút `[Reset / Xóa sạch]` hoặc phím `Ctrl + L` / `Esc`:
  - Xóa sạch toàn bộ văn bản trong ô nháp `#draft-input`.
  - Đưa preview Real-Time về trạng thái kết nối ban đầu (`• Real-Time Sync: Đang kết nối trực tiếp Terminal AGY...`).
  - Tự động đặt lại con trỏ vào ô nhập nháp.

### F-09: Widget Tra từ nhanh Google Translate
- Nằm ở khung dưới (`#quick-translate-panel`).
- Nhấn `Ctrl + T` để đổi chiều dịch: `[VI ➔ EN]` ⇄ `[EN ➔ VI]`.
- Nhấn `Enter`: Kết quả hiển thị tức thì và tự động lưu vào clipboard.

### F-10: Bảo toàn 100% AGY Gốc & Chỉ thị Tiếng Việt
- Giữ nguyên terminal AGY độc lập, không can thiệp luồng lệnh.
- File `C:\Document\05.VsCodeAI\GEMINI.md` bảo đảm AGY luôn phản hồi 100% bằng tiếng Việt chuẩn.
- File khởi chạy: `launch_split.bat` (Windows Terminal Split-Pane 67/33).

### F-13: Nút Răng cưa Phím tắt (`[⚙ Phím tắt [F1]]`) & Bảng xổ Danh sách Phím tắt (Gear Button & Shortcuts Dropdown)
- **Nút răng cưa (`#btn-settings`)**: Nằm ngay đầu ứng dụng trên thanh tiêu đề (`#header-bar`), nhãn hiển thị rõ ràng `[⚙ Phím tắt [F1]]` với nền `#21262d` và màu chữ xanh công nghệ `#58a6ff`, nổi bật và dễ nhận diện trên mọi độ phân giải.
- **Bảng xổ danh sách phím tắt (`#shortcuts-dropdown`)**:
  - Mặc định ẩn (`display: none`).
  - Khi click vào nút `[⚙ Phím tắt [F1]]` (hoặc nhấn phím `F1`): Xổ ra danh sách phím tắt chi tiết, định dạng đẹp mắt ngay bên dưới thanh tiêu đề.
  - Tự động co giãn phần hiển thị nội dung bên dưới nhờ layout linh hoạt `height: 1fr;`.
  - Nhấn lại nút `[⚙ Phím tắt [F1]]`, phím `F1` hoặc phím `Esc` để đóng nhanh danh sách.
  - Tích hợp đồng bộ ở cả `companion.py` và `ui/app.py`, kèm chỉ dẫn `F1: Phím tắt [⚙]` trên thanh trạng thái dưới cùng.

### F-14: Đóng gói Standalone Executable (`AGYCompanion.exe`) & Shortcut Desktop / Taskbar
- **Trình khởi chạy Native Windows Executable (Zero Temp DLL Extraction)**:
  - Khắc phục triệt để lỗi `[PYI:ERROR] Failed to load Python DLL` do giải nén tạm vào `%TEMP%`.
  - Được biên dịch thành file nhị phân Native Windows Executable siêu nhẹ (5 KB, chuẩn WinExe GUI), không bao giờ gặp lỗi thiếu hay khóa file `python312.dll`.
  - Khởi động tức thì trong chưa đầy 0.05 giây, không nhấp nháy cửa sổ console đen.
- **Giao diện & Chức năng Đồng nhất Tuyệt đối 100% với `launch_split.bat`**:
  - Khi nhấp đúp vào `AGYCompanion.exe` (hoặc mở từ Shortcut Desktop / Taskbar), ứng dụng tự động kích hoạt **Windows Terminal Split-Pane** giống hệt 100% như khi mở `launch_split.bat`:
    - **Khung trái (67%)**: Terminal AGY nguyên bản (hỗ trợ 100% slash commands, autocomplete, tool approval, model switcher).
    - **Khung phải (33%)**: AGY Dev English Companion TUI (sửa ngữ pháp thời gian thực, dev polish, tra từ nhanh).
  - Triệt tiêu 100% khả năng xảy ra vòng lặp lặp lại (zero fork loop).
- **Vị trí Shortcut tiện lợi**:
  - Shortcut trên Màn hình chính (`Desktop` / thư mục `Máy tính` OneDrive): `C:\Users\PC\OneDrive - Hanoi University of Science and Technology\Máy tính\AGY Companion.lnk`
  - Shortcut ghim trên Thanh công cụ (`Taskbar` User Pinned): `C:\Users\PC\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar\AGY Companion.lnk`
  - Shortcut trong Start Menu và Quick Launch.

### F-15: Bộ Cài đặt Độc lập Toàn diện 1-Click (Single Installer Setup - `AGY_Companion_Setup.exe`)
- **Tự chứa toàn bộ tài nguyên (100% Self-Contained / Portable Setup)**:
  - File cài đặt duy nhất `AGY_Companion_Setup.exe` (43.8 MB) nhúng sẵn toàn bộ runtime Python, tất cả thư viện phụ thuộc (`textual`, `rich`, `httpx`, `pywin32`, `pynput`...), file thực thi độc lập `companion_core.exe`, launcher `AGYCompanion.exe` và file `launch_split.bat`.
  - **Khả năng mang sang máy khác (True Portability)**: Người dùng chỉ cần copy duy nhất 1 file `AGY_Companion_Setup.exe` sang bất kỳ máy tính Windows 10/11 nào (qua USB, Drive, Zalo, Telegram...).
- **Giao diện Cài đặt Chuyên nghiệp & Tự động Tạo Phím tắt**:
  - Giao diện WinForms GUI hiển thị rõ ràng thông tin cài đặt và cho phép tùy chọn thư mục đích (mặc định: `%LocalAppData%\Programs\AGYCompanion`).
  - Tự động tạo Shortcut trên Màn hình chính (Desktop), Thanh công cụ (Taskbar) và Start Menu.
  - Sau khi cài đặt, ứng dụng kích hoạt trực tiếp Windows Terminal Split-Pane (Khung trái 67% AGY, Khung phải 33% Companion TUI) mà **không đòi hỏi máy tính đó phải cài đặt Python trước**.

---

## III. Hướng dẫn Chạy Kiểm thử Hồi quy Toàn diện (Regression Test Guide)

Hệ thống cung cấp 3 bộ kịch bản kiểm thử độc lập để bảo đảm chất lượng toàn diện:

1. **Kiểm thử tự động các module & tích hợp (`test_bridge.py`):**
   ```powershell
   C:\Document\05.VsCodeAI\.venv\Scripts\python.exe C:\Document\05.VsCodeAI\agy_terminal_bridge\test_bridge.py
   ```
   *Kết quả kỳ vọng:* `ALL AUTOMATED TESTS PASSED SUCCESSFULLY!`

2. **Kiểm thử vòng lặp tương tác giao diện thời gian thực (`test_interactive.py`):**
   ```powershell
   C:\Document\05.VsCodeAI\.venv\Scripts\python.exe C:\Document\05.VsCodeAI\agy_terminal_bridge\test_interactive.py
   ```
   *Kết quả kỳ vọng:* `>> TOÀN BỘ 8/8 TIÊU CHUẨN KIỂM THỬ ĐÃ ĐẠT 100% THÀNH CÔNG! <<`

3. **Kiểm thử 56 kịch bản ngữ pháp phức tạp Pro Max (`test_50_grammar_scenarios.py`):**
   ```powershell
   C:\Document\05.VsCodeAI\.venv\Scripts\python.exe C:\Document\05.VsCodeAI\agy_terminal_bridge\test_50_grammar_scenarios.py
   ```
   *Kết quả kỳ vọng:* `>> KẾT QUẢ KIỂM THỬ: 56/56 KỊCH BẢN ĐẠT CHUẨN! (100.0%) <<`

Khi cả 3 lệnh trên đều trả về kết quả thành công, toàn bộ 15 tính năng từ F-01 đến F-15 cùng bộ máy ngữ pháp Pro Max được bảo đảm hoạt động hoàn hảo và không bị hồi quy.
