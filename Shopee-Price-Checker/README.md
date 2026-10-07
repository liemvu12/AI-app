# 🛒 Shopee Price Checker — E-Commerce Price Verification & Anti-Scam Tool

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-0078D4" />
  <img src="https://img.shields.io/badge/Engine-Playwright%20%2B%20Curl--CFFI-orange" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

> **Shopee Price Checker** là công cụ CLI & Automation thông minh giúp tra cứu, đối soát giá thực tế của sản phẩm trên sàn thương mại điện tử **Shopee Việt Nam**. Công cụ tự động bóc tách biến thể, phát hiện & loại bỏ "giá mồi" (phụ kiện giá rẻ), quét review 1-2 sao để cảnh báo hàng giả/hàng lỗi/trâu cày, và tính giá trung vị thị trường chuẩn xác.

---

## ✨ Tính Năng Nổi Bật

### 1. 🎯 Bóc Tách Biến Thể & Kiểm Tra Tồn Kho Thật (Variant Matching & Stock Check)
- Tự động phân tích cây phân loại (models/tiers): bản Tray/Box, dung lượng 128GB/256GB, màu sắc, tùy chọn combo.
- **Loại bỏ giá mồi**: Tránh bẫy người bán treo giá phụ kiện rẻ tiền (ví dụ: bán CPU 2 triệu nhưng treo keo tản nhiệt 20k làm giá hiển thị).
- Kiểm tra số lượng tồn kho thực tế (`stock > 0`) trước khi báo giá.

### 2. 🛡️ Lọc Shop Uy Tín (Fast & Trusted Filter)
- **Tiêu chuẩn lượt bán**: Bắt buộc số lượng bán ra phải trên 100 (`sold > 100`).
- Ưu tiên **Shopee Mall** và **Shop Yêu Thích**.
- Đánh giá trung bình đạt chuẩn (`rating >= 4.6`).

### 3. 🔍 Quét Đánh Giá Chống Lừa Đảo (Anti-Scam Review Scanner)
- Tự động đào sâu và phân tích đánh giá tiêu cực (1 - 2 sao).
- Nhận diện các từ khóa nguy cơ cao: `"lừa đảo"`, `"hàng giả"`, `"fake"`, `"trâu cày"`, `"rỉ sét"`, `"cháy"`, `"không lên"`, `"chối bỏ"`.
- Đánh dấu cờ cảnh báo `HIGH_RISK` nếu phát hiện shop có dấu hiệu bất thường.

### 4. 📊 Đối Soát Giá Thị Trường (Median Price Benchmark)
- Thống kê phân vị giá trên toàn bộ các shop uy tín.
- Loại bỏ giá ảo (quá thấp hoặc quá cao so với giá trung vị thị trường).

### 5. 🔐 Xác Thực Phiên Đăng Nhập An Toàn (QR Code Auth)
- Hỗ trợ đăng nhập qua mã QR quét trực tiếp bằng App Shopee (`auth.py`).
- Lưu phiên làm việc an toàn tại `session_state.json` (được bảo vệ bởi `.gitignore`).

---

## 🏗️ Cấu Trúc Mã Nguồn

```text
Shopee-Price-Checker/
├── auth.py                  # Xác thực tài khoản Shopee bằng mã QR & quản lý session
├── check_price.py           # CLI Tool & Controller điều phối toàn bộ quy trình
├── shopee_engine.py         # Engine tìm kiếm & lấy dữ liệu qua Playwright / Curl-CFFI
├── verifier.py              # Logic so khớp phân loại, quét review tiêu cực, tính benchmark giá
├── test_verifier.py         # Bộ kiểm thử logic tự động (Unit Tests)
├── session_state.example.json # File mẫu cấu hình session
├── requirements.txt         # Danh sách thư viện phụ thuộc
└── README.md                # Tài liệu hướng dẫn sử dụng
```

---

## 📦 Cài Đặt

### 1. Yêu cầu hệ thống
- **Python**: 3.10 trở lên
- **Trình duyệt**: Microsoft Edge hoặc Google Chrome (dùng cho Playwright)

### 2. Cài đặt thư viện
```bash
# Di chuyển vào thư mục của app
cd Shopee-Price-Checker

# Cài đặt các gói phụ thuộc
pip install -r requirements.txt

# Cài đặt Playwright browsers (nếu chưa có)
playwright install chromium
```

### 3. Đăng nhập tạo Session (Tùy chọn nhưng khuyến nghị)
Để tránh bị giới hạn lượt tìm kiếm bởi Shopee bot-detection, hãy quét QR để đăng nhập:
```bash
python auth.py
```
> Trình duyệt sẽ mở trang đăng nhập QR Shopee. Dùng ứng dụng Shopee trên điện thoại để quét mã. Sau khi thành công, session sẽ tự động lưu vào `session_state.json`.

---

## 🚀 Hướng Dẫn Sử Dụng

### 1. Tra cứu tự động qua từ khóa & phân loại
```bash
# Tìm kiếm sản phẩm CPU i5 10400F, phân loại Tray
python check_price.py --keyword "i5 10400f" --variant "tray"

# Xuất kết quả dạng bảng trực quan (mặc định)
python check_price.py --keyword "chuột logitech g102" --format table

# Xuất kết quả dạng JSON cho AI hoặc phần mềm khác tích hợp
python check_price.py --keyword "ram ddr4 16gb" --format json
```

### 2. Tra cứu trực tiếp từ danh sách URL cụ thể
```bash
python check_price.py --keyword "bàn phím cơ" --urls "https://shopee.vn/product/...1" "https://shopee.vn/product/...2"
```

### 3. Chế độ tương tác từng bước (Interactive Mode)
```bash
python check_price.py --interactive
```

---

## 🧪 Chạy Kiểm Thử (Unit Tests)

Kiểm tra toàn bộ thuật toán lọc biến thể, loại trừ giá mồi, quét review và benchmark giá:

```bash
python test_verifier.py
```

Kết quả mong đợi:
```text
--- BẮT ĐẦU CHẠY UNIT TEST VERIFIER ---
[PASS] Test khớp đúng phân loại 'tray', né giá mồi keo tản nhiệt 25k.
[PASS] Test khớp đúng phân loại 'box'.
[PASS] Test tự động né phụ kiện mồi khi không có target_variant.
[PASS] Test đánh giá shop uy tín (SAFE).
[PASS] Test phát hiện shop rủi ro: HIGH_RISK...
[PASS] Test đối soát giá thị trường (Benchmark) và phát hiện giá ảo.
[PASS] Test tính giá cuối cùng sau ship và voucher thành công!
✅ TẤT CẢ CÁC TEST CASE ĐÃ VƯỢT QUA!
```

---

## 📄 License

Dự án phát hành dưới giấy phép [MIT License](https://opensource.org/licenses/MIT).
