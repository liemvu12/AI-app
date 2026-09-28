# 🤖 AGY Companion — AI Dev English Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" />
  <img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4?logo=windows" />
  <img src="https://img.shields.io/badge/Grammar%20Engine-Pro%20Max%20ULTRA-brightgreen" />
  <img src="https://img.shields.io/badge/Rules-222%2B-orange" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

> **AGY Companion** là ứng dụng TUI (Terminal User Interface) chạy song song cùng [Antigravity (AGY) CLI](https://antigravity.dev), giúp lập trình viên viết prompt tiếng Anh chuẩn xác và chuyên nghiệp hơn trong thời gian thực.

---

## ✨ Tính Năng Nổi Bật

### 🏗️ Grammar Engine Pro Max ULTRA (222+ Rules / 3 Tầng)

| Tầng | Mô tả | Thời gian |
|---|---|---|
| **Tầng 1** | 222+ quy tắc ngữ pháp offline (Heuristic) | 0ms |
| **Tầng 2** | LanguageTool NLP Deep Analysis (multi-endpoint) | ~200ms |
| **Tầng 3** | Vocabulary Enrichment — gợi ý từ vựng Senior Engineer | 0ms |

### 📚 13 Nhóm Lỗi Được Xử Lý Hoàn Toàn Tự Động

| # | Nhóm Lỗi | Ví dụ |
|---|---|---|
| 1 | **Hòa hợp chủ - vị** | `he have` → `he has`, `there is many` → `there are many` |
| 2 | **Động từ khuyết thiếu** | `can to run` → `can run`, `does it has` → `does it have` |
| 3 | **Thì động từ (Tense)** | `I am work` → `I am working`, `we have deploy` → `we have deployed` |
| 4 | **Thể bị động & V-ing** | `data is send` → `data is sent`, `consider to use` → `consider using` |
| 5 | **Đảo ngữ câu hỏi** | `how i can` → `how can I`, `why this happen` → `why does this happen` |
| 6 | **Mệnh đề quan hệ** | `person which` → `person who`, `which it returns` → `which returns` |
| 7 | **Câu điều kiện** | `if i would know` → `if I knew`, `unless you not` → `unless you` |
| 8 | **Giới từ kỹ thuật** | `in line 45` → `on line 45`, `listen at port` → `listen on port` |
| 9 | **Từ dễ nhầm lẫn** | `faster then` → `faster than`, `site effect` → `side effect` |
| 10 | **Danh từ không đếm được** | `informations` → `information`, `feedbacks` → `feedback` |
| 11 | **Phủ định kép & viết tắt** | `dont` → `don't`, `doesnt have no` → `doesn't have any` |
| 12 | **Mạo từ kỹ thuật** | `a error` → `an error`, `an user` → `a user`, `a SQL` → `an SQL` |
| 13 | **Collocation kỹ thuật** | `do a mistake` → `make a mistake`, `do a test` → `run a test` |

---

## 📦 Cài Đặt (1-Click Setup)

### Cách 1: Dùng File Cài Đặt (Khuyến nghị)
1. Tải [`AGY_Companion_Setup.exe`](https://github.com/liemvu12/AI-app/releases/latest) từ trang Releases.
2. Double-click để cài đặt.
3. Trình cài đặt tự động tạo shortcut Desktop & Taskbar.
4. **Không cần cài Python** — runtime đã được nhúng sẵn.

### Cách 2: Chạy từ Source
```powershell
git clone https://github.com/liemvu12/AI-app.git
cd AI-app
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
agy_terminal_bridge\launch_split.bat
```

---

## 🖥️ Giao Diện

Khi khởi động, ứng dụng mở **Windows Terminal Split-Pane** (2 ngăn):

```
┌────────────────────────────┬──────────────────────────┐
│  AGY Terminal (67%)        │  Companion TUI (33%)     │
│  ──────────────────────    │  ┌──────────────────────┐│
│  $ agy                     │  │ 📝 Nguyên văn        ││
│  > how i can fix this      │  │ how i can fix this   ││
│                            │  ├──────────────────────┤│
│                            │  │ ✔ Đã sửa ngữ pháp   ││
│                            │  │ How can I fix this   ││
│                            │  ├──────────────────────┤│
│                            │  │ 🚀 Dev Polish        ││
│                            │  │ How can I diagnose.. ││
│                            │  └──────────────────────┘│
└────────────────────────────┴──────────────────────────┘
```

---

## ⌨️ Phím Tắt

| Phím | Chức năng |
|---|---|
| `Ctrl+R` | Thay thế & gửi prompt đã sửa vào AGY Terminal |
| `Alt+R` | Thay thế & gửi (toàn cục, ngay cả khi đang ở AGY) |
| `Alt+A` / `F9` | Chuyển đổi qua lại giữa AGY và Companion |
| `Alt+Left` | Chuyển sang AGY Terminal |
| `Alt+Right` | Chuyển sang Companion TUI |
| `Ctrl+T` | Đổi chiều dịch (VI→EN / EN→VI) |
| `Ctrl+L` / `Esc` | Reset sạch toàn bộ |
| `F1` | Hiện/ẩn bảng phím tắt |

---

## 🏗️ Kiến Trúc Hệ Thống

```
agy_terminal_bridge/
├── companion.py              # TUI App chính (Textual framework)
├── launch_split.bat          # Launcher Windows Terminal Split-Pane
├── services/
│   ├── grammar_checker.py    # 🔥 Pro Max ULTRA Grammar Engine (222+ rules)
│   ├── language_helper.py    # Xử lý ngôn ngữ & Dev Polish
│   ├── translator.py         # Dịch VI↔EN (MyMemory API)
│   ├── console_daemon.py     # Đọc console buffer real-time <80ms
│   ├── terminal_reader.py    # Terminal sync daemon
│   ├── transcript_watcher.py # Theo dõi hội thoại AGY
│   └── window_switcher.py    # Chuyển đổi ngữ cảnh cửa sổ
├── dist/
│   └── companion_core/       # PyInstaller --onedir build
│       ├── companion_core.exe
│       └── _internal/        # Python 3.12 embedded runtime
└── AGYCompanion.exe          # C# WinForms launcher (6KB)
```

---

## 🧪 Kiểm Thử

```powershell
# Chạy bộ kiểm thử toàn diện 55 kịch bản ngữ pháp
python agy_terminal_bridge/test_50_grammar_scenarios.py

# Kiểm thử hồi quy đầy đủ (15 tính năng)
python agy_terminal_bridge/test_bridge.py
```

**Kết quả hiện tại**: ✅ 73/73 kịch bản đạt chuẩn (100%)

---

## 📋 Yêu Cầu Hệ Thống

| Yêu cầu | Chi tiết |
|---|---|
| OS | Windows 10/11 (x64) |
| Terminal | Windows Terminal (wt.exe) |
| AGY | Antigravity CLI (`agy` command) |
| Python | Không cần (đã nhúng trong Setup.exe) |
| RAM | ~150 MB khi chạy |

---

## 📄 License

MIT License — © 2026 liemvu12

---

<p align="center">Made with ❤️ for Vietnamese developers who want to write better English prompts.</p>
