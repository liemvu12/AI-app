---
name: shopee-price-checker
description: >-
  Tra cứu giá thực tế sản phẩm trên sàn Shopee, tự động bóc tách phân loại (bản tray, box, dung lượng, màu sắc), loại bỏ giá mồi của phụ kiện kèm theo, kiểm tra tồn kho thật (stock > 0), lọc shop uy tín đa tầng (Shopee Mall / Yêu thích sold >= 5, Shop thường sold >= 15 & rating cao, hoặc hàng mới sold > 50), quét nhanh cảnh báo nghiêm trọng trong review 1-2 sao và tính giá trung vị thị trường. BẮT BUỘC: Nếu phiên đăng nhập Shopee chưa có hoặc hết hạn, AI phải dừng lại và yêu cầu người dùng chạy file 'login_shopee.bat' để đăng nhập trước khi làm bất kỳ điều gì (không tự ý chạy lệnh python auth.py); Khi tra cứu thiết bị đơn lẻ phải hỏi rõ mức giá mong muốn; khi build hệ thống phải hỏi đồ đã có, lên danh sách cần mua và chờ người dùng xác nhận trước khi tra đơn giá.
---

# Shopee Price Checker Skill

Skill này trang bị cho AI khả năng tra cứu giá sản phẩm trên sàn Shopee Việt Nam với độ chính xác cao nhất, loại bỏ hoàn toàn các loại dữ liệu rác (giá mồi, sản phẩm hết hàng, gian thương lừa đảo, trâu cày nát), tối ưu tốc độ tra cứu và tuân thủ quy trình tương tác chuẩn mực.

---

## 🔐 0. QUY TẮC BẮT BUỘC VỀ PHIÊN ĐĂNG NHẬP (MANDATORY AUTHENTICATION PROTOCOL)

**TRƯỚC KHI LÀM BẤT KỲ ĐIỀU GÌ (kể cả khảo sát hay tra cứu):**
1. AI phải kiểm tra tính hợp lệ của phiên đăng nhập (`python -c "from auth import is_session_valid; print(is_session_valid())"`).
2. **NẾU PHIÊN ĐĂNG NHẬP CHƯA CÓ HOẶC ĐÃ HẾT HẠN (`is_session_valid() == False`):**
   - **AI KHÔNG TỰ Ý CHẠY LỆNH `python auth.py`**.
   - **AI BẮT BUỘC PHẢI DỪNG LẠI VÀ YÊU CẦU NGƯỜI DÙNG CHẠY FILE `login_shopee.bat`** (nhấp đúp vào file để mở trình duyệt hiển thị mã QR và quét mã đăng nhập bằng điện thoại).
   - **TUYỆT ĐỐI KHÔNG làm bất kỳ điều gì khác** (không tự ý tra cứu giá, không kết luận số liệu giỏ hàng) trước khi người dùng chạy `login_shopee.bat` và phiên đăng nhập được xác nhận thành công!

---

## ⚡ 1. CÁC QUY TẮC LỌC ĐA TẦNG & CHẤT LƯỢNG (TIERED TRUST RULES)

1. **Đánh giá độ tin cậy đa tầng (Tiered Trust Evaluation - Không cứng nhắc `sold > 100`):**
   - **Tầng 1 (Shopee Mall / Shop Yêu Thích / Yêu Thích+):** Đã được Shopee định danh & kiểm duyệt. Chỉ cần có phát sinh đơn bán thực tế (`sold >= 5`), điểm đánh giá shop uy tín (`rating >= 4.5`), review không dính cờ rủi ro.
   - **Tầng 2 (Shop thường điểm tín nhiệm cao):** Đánh giá sản phẩm/shop cao (`rating >= 4.7`), lượt bán thực tế từ 15 chiếc trở lên (`sold >= 15`), không có khiếu nại lừa đảo trong review 1-2 sao.
   - **Tầng 3 (Hàng mới phổ thông 100%):** Ưu tiên các sản phẩm có lượt mua cao (`sold >= 50` hoặc `sold > 100`).
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
4. **Bước 4 - Triển khai tra cứu đơn giá qua Cổng kiểm định bắt buộc (Mandatory Verification Gate):**
   - **CHỈ KHI người dùng xác nhận đồng ý**, AI mới sử dụng script `check_price.py` để tìm kiếm sản phẩm, kiểm tra tồn kho thật, mô phỏng giỏ hàng tính phí ship/voucher và lập bảng báo giá hoàn chỉnh.
   - **QUY TẮC CỐT LÕI:** Mọi sản phẩm đưa vào bảng báo giá cuối cùng gửi cho người dùng **BẮT BUỘC 100% PHẢI NẰM TRONG MẢNG `trusted_deals` DO TOOL XUẤT RA**.
   - **TUYỆT ĐỐI NGHIÊM CẤM:** Không được phép lấy link từ search engine hoặc ước lượng giá ngoài đời rồi tự ý ghép vào bảng báo giá mà chưa qua đối soát thực tế của tool! Nếu sản phẩm bị `check_price.py` loại ra (`other_deals_flagged` hoặc `status: not_found`), AI phải báo thẳng cho người dùng là link đó không đạt chuẩn (hết hàng/giá ảo/sold < 100), không được phép che giấu hoặc đưa link rác cho người dùng.

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
