# 🚀 AI-app — Multi-App Repository

Repository tổng hợp các ứng dụng, công cụ và tiện ích AI được phát triển bởi [liemvu12](https://github.com/liemvu12).

---

## 📂 Danh Sách Ứng Dụng (Apps)

| Thư mục | Tên ứng dụng | Mô tả ngắn | Công nghệ |
|---|---|---|---|
| [`AGY-Companion/`](./AGY-Companion) | **AGY Companion** | Trợ lý tiếng Anh & AI tích hợp TUI đồng hành cùng Antigravity CLI | Python 3.12, Textual (TUI), Ollama AI, Grammar Engine |
| [`Shopee-Price-Checker/`](./Shopee-Price-Checker) | **Shopee Price Checker** | Tra cứu & đối soát giá sản phẩm Shopee, bóc tách biến thể, lọc shop uy tín, chống giá mồi & phát hiện rủi ro qua review | Python 3.10+, Playwright, Curl-CFFI, CLI |
| [`Ghost-Window/`](./Ghost-Window) | **Ghost Window** | Bộ công cụ duyệt web & làm việc tàng hình: Chrome Extension (Manifest V3) làm mờ/ngụy trang web + Windows Desktop App (C# Win32) làm trong suốt mọi cửa sổ | JavaScript (Manifest V3), CSS3, C# WinForms, Win32 API |

---

## 🏗️ Cấu Trúc Repository (Monorepo)

Mỗi ứng dụng trong repository này được tổ chức độc lập trong thư mục riêng:

```text
AI-app/
├── README.md                   # Mục lục và giới thiệu repository
├── .gitignore                  # Bộ lọc git chung cho toàn bộ dự án
│
├── AGY-Companion/              # [App 1] AGY Companion (TUI + Grammar + Ollama)
│   ├── README.md               # Hướng dẫn chi tiết cho AGY Companion
│   ├── companion.py            # Ứng dụng chính
│   ├── services/               # Backend services & grammar engine
│   ├── ui/                     # Giao diện TUI
│   ├── requirements.txt
│   └── run.bat
│
├── Shopee-Price-Checker/       # [App 2] Shopee Price Checker & Anti-Scam Tool
│   ├── README.md               # Hướng dẫn chi tiết cho Shopee Price Checker
│   ├── check_price.py          # CLI & controller tra cứu giá
│   ├── shopee_engine.py        # Engine Playwright & Scraper
│   ├── verifier.py             # Thuật toán so khớp biến thể & quét review
│   ├── auth.py                 # Đăng nhập QR & quản lý session
│   ├── requirements.txt
│   └── test_verifier.py
│
├── Ghost-Window/               # [App 3] Ghost Window & Ghost Mode (Stealth Suite)
│   ├── README.md               # Hướng dẫn chi tiết cho Ghost Window
│   ├── manifest.json           # Cấu hình Chrome Extension (Manifest V3)
│   ├── background/             # Service worker nền
│   ├── content/                # Scripts can thiệp DOM, hiệu ứng mờ, Panic screen
│   ├── popup/                  # Giao diện điều khiển extension
│   ├── GhostWindow.exe         # Desktop Tool native cho Windows (16KB)
│   └── TransparencyTool.cs     # Mã nguồn C# Win32 API
│
└── [App-Moi]/                  # Các ứng dụng tiếp theo sẽ được thêm vào đây
```

---

## 📌 Hướng Dẫn Chung

- Xem chi tiết hướng dẫn cài đặt và sử dụng của từng app tại file `README.md` nằm bên trong thư mục của app đó:
  - [AGY Companion Guide](./AGY-Companion/README.md)
  - [Shopee Price Checker Guide](./Shopee-Price-Checker/README.md)
  - [Ghost Window Guide](./Ghost-Window/README.md)
- Đóng góp hoặc thêm ứng dụng mới: Vui lòng tạo thư mục con mới theo cấu trúc độc lập trên.
