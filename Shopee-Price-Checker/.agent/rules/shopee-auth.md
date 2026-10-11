# Rule: Bắt buộc xác thực phiên đăng nhập Shopee trước khi thực hiện tác vụ

## Bối cảnh và Tầm quan trọng
Shopee áp dụng cơ chế chống bot và xác minh bảo mật (mã lỗi 90309999). Nếu không có phiên đăng nhập hợp lệ (chứa cookie `SPC_ST`, `SPC_SI`, `SPC_SEC_SI` còn hạn), hệ thống sẽ bị chặn hoặc không thể lấy đúng giá giỏ hàng/voucher/phí vận chuyển thực tế.

## Quy tắc bắt buộc đối với AI:
1. **Kiểm tra phiên đăng nhập đầu tiên:**
   Trước khi tiến hành khảo sát, tra cứu giá hoặc bóc tách bất kỳ linh kiện/sản phẩm nào trên Shopee, AI phải kiểm tra trạng thái phiên qua hàm `is_session_valid()`.

2. **Hành động bắt buộc khi phiên hết hạn hoặc chưa có:**
   NẾU `is_session_valid() == False`:
   - AI **KHÔNG TỰ Ý CHẠY LỆNH `python auth.py`**.
   - AI **BẮT BUỘC PHẢI DỪNG LẠI VÀ YÊU CẦU NGƯỜI DÙNG CHẠY FILE `login_shopee.bat`** (nhấp đúp chuột vào file để mở giao diện quét mã QR đăng nhập Shopee).
   - **TUYỆT ĐỐI KHÔNG làm bất kỳ điều gì khác** (không tự ý tra cứu mò, không lên đơn giá dự đoán) cho đến khi người dùng chạy `login_shopee.bat` và hoàn tất đăng nhập.
