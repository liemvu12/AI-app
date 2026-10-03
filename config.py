"""
Cấu hình cho AGY Terminal Bridge
"""
import os
import shutil

# Đường dẫn agy executable (tự động dò tìm trên hệ thống)
AGY_PATH = shutil.which("agy") or r"C:\Users\PC\AppData\Local\agy\bin\agy.exe"

# Chỉ thị bắt buộc AI luôn trả lời bằng tiếng Việt (giữ nguyên code/identifiers tiếng Anh)
VIETNAMESE_DIRECTIVE = (
    "[CHỈ THỊ HỆ THỐNG QUAN TRỌNG: Bạn là trợ lý lập trình AGY. "
    "Dù prompt của người dùng bằng tiếng Anh hay tiếng Việt, bạn BẮT BUỘC phải luôn giải thích, "
    "hướng dẫn và trả lời hoàn toàn bằng Tiếng Việt chuẩn mực, rõ ràng, dễ hiểu. "
    "Các đoạn mã nguồn, cú pháp lệnh terminal, tên hàm, tên biến và thuật ngữ kỹ thuật quốc tế "
    "vẫn giữ nguyên bằng tiếng Anh chuẩn.]\n\n"
)

# Cấu hình phím tắt mặc định
HOTKEYS = {
    "toggle_translate": "ctrl+t",     # Đổi chiều dịch trong Quick Translate
    "send_english": "ctrl+e",         # Gửi prompt tiếng Anh trong English Panel sang AI
    "copy_original": "ctrl+o",        # Sao chép trực tiếp prompt gốc vào Clipboard
    "focus_translate": "ctrl+backslash", # Nhảy nhanh vào ô Quick Translate
    "escape": "escape",               # Trở về ô nhập prompt chính
    "switch_pane": "tab",             # Chuyển đổi focus giữa các khung
}
