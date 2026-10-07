---
name: shopee-price-checker
description: >-
  Tra cứu giá thực tế sản phẩm trên sàn Shopee, tự động bóc tách phân loại (bản tray, box, dung lượng, màu sắc), loại bỏ giá mồi của phụ kiện kèm theo, kiểm tra tồn kho thật (stock > 0), lọc shop uy tín (Shopee Mall / Yêu thích / đánh giá cao), quét nhanh cảnh báo nghiêm trọng trong review 1-2 sao và tính giá trung vị thị trường. BẮT BUỘC: Lượt bán phải lớn hơn 100 (sold > 100), đơn giản hóa phân tích bình luận; Khi tra cứu thiết bị đơn lẻ phải hỏi rõ mức giá mong muốn; khi build hệ thống phải hỏi đồ đã có, lên danh sách cần mua và chờ người dùng xác nhận trước khi tra đơn giá.
---

# Shopee Price Checker Skill

Skill này trang bị cho AI khả năng tra cứu giá sản phẩm trên sàn Shopee Việt Nam với độ chính xác cao nhất, loại bỏ hoàn toàn các loại dữ liệu rác (giá mồi, sản phẩm hết hàng, gian thương lừa đảo, trâu cày nát), tối ưu tốc độ tra cứu và tuân thủ quy trình tương tác chuẩn mực.

---

## ⚡ 1. CÁC QUY TẮC LỌC NHANH & CHẤT LƯỢNG (FAST & TRUSTED RULES)

1. **Số lượng lượt mua bắt buộc lớn hơn 100 (`sold > 100`):**
   - Chỉ đối soát các sản phẩm đã có trên 100 lượt bán thành công.
   - Bỏ qua các shop mới tạo, shop không có lượt mua hoặc lượt mua lẹt đẹt (< 100) để tối ưu thời gian tìm kiếm và đảm bảo uy tín thị trường.
2. **Đơn giản hóa phân tích bình luận (Lightweight Review Analysis):**
   - Chỉ quét nhanh các từ khóa rủi ro nghiêm trọng trong đánh giá 1-2 sao: `"lừa đảo"`, `"hàng giả"`, `"fake"`, `"trâu cày"`, `"rỉ sét"`, `"cháy"`, `"không lên"`, `"chối bỏ"`.
   - Nếu có từ 2 đánh giá tiêu cực chứa từ khóa trên -> gắn cờ cảnh báo `HIGH_RISK` và loại bỏ.

---

## ⚠️ 2. QUY TRÌNH HỎI & XÁC NHẬN BẮT BUỘC (MANDATORY INQUIRY PROTOCOL)

Khi người dùng kích hoạt skill hoặc yêu cầu tìm kiếm, **AI TUYỆT ĐỐI KHÔNG TỰ Ý CHẠY TOOL LÊN ĐƠN GIÁ NGAY LẬP TỨC** mà phải tuân theo 2 quy tắc sau:

### Quy tắc 1: Khi tra cứu sản phẩm / thiết bị đơn lẻ
- Nếu người dùng chưa nêu rõ khoảng ngân sách, **AI phải hỏi rõ lại người dùng:**
  > *"Bạn cần tìm thiết bị này trong tầm giá khoảng bao nhiêu? (Ví dụ: dưới 1 triệu, khoảng 2-3 triệu, hàng mới chính hãng hay hàng cũ lướt giá tốt?)"*
- Sau khi người dùng phản hồi mức giá mong muốn, AI mới tiến hành lọc và tra cứu các sản phẩm khớp đúng khoảng giá đó.

### Quy tắc 2: Khi người dùng yêu cầu build hệ thống (Case PC, Samsung DeX, Mini PC, dàn máy làm việc...)
AI phải thực hiện nghiêm ngặt quy trình 3 bước trước khi lên đơn giá:
1. **Bước 1 - Khảo sát linh kiện đã có sẵn:**
   - Hỏi trực tiếp người dùng:
     > *"Để tối ưu chi phí và tránh mua trùng lặp, hiện tại bạn/anh/chị **đã có sẵn những linh kiện hoặc thiết bị gì rồi?** (Ví dụ: đã có màn hình, phím chuột, nguồn, vỏ case, ổ cứng SSD, củ sạc... chưa?)"*
2. **Bước 2 - Lên danh sách các món cần mua:**
   - Dựa trên nhu cầu và những món người dùng còn thiếu, AI đề xuất **Danh sách các linh kiện dự kiến cần mua** (chỉ liệt kê tên linh kiện và phân loại dự kiến, **chưa chạy tool tra cứu giá chi tiết**).
3. **Bước 3 - Yêu cầu người dùng xác nhận:**
   - Đặt câu hỏi xác nhận:
     > *"Bạn vui lòng xem lại danh sách các món cần mua trên đã đúng ý chưa hoặc có cần thêm/bớt món nào không? Hãy xác nhận để mình tiến hành đối soát giá thực tế và tìm shop rẻ/uy tín nhất trên Shopee nhé!"*
4. **Bước 4 - Triển khai tra cứu đơn giá:**
   - **CHỈ KHI người dùng xác nhận đồng ý**, AI mới sử dụng script `check_price.py` để tìm kiếm sản phẩm, kiểm tra tồn kho thật, mô phỏng giỏ hàng tính phí ship/voucher và lập bảng báo giá hoàn chỉnh.

---

## 3. Cách thực thi lệnh (Execution Runbook)

Chạy lệnh qua tool `run_command` trong thư mục `Shopee-Price-Checker`:

```bash
# Cách 1: Tự động khám phá qua Search Engine
python check_price.py --keyword "<Từ khóa sản phẩm>" --variant "<Phân loại cần tìm>" --format json

# Cách 2 (Khuyên dùng cho AI): Dùng tool search_web tìm nhanh link Mall/Yêu thích rồi truyền trực tiếp:
python check_price.py --keyword "<Từ khóa sản phẩm>" --variant "<Phân loại cần tìm>" --urls "<url_1>" "<url_2>" --format json

# Cách 3: Chế độ tương tác khảo sát nhu cầu trực tiếp trên terminal:
python check_price.py --interactive
```

### Các tham số quan trọng:
* `--keyword` (Bắt buộc trong chế độ CLI thường): Tên sản phẩm chính (Ví dụ: `"i5 10400F"`, `"Kalite KL6100"`).
* `--variant` (Khuyên dùng): Chuỗi từ khóa của phân loại mong muốn (Ví dụ: `"tray"`, `"box"`, `"6L"`).
* `--urls` (Tùy chọn): Danh sách URL Shopee cụ thể cần đối soát.
* `--min-rating`: Đánh giá sao tối thiểu của shop (mặc định: `4.6`).
* `--min-sold`: Số lượng bán tối thiểu (mặc định: `100`, bắt buộc phải lớn hơn 100 lượt bán).
* `--strict-shop`: Thêm cờ này nếu người dùng yêu cầu chỉ mua ở Shopee Mall hoặc Shop Yêu Thích.
* `--format`: Đặt là `json` để AI dễ đọc cấu trúc dữ liệu, hoặc `table` để xem bảng trực quan.

---

## 4. Cách đọc dữ liệu trả về từ Tool

Kết quả JSON trả về gồm 2 mảng chính:
1. `trusted_deals`: Danh sách các gian hàng **ĐÃ ĐẠT CHUẨN**:
   - Khớp đúng phân loại cần mua.
   - Còn hàng thật (`stock > 0`, `has_stock: true`).
   - Lượt bán đạt tiêu chuẩn (`sold > 100`).
   - Shop uy tín, đã quét nhanh bình luận không có phốt lừa đảo/hàng lỗi (`risk_level: SAFE`).
   - Mức giá nằm trong khoảng trung vị hợp lý của thị trường (`price_status: REASONABLE`).
   - **Đã mô phỏng chọn mua trong giỏ hàng (TUYỆT ĐỐI KHÔNG THANH TOÁN):**
     - `matched_price`: Tiền hàng thật của phân loại.
     - `shipping_fee`: Phí ship thực tế phải trả (sau khi áp mã Freeship).
     - `voucher_discount`: Mức giảm giá từ Voucher Shop tối ưu nhất.
     - `final_price`: **Tổng thanh toán cuối cùng = Tiền hàng + Phí ship - Voucher shop**.
     - `buyer_location`: Địa chỉ nhận hàng dự kiến của tài khoản.
2. `other_deals_flagged`: Các shop bị loại bỏ:
   - `SUSPICIOUS_LOW`: Giá rẻ bất thường (giá mồi phụ kiện hoặc hàng giả).
   - `HIGH_RISK`: Phát hiện bình luận phốt (lừa đảo, hàng trâu cày, rỉ sét, cắm không lên nguồn).
   - `OUT_OF_STOCK`: Đã hết hàng.

---

## 5. Mẫu báo cáo phản hồi cho Người dùng (Sau khi đã được xác nhận)

```markdown
### 🖥️ BÁO CÁO CẤU HÌNH [TÊN CẤU HÌNH] (ĐÃ ĐỐI SOÁT GIÁ, TỒN KHO, SHIP & VOUCHER THỰC TẾ)

| Linh kiện | Tên phân loại | Tiền hàng | Phí ship (Giảm) | Voucher Shop | GIÁ CUỐI CÙNG | Shop & Đánh giá | Link mua |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Sản phẩm** | Tên phân loại chuẩn | xxx.000đ | 0đ (Freeship) | -xx.000đ | **xxx.000đ** | Shop ABC (Mall, >100 đã bán) | [Xem link](url) |
| **TỔNG TIỀN** | | | | | **x.xxx.000đ** | | |

> 🛡️ **Cam kết an toàn hệ thống:**
> - Bước đối soát giỏ hàng chỉ tính toán mức thanh toán dự kiến — **TUYỆT ĐỐI KHÔNG TIẾN HÀNH THANH TOÁN HAY ĐẶT HÀNG**.
> - Chỉ chọn các gian hàng uy tín có trên 100 lượt bán thành công và không dính cảnh báo lừa đảo.
> - [Địa chỉ nhận hàng dự kiến: Tỉnh/Thành phố]
```
