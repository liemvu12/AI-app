# Rule: Cổng kiểm định dữ liệu linh hoạt & đa tầng (Tiered Verification Gate)

## Bối cảnh và Tầm quan trọng
Trên sàn Shopee, nhiều linh kiện máy tính đặc thù (như VGA cũ/lướt, CPU tray, mainboard, vỏ case theo đợt) mỗi bài đăng thường có số lượng giới hạn, khó đạt điều kiện cứng nhắc `sold > 100` dù người bán là gian hàng lớn (Shopee Mall hoặc Shop Yêu Thích) có hàng nghìn đánh giá uy tín. Việc áp dụng cứng nhắc quy tắc lượt bán > 100 dẫn đến việc loại bỏ nhầm các deal tốt, uy tín của người dùng.

Vì vậy, hệ thống áp dụng **Quy chuẩn đánh giá uy tín đa tầng (Tiered Trust System)** kết hợp chặt chẽ giữa: huy hiệu shop (Mall, Yêu Thích), chất lượng bình luận, điểm sao và lượt bán thực tế.

## Quy tắc bắt buộc đối với AI:

1. **100% Dữ liệu báo giá phải xuất phát từ mảng `trusted_deals`:**
   Mọi link sản phẩm, tên shop, biến thể chính xác, đơn giá thực tế, phí ship và voucher đưa vào bảng báo giá cuối cùng gửi cho người dùng **BẮT BUỘC PHẢI ĐƯỢC KIỂM ĐỊNH QUA TOOL `check_price.py` VÀ NẰM TRONG MẢNG `trusted_deals`**.

2. **Tiêu chuẩn công nhận deal đạt chuẩn (`trusted_deals`):**
   Một sản phẩm được chấp thuận vào báo giá nếu đáp ứng **ĐIỀU KIỆN TIÊN QUYẾT** và **MỘT TRONG CÁC TẦNG UY TÍN**:

   * **Điều kiện tiên quyết (Bắt buộc 100%):**
     * Còn hàng thật trong kho (`has_stock: True`, `stock > 0`).
     * Không dính cờ giá mồi phụ kiện hoặc giá ảo trên trời (`price_status: REASONABLE`).
     * Không dính cờ rủi ro nghiêm trọng trong bình luận 1-2 sao (`risk_level: SAFE` - không có phốt lừa đảo, trâu cày rỉ sét, cắm không lên, chối bỏ bảo hành).

   * **Tầng 1 - Shopee Mall hoặc Shop Yêu Thích / Yêu Thích+:**
     * Đã được sàn Shopee xác minh định danh và cam kết chất lượng.
     * Chỉ cần sản phẩm có phát sinh đơn bán thực tế (`sold >= 5`), điểm đánh giá shop uy tín (`rating_star >= 4.5` hoặc shop có lượng review tích cực lớn).
   
   * **Tầng 2 - Shop thường nhưng có điểm tín nhiệm cao:**
     * Điểm đánh giá sản phẩm/shop cao (`rating_star >= 4.7`).
     * Có lượt bán thực tế từ 15 chiếc trở lên (`sold >= 15`).
   
   * **Tầng 3 - Hàng mới phổ thông 100%:**
     * Ưu tiên các sản phẩm có lượt mua cao (`sold >= 50` hoặc `sold > 100`).

3. **Nghiêm cấm "Đi tắt đón đầu" (No Shortcut / No Unverified Links):**
   - **TUYỆT ĐỐI KHÔNG** đưa bất kỳ đường link Shopee nào vào bảng báo giá nếu link đó chưa được chạy qua lệnh:
     ```bash
     python check_price.py --keyword "<tên món>" --urls "<link>" --format json
     ```
   - **TUYỆT ĐỐI KHÔNG** tự ý lấy mức giá ước lượng thị trường bên ngoài rồi ghép bừa vào một link chưa được bóc tách bằng Playwright.

4. **Báo cáo trung thực và minh bạch khi không có deal đạt chuẩn (Transparent Reporting):**
   - Nếu một linh kiện sau khi quét qua tool mà không tìm thấy shop nào đạt chuẩn (bị xếp vào `other_deals_flagged` do hết hàng, giá ảo, shop dính phốt hoặc shop mới tạo 0 lượt bán):
     * AI phải báo cáo thẳng thắn cho người dùng: *"Linh kiện này hiện trên Shopee đang hết hàng hoặc bị các shop đẩy giá ảo, chưa có deal đạt chuẩn uy tín"*.
     * Giải thích rõ lý do bị loại bỏ và đề xuất phương án thay thế có kiểm chứng.
     * **TUYỆT ĐỐI KHÔNG** che giấu bằng cách đưa link của shop chưa đạt chuẩn vào bảng giá.
