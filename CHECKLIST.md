# CHECKLIST DỰ ÁN: AGY TERMINAL BRIDGE (TUI)
*Giao diện Terminal trung gian cho Antigravity CLI kết hợp hỗ trợ tiếng Anh cho lập trình viên.*

---

## Danh sách tính năng triển khai

### Phase 1: Khởi tạo Kiến trúc & Giao diện TUI Cốt lõi
- [x] **1.1 Cấu trúc dự án và môi trường**
  - Thư mục làm việc: `C:\Document\05.VsCodeAI\agy_terminal_bridge`
  - Thiết lập virtualenv và các dependencies (`textual`, `rich`, `httpx`,...).
- [x] **1.2 Luồng Terminal Đồng Nhất (Inline Terminal Stream) & 2 Cửa Sổ Tối Giản**
  - Khung trái (Terminal Đồng Nhất): Trải nghiệm như terminal/powershell/bash thật, **KHÔNG chia tách ô nhập prompt và ô phản hồi**. Dòng nhập lệnh `agy> ` nằm tiếp nối ngay sau câu trả lời trước đó và tự động trượt xuống cùng luồng dữ liệu.
  - Hỗ trợ đầy đủ Slash Commands (`/model`, `/skills`, `/agents`, `/effort`, `/new`, `/clear`, `/help`).
  - Khung phải trên (English Learning Panel): Phản hồi thời gian thực 0ms khi gõ prompt, tự động dịch kỹ thuật hoặc sửa ngữ pháp.
  - Khung phải dưới (Quick Translate Widget): Tra cứu nhanh từ/câu với Google Translate tốc độ cao (<300ms).
  - Phong cách tối giản: Chỉ phân cách bằng các đường viền mảnh đơn sắc (`#262936`), không màu mè phức tạp.
- [x] **1.3 Hệ thống phím tắt (Keyboard First Navigation)**
  - `Tab` / `Shift+Tab`: Chuyển đổi focus mượt mà giữa Terminal Input, Quick Translate, và Terminal Log.
  - `Ctrl+T`: Đổi chiều dịch tức thì trong Quick Translate (VI -> EN và EN -> VI).
  - `Ctrl+E`: Gửi phiên bản tiếng Anh đã dịch/sửa lỗi cho AI thay vì câu gốc tiếng Việt.
  - `Esc`: Trở về nhanh dòng lệnh Terminal `agy>`.

---

### Phase 2: Module Dịch thuật & Bộ Sửa Ngữ Pháp Tiếng Anh (Language & Grammar Engine)
- [x] **2.1 Bộ Sửa Ngữ Pháp & Cú Pháp Tiếng Anh Cấp Độ Pro Max (Pro Max English Grammar & Dev Syntax Engine)**
  - Tự động nhận diện ngôn ngữ của prompt (Việt hay Anh).
  - Nếu là tiếng Việt: Dịch sang tiếng Anh phong cách kỹ thuật (Dev-oriented / Engineering English).
  - Nếu là tiếng Anh: Kích hoạt hệ thống **Pro Max Grammar Engine** với 3 tầng phân tích chuyên sâu:
    - **Tầng 1 (Tức thì 0ms - Offline First)**: Hơn 80+ quy tắc ngữ pháp chuyên sâu cho lập trình viên (Hòa hợp chủ vị, trật tự từ trong câu hỏi, trợ động từ, động từ khuyết thiếu bare infinitive, thể bị động, giới từ kỹ thuật, danh từ không đếm được).
    - **Tầng 2 (Deep NLP Multi-Endpoint)**: Kết nối phân tích chuyên sâu LanguageTool đa máy chủ dự phòng, kèm bộ lọc **120+ thuật ngữ công nghệ (DEV_TECH_WHITELIST)** loại trừ 100% việc bắt nhầm từ khóa lập trình thành lỗi chính tả.
    - **Tầng 3 (Engineering Dev Polish - Pro Max)**: Tự động nâng cấp prompt từ văn phong sơ sài sang phong cách kỹ thuật cao cấp chuẩn Senior / Staff Software Engineer (ví dụ: `fix this bug` ➔ `debug and resolve this issue`, `write a code for login` ➔ `implement a clean, production-grade routine for login`).
  - Phân loại trực quan 5 nhóm lỗi trên UI: `[Ngữ pháp]`, `[Cú pháp]`, `[Từ dễ nhầm]`, `[Giới từ]`, `[Chính tả]`.
- [x] **2.2 Quick Google Translate Widget**
  - Tra từ/cụm từ nhanh không cần rời khỏi terminal.
  - Tích hợp phím tắt `Ctrl+T` đổi chiều `[VI -> EN]` ⇄ `[EN -> VI]`.
  - Hiển thị kết quả rõ ràng, nhanh chóng với cơ chế cache/async không làm đơ UI.

---

### Phase 3: Chế độ Companion Độc Lập & Giữ Nguyên 100% AGY Gốc (Native AGY Preservation)
- [x] **3.1 AGY Native Runner (Không can thiệp luồng lệnh)**
  - Chạy trực tiếp `agy` nguyên bản trong terminal gốc, không cần pipe/chuyển tiếp lệnh.
  - Bảo toàn 100% tính năng AGY: Slash commands tương tác, autocomplete, menu chọn model, duyệt quyền thực thi tool `[y/N]`, subagents, spinner thời gian thực.
- [x] **3.2 Chỉ thị tiếng Việt cấp Workspace qua `GEMINI.md`**
  - Tạo file `C:\Document\05.VsCodeAI\GEMINI.md` quy định AGY luôn trả lời bằng Tiếng Việt 100% cho mọi câu hỏi.
- [x] **3.3 AGY English Companion (`companion.py`)**
  - Cửa sổ đồng hành độc lập bên ngoài: Tối ưu hóa tiếng Anh kỹ thuật theo thời gian thực + Tra từ Google Translate siêu tốc.
  - **Đọc trực tiếp Console Screen Buffer qua Daemon độc lập (`services/console_daemon.py` & `services/terminal_reader.py`):**
    - Chạy tiến trình ngầm độc lập đính kèm vào console của AGY và đọc bộ đệm hiển thị `CONOUT$`.
    - Không làm ảnh hưởng hay phá vỡ Console Handle của giao diện Textual UI.
    - Nhận diện 100% văn bản thuần Unicode chuẩn (không bị lỗi lặp chữ `aảare yoou S` do bộ gõ Unikey / Telex / EVKey).
    - Cập nhật thời gian thực Real-Time mượt mà (độ trễ <80ms) ngay khi bạn gõ từng ký tự trong Terminal AGY.
  - **Bộ kiểm tra & sửa lỗi ngữ pháp tiếng Anh chuyên sâu (`services/grammar_checker.py`):** Tự động phát hiện lỗi chia động từ, trật tự từ, giới từ, mạo từ và gợi ý sửa trực quan.
  - Phím tắt `Enter`: Tự động sao chép câu tiếng Anh đã chuẩn hóa vào Clipboard (tốc độ <1ms) để dán `Ctrl+V` sang AGY.
  - Phím tắt `Ctrl+T`: Đổi chiều dịch tức thì trong widget Quick Translate.
- [x] **3.4 Script khởi chạy tích hợp Windows Terminal Split-Pane (`launch_split.bat`)**
  - 1-Click mở Windows Terminal chia đôi màn hình: Trái là AGY gốc (67%), Phải là Companion (33%).
- [x] **3.5 Nút thay thế prompt đã sửa [Ctrl+R] & Thanh trượt (Slider) kiểm tra prompt dài**
  - **Nút Thay thế Prompt (`#btn-replace-prompt`):** Nằm ngay dưới khung `[🔴 REAL-TIME TỪ TERMINAL AGY]`, cho phép thay thế prompt bị sai cú pháp/ngữ pháp bằng bản chuẩn kỹ thuật (phím tắt `Ctrl+R`), tự động sao chép vào clipboard hệ thống để paste ngay sang AGY.
  - **Thanh trượt dọc nổi bật (Slider / Scrollbar):** Thiết lập thanh cuộn cố định bên cạnh cửa sổ (`overflow-y: scroll`, `scrollbar-size-vertical: 2`, `scrollbar-color: #388bfd #161b22`), kèm thông báo độ dài ký tự giúp kiểm tra toàn diện khi prompt dài vượt khung.
  - **Khắc phục lỗi treo/không hoàn tất khi xử lý prompt dài:**
    - Cải tiến `console_daemon.py` thu thập trọn vẹn văn bản wrap qua nhiều dòng console (`read_console_prompt`).
    - Chuyển `_google_translate_fast` sang phương thức HTTP POST tránh giới hạn độ dài URL.
    - Tăng timeout dịch lên 6.0s và LanguageTool lên 5.0s, bổ sung chia cụm an toàn (`_translate_with_mymemory`) khi prompt vượt 450 ký tự.
- [x] **3.6 Phím tắt chuyển đổi ngữ cảnh nhanh giữa các ứng dụng & Thanh trượt lồng trong app**
  - **Hệ thống phím tắt chuyển đổi nhanh (Fast Context Switcher):**
    - Phím tắt toàn cục (Global Hotkeys): `Alt + A`, `F9`, `Ctrl + Alt + A` hoạt động từ bất kỳ đâu (kể cả khi đang gõ phím trong AGY terminal) để chuyển đổi qua lại tức thì giữa AGY và Companion.
    - Windows Terminal Split-Pane: Hỗ trợ `Alt + Left` (sang AGY pane bên trái) và `Alt + Right` (sang Companion pane bên phải).
  - **Thanh trượt lồng trực tiếp bên trong `[🔴 REAL-TIME TỪ TERMINAL AGY]`:**
    - Đóng gói trong container `VerticalScroll(id="realtime-scroll-view")` lồng trực tiếp bên trong khung viền nội dung.
    - `Screen` và `#english-panel` được cấu hình `overflow: hidden;` loại bỏ hoàn toàn thanh cuộn ngoài màn hình, đảm bảo thanh trượt (slider) chỉ xuất hiện và cuộn riêng bên trong khối Real-Time.
- [x] **3.7 Tự động Focus ô nhập, Tự động Thay thế & Gửi [Ctrl+R], và Nút Reset [Ctrl+L]**
  - **Tự động nhảy con trỏ thẳng vào thanh nhập dữ liệu:**
    - Khi chuyển sang Companion (`Alt + Right`, `Alt + A`, `F9`), con trỏ tự động nhảy thẳng vào `#draft-input` qua sự kiện `on_app_focus`, thao tác 100% bằng bàn phím mà không cần chạm chuột.
    - Khi chuyển sang AGY (`Alt + Left`, `Alt + A`, `F9`), con trỏ lập tức nằm tại dòng lệnh terminal sẵn sàng gõ tiếp.
  - **Tự động Thay thế, Xóa prompt cũ và Gửi [Ctrl+R] (hoặc Alt+R toàn cục):**
    - Nhấn `Ctrl + R` (trong Companion) hoặc `Alt + R` (từ bất kỳ đâu): Tự động sao chép prompt mới, chuyển sang AGY Terminal, xóa sạch toàn bộ ký tự prompt cũ bằng chuỗi Backspace chuẩn, dán prompt mới (`Ctrl+V`), và nhấn `Enter` gửi đi ngay!
  - **Nút Reset / Xóa sạch (`#btn-reset`):**
    - Thay thế nút "Sang AGY" thành nút `[Reset / Xóa sạch [Ctrl+L]]`.
    - Phím tắt `Ctrl + L` hoặc `Esc`: Xóa sạch nội dung nháp, reset màn hình preview về trạng thái ban đầu, và đặt ngay con trỏ vào ô nhập tài liệu.
- [x] **3.8 Nút Răng cưa Phím tắt (`[⚙ Phím tắt [F1]]`) & Bảng xổ Danh sách Phím tắt (Shortcuts Dropdown)**
  - Nút `[⚙ Phím tắt [F1]]` được thiết kế nổi bật, rõ ràng ngay góc trên bên phải thanh tiêu đề đầu app (`#header-bar`) với nền `#21262d` và chữ xanh công nghệ `#58a6ff`.
  - Tích hợp đồng bộ ở cả `companion.py` và `ui/app.py`.
  - Bấm vào nút `[⚙ Phím tắt [F1]]` hoặc nhấn phím `F1`: Xổ xuống bảng tra cứu phím tắt chi tiết (`#shortcuts-dropdown`).
  - Đóng bảng nhanh chóng bằng cách bấm lại nút, phím `F1` hoặc `Esc`.
  - Bổ sung hiển thị chỉ dẫn `F1: Phím tắt [⚙]` trên thanh trạng thái dưới cùng (`#status-bar`).
- [x] **3.9 Tinh chỉnh UI 2 Button tối giản đơn sắc, thu nhỏ, loại bỏ icon và căn giữa chữ**
  - Loại bỏ hoàn toàn màu xanh lá / vàng đất sặc sỡ, chuyển sang phong cách tối giản đơn sắc (`#1a1e29` / `#262c3a`).
  - Thu nhỏ kích thước tối đa (`height: 1; min-height: 1; padding: 0`).
  - Gỡ bỏ hoàn toàn icon / emoji (`Thay thế & Gửi [Ctrl+R]`, `Reset / Xóa sạch [Ctrl+L]`).
  - Căn giữa chữ cân đối tuyệt đối (`text-align: center; content-align: center middle`).
- [x] **3.10 Khóa kết nối Bền vững (Connection Locking) cho Real-Time Console Sync**
  - Cơ chế Connection Locking: Giữ chặt kết nối với `agy.exe` khi đang hoạt động, tuyệt đối không ngắt kết nối khi có tiến trình phụ hay lệnh terminal nền chạy.
  - Loại trừ 100% các tiến trình PowerShell tạm thời (`-Command`).
  - Quét vùng prompt chính xác xung quanh tọa độ con trỏ `cursor_y` và hỗ trợ prompt dài nhiều tầng.

---

### Phase 4: Tinh chỉnh, Kiểm thử & Đóng gói (Testing & Polish)
- [x] **4.1 Kiểm tra tương tác và luồng chạy thực tế**
  - Test tương tác nhập tiếng Việt -> Kiểm tra ô dịch EN -> Nhận kết quả AI tiếng Việt.
  - Test tương tác nhập tiếng Anh -> Kiểm tra ô sửa ngữ pháp -> Nhận kết quả AI tiếng Việt.
  - Test widget Quick Translate và chuyển đổi phím tắt `Ctrl+T`.
- [x] **4.2 Script khởi chạy tiện lợi (Launcher)**
  - File `run.bat` hoặc script khởi chạy 1-click cho người dùng (`launch_split.bat`).
- [x] **4.3 Kiểm duyệt lại toàn bộ theo Checklist**
  - Xác nhận mọi tính năng đã hoàn thiện đúng yêu cầu.
- [x] **4.4 Quy trình Kiểm thử Hồi quy & Bảng Tính năng Hiện có (`EXISTING_FEATURES.md`)**
  - Đã lập file [EXISTING_FEATURES.md](file:///C:/Document/05.VsCodeAI/agy_terminal_bridge/EXISTING_FEATURES.md) liệt kê chi tiết 14 tính năng cốt lõi (F-01 đến F-14).
  - Tích hợp toàn diện vào `test_bridge.py` để tự động kiểm thử hồi quy 100% các tính năng cũ mỗi khi thêm tính năng mới.
- [x] **4.5 Đóng gói Standalone Executable (.exe) & Shortcut Màn hình chính + Thanh công cụ (Taskbar)**
  - Đóng gói toàn bộ ứng dụng thành file thực thi hoàn chỉnh `AGYCompanion.exe`.
  - **Khắc phục triệt để lỗi `[PYI:ERROR] Failed to load Python DLL`**:
    - Thay thế cơ chế giải nén tạm vào `%TEMP%` bằng trình khởi chạy Native Windows Executable siêu nhẹ (5 KB, chuẩn WinExe, không nháy màn hình console đen).
    - Loại bỏ 100% tình trạng xung đột giải nén file DLL tạm thời (`python312.dll`) và loại trừ sự can thiệp khóa file của Windows Defender.
  - **Giao diện đồng nhất 100% với `launch_split.bat`**:
    - Khi khởi chạy `AGYCompanion.exe` (hoặc nhấp đúp từ Shortcut Desktop / Taskbar), ứng dụng tự động kích hoạt **Windows Terminal Split-Pane** (<0.05s) giống hệt 100% như khi mở `launch_split.bat`:
      - **Khung trái (67%)**: Terminal AGY nguyên bản (hỗ trợ 100% slash commands, autocomplete, tool approval, model switcher).
      - **Khung phải (33%)**: AGY Dev English Companion TUI (sửa ngữ pháp thời gian thực, dev polish, tra từ nhanh).
  - Bộ kiểm thử 56 kịch bản ngữ pháp phức tạp (`test_50_grammar_scenarios.py`) đạt 100% (56/56 PASS).
- [x] **4.6 Bộ Cài đặt Độc lập Toàn diện 1-Click (Single Installer .exe - `AGY_Companion_Setup.exe`)**
  - Đóng gói toàn bộ ứng dụng thành 1 file cài đặt duy nhất `AGY_Companion_Setup.exe` (43.8 MB) chuẩn WinForms GUI.
  - Tích hợp trọn gói: Python embedded runtime, toàn bộ thư viện phụ thuộc (`textual`, `rich`, `httpx`, `pywin32`,...), file thực thi độc lập `companion_core.exe` và Native Split-Pane Launcher `AGYCompanion.exe`.
  - Khả năng di động 100% (True Portability): Chỉ cần copy 1 file `AGY_Companion_Setup.exe` sang bất kỳ máy tính Windows nào, nhấp đúp để tự động cài đặt và tự tạo shortcut trên Desktop, Taskbar, Start Menu mà không cần cài đặt Python.
