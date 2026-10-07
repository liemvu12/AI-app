# 👻 Ghost Window & Ghost Mode — Stealth Web Browsing & Desktop Transparency Suite

<p align="center">
  <img src="https://img.shields.io/badge/Chrome%20Extension-Manifest%20V3-4285F4?logo=googlechrome" />
  <img src="https://img.shields.io/badge/Desktop%20App-C%23%20%7C%20WinForms-512BD4?logo=csharp" />
  <img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4?logo=windows" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

> **Ghost Window** là bộ giải pháp toàn diện giúp duyệt web và làm việc riêng tư tối đa trong môi trường mở (văn phòng, lớp học, quán café). Bộ công cụ bao gồm **Chrome Extension Manifest V3** (làm mờ và ngụy trang nội dung tab web) và **Ứng dụng Desktop Windows native** (làm trong suốt mọi cửa sổ ứng dụng trên hệ điều hành qua Win32 API).

---

## 🌟 2 Thành Phần Trong Bộ Công Cụ

Bộ công cụ được cấu thành từ 2 giải pháp kết hợp ăn ý với nhau:

```text
Ghost-Window/
├── 🧩 1. Chrome Extension (Manifest V3)  -> Làm tàng hình, mờ nhòe & ngụy trang trang web trực tiếp
└── 🖥️ 2. GhostWindow Desktop App (C#)    -> Làm trong suốt bất kỳ cửa sổ Windows nào qua Win32 API
```

---

## 🧩 1. Tiện Ích Mở Rộng: Ghost Mode (Chrome Extension)

Extension chạy trực tiếp trên các trình duyệt Chromium (Chrome, Edge, Brave, Cốc Cốc,...) với các tính năng ngụy trang chuyên sâu:

### ✨ Tính Năng Nổi Bật

1. **Độ trong suốt siêu cấp (Opacity Slider: 1% – 100%)**:
   - Tinh chỉnh độ mờ linh hoạt xuống tới tận 1%.
   - Các mức preset nhanh: **🫥 5% (Cực mờ)**, **👻 15% (Siêu mờ)**, **💼 35% (Văn phòng lý tưởng)**, **🕶️ 60%**, **💡 100%**.
2. **Làm mờ nét & sương mù (Heavy Blur: 0px – 30px)**:
   - Làm nhòe toàn bộ chữ, bố cục và hình ảnh từ nhẹ (`4px`) đến mờ mịt (`18px – 30px`), người đứng cạnh cũng không thể đọc được nội dung.
3. **Làm mờ Media & Hover-to-Reveal**:
   - Tự động làm mờ sâu toàn bộ hình ảnh, video, banner và meme.
   - Chỉ khi bạn rê chuột (hover) vào hình ảnh/video thì nội dung đó mới hiện rõ tạm thời.
4. **Chế độ đơn sắc (Grayscale & Low Contrast)**:
   - Chuyển toàn bộ màu sắc rực rỡ thành tông xám đen trắng nhạt, nhìn từ xa trông giống hệt một trang văn bản tài liệu Word/PDF thông thường.
5. **Vùng sáng theo con trỏ chuột (Spotlight Mode)**:
   - Toàn trang web mờ tịt, chỉ duy nhất một vùng tròn xung quanh con trỏ chuột là sáng và rõ nét.
6. **Tự mờ khi rời tay (Idle Fade)**:
   - Tự động mờ tối đa nếu không di chuột hoặc gõ phím sau 5 giây. Chạm chuột lại sẽ lập tức phục hồi độ sáng.
7. **Chữ siêu mỏng (Stealth Font)**:
   - Tinh chỉnh font chữ mỏng và giảm tương phản nhằm hạn chế tối đa góc nhìn lén từ hai bên.
8. **Phím tắt khẩn cấp (Boss Key / Panic Screen — `Alt + Z`)**:
   - Lập tức phủ toàn màn hình bằng tài liệu ngụy trang:
     - 📝 **Tài liệu Word**: Báo cáo tổng kết vận hành nội bộ công ty.
     - 📊 **Bảng tính Excel**: Quản lý tiến độ dự án Cloud & IT.
     - 💻 **Code IDE**: Giao diện lập trình VS Code.
     - ⚪ **Blank Screen**: Màn hình trắng sạch.
   - Bấm lại `Alt + Z` hoặc **nhấp đúp chuột** vào màn hình để quay lại trang web.

### ⌨️ Phím Tắt Tiện Ích Trong Trình Duyệt

| Phím tắt | Chức năng |
| :--- | :--- |
| **`Alt + X`** | Bật / Tắt nhanh chế độ Tàng hình |
| **`Alt + Z`** | **Boss Key khẩn cấp** (Phủ màn hình ngụy trang ngay lập tức) |
| **`Alt + ↑`** | Tăng độ rõ nét (+5% Opacity) |
| **`Alt + ↓`** | Tăng độ trong suốt (-5% Opacity, xuống tới 1%) |
| **`Alt + B`** | Bật / Tắt làm mờ nhòe sương mù (Heavy Blur) |
| **`Alt + M`** | Bật / Tắt làm mờ Hình ảnh & Video |

---

## 🖥️ 2. Ứng Dụng Desktop: Ghost Window (`GhostWindow.exe`)

Ứng dụng Windows nhỏ gọn (16KB) được viết bằng C# WinForms, tương tác trực tiếp với **Windows User32 API** (`SetWindowLong`, `SetLayeredWindowAttributes`, `RegisterHotKey`):

### ✨ Tính Năng Nổi Bật

1. **Làm trong suốt cửa sổ bất kỳ**: Áp dụng được cho Google Chrome, Microsoft Edge, VS Code, Notepad, Discord, hoặc bất kỳ phần mềm nào đang mở.
2. **Chọn cửa sổ trực quan**: Dropdown tự động liệt kê toàn bộ các cửa sổ ứng dụng đang chạy.
3. **Thanh trượt Opacity & Preset 1-Click**: Điều chỉnh từ 5% đến 100% cực kỳ mượt mà.
4. **Phím tắt toàn cục (Global Hotkeys)**: Hoạt động ngay cả khi bạn đang thao tác ở cửa sổ khác:
   - `Ctrl + Alt + 1` → Trong suốt 10% (Siêu tàng hình)
   - `Ctrl + Alt + 2` → Trong suốt 20%
   - `Ctrl + Alt + 3` → Trong suốt 30% (Khuyên dùng khi có người qua lại)
   - `Ctrl + Alt + 4..9` → Trong suốt 40% – 90%
   - `Ctrl + Alt + 0` → Khôi phục 100% (Bình thường)
   - `Ctrl + Alt + Z` → **Boss Key** (Thu nhỏ cửa sổ ngay lập tức)
5. **Chạy ngầm ở System Tray**: Thu nhỏ gọn gàng xuống khay hệ thống cạnh đồng hồ Windows.

---

## 🏗️ Cấu Trúc Mã Nguồn

```text
Ghost-Window/
├── manifest.json              # Khai báo cấu hình Chrome Extension (Manifest V3)
├── background/
│   └── background.js          # Service worker xử lý phím tắt & trạng thái
├── content/
│   ├── content.js             # Logic can thiệp DOM, hiệu ứng mờ, Panic screen
│   └── content.css            # Stylesheets cho overlay ngụy trang & HUD
├── popup/
│   ├── popup.html             # Giao diện cài đặt popup của Extension
│   ├── popup.js               # Điều khiển slider, toggles, lưu chrome.storage
│   └── popup.css              # Giao diện Dark Mode hiện đại
├── icons/                     # Bộ biểu tượng extension (16, 32, 48, 128px)
├── generate_icons.ps1         # Script PowerShell tự động sinh bộ icon
│
├── GhostWindow.exe            # Ứng dụng Desktop Windows native (16KB)
├── TransparencyTool.cs        # Mã nguồn C# Win32 API của Desktop Tool
└── README.md                  # Hướng dẫn chi tiết dự án
```

---

## 📦 Hướng Dẫn Cài Đặt & Sử Dụng

### 1. Cài đặt Chrome Extension
1. Mở trình duyệt Chrome / Edge và truy cập `chrome://extensions/`.
2. Bật công tắc **Developer mode** (Chế độ dành cho nhà phát triển) ở góc trên bên phải.
3. Nhấn nút **Load unpacked** (Tải tiện ích đã giải nén).
4. Chọn thư mục `Ghost-Window/`.
5. Ghim 📌 biểu tượng Ghost Mode lên thanh công cụ trình duyệt để tiện sử dụng.

### 2. Sử dụng Desktop Tool (`GhostWindow.exe`)
- Chạy trực tiếp file `GhostWindow.exe`. Ứng dụng không cần cài đặt.
- Chọn cửa sổ cần làm mờ từ danh sách, sau đó dùng các nút preset hoặc phím tắt toàn cục `Ctrl + Alt + 1..0`.

### 3. Biên dịch lại Desktop Tool từ Source (Tùy chọn)
Nếu bạn muốn chỉnh sửa mã nguồn `TransparencyTool.cs`, bạn có thể tự biên dịch lại bằng trình biên dịch .NET mặc định của Windows mà **không cần cài Visual Studio**:

```powershell
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /target:winexe /out:GhostWindow.exe TransparencyTool.cs
```

---

## 💡 Mẹo Sử Dụng Thực Tế

- **Chế độ Ninja Văn Phòng**: Bật Chrome Extension ở mức `Opacity 35%` + `Grayscale (Đơn sắc)` + `Media Blur`. Từ khoảng cách 2 mét, màn hình của bạn sẽ trông hệt như một tài liệu báo cáo kỹ thuật đen trắng.
- **Duyệt Toàn Màn Hình**: Nhấn `F11` trên Chrome để ẩn toàn bộ thanh địa chỉ và tab, kết hợp với Ghost Mode để có trải nghiệm tàng hình hoàn hảo.
- **Phòng Bị Khẩn Cấp**: Luôn sẵn sàng ngón tay với phím `Alt + Z` (trên trình duyệt) hoặc `Ctrl + Alt + Z` (trên Windows) để lập tức che giấu nội dung khi có người bất ngờ đến gần.

---

## 📄 License

Dự án phát hành dưới giấy phép [MIT License](https://opensource.org/licenses/MIT).
