# 🚀 AI-app — Multi-App Repository

Repository tổng hợp các ứng dụng, công cụ và tiện ích AI được phát triển bởi [liemvu12](https://github.com/liemvu12).

---

## 📂 Danh Sách Ứng Dụng (Apps)

| Thư mục | Tên ứng dụng | Mô tả ngắn | Công nghệ |
|---|---|---|---|
| [`AGY-Companion/`](./AGY-Companion) | **AGY Companion** | Trợ lý tiếng Anh & AI tích hợp TUI đồng hành cùng Antigravity CLI | Python 3.12, Textual (TUI), Ollama AI, Grammar Engine |

---

## 🏗️ Cấu Trúc Repository (Monorepo)

Mỗi ứng dụng trong repository này được tổ chức độc lập trong thư mục riêng:

```text
AI-app/
├── README.md               # Mục lục và giới thiệu repository
├── .gitignore              # Bộ lọc git chung cho toàn bộ dự án
│
├── AGY-Companion/          # App 1: AGY Companion (TUI + Grammar + Ollama)
│   ├── README.md           # Hướng dẫn chi tiết cho AGY Companion
│   ├── companion.py        # Ứng dụng chính
│   ├── services/           # Backend services & grammar engine
│   ├── ui/                 # Giao diện TUI
│   ├── requirements.txt
│   └── run.bat
│
└── [App-Moi]/              # Các ứng dụng tiếp theo sẽ được thêm vào đây
```

---

## 📌 Hướng Dẫn Chung

- Xem chi tiết hướng dẫn cài đặt và sử dụng của từng app tại file `README.md` nằm bên trong thư mục của app đó (ví dụ: [AGY-Companion/README.md](./AGY-Companion/README.md)).
- Đóng góp hoặc thêm ứng dụng mới: Vui lòng tạo thư mục con mới theo cấu trúc độc lập trên.
