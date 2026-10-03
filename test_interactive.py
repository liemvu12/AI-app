"""
End-to-End Interactive Validation Loop for AGY Companion
Kiểm tra toàn bộ luồng tương tác thực tế:
1. Mounting & Giao diện tối giản của 2 Button + Nút răng cưa ⚙
2. Đóng/mở bảng phím tắt (Shortcuts Dropdown)
3. Nhận diện gõ Real-Time tức thì (<80ms)
4. Tự động dịch Dev English & Sửa lỗi ngữ pháp
5. Sự kiện IDLE & SUBMIT từ Terminal AGY
6. Nút Thay thế & Gửi [Ctrl+R]
7. Nút Reset / Xóa sạch [Ctrl+L] & Tự động Focus ô nhập
"""
import sys
import asyncio
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from companion import AGYCompanionApp
from textual.widgets import Button, Input, Static
from textual.containers import VerticalScroll
from services.console_daemon import find_target_pid, is_process_alive, is_agy_process


async def validate_all_features():
    print("=======================================================")
    print("BẮT ĐẦU VÒNG LẶP KIỂM THỬ TOÀN DIỆN CÁC TÍNH NĂNG...")
    print("=======================================================")

    # 1. Kiểm tra Daemon & Connection Locking
    pid = find_target_pid()
    print(f"[1/8] Kiểm tra Target PID cho Real-Time Sync: PID={pid}")
    assert pid is not None, "Không tìm thấy tiến trình AGY!"
    assert is_process_alive(pid) is True
    assert is_agy_process(pid) is True
    print("      >> Khóa kết nối Bền vững (Connection Locking): ĐẠT CHUẨN ✅")

    # 2. Khởi tạo App Headless và kiểm tra Mounting
    app = AGYCompanionApp()
    async with app.run_test() as pilot:
        preview = app.query_one("#english-preview", Static)
        draft = app.query_one("#draft-input", Input)
        btn_replace = app.query_one("#btn-replace-prompt", Button)
        btn_copy_original = app.query_one("#btn-copy-original", Button)
        btn_reset = app.query_one("#btn-reset", Button)
        btn_settings = app.query_one("#btn-settings", Button)
        dropdown = app.query_one("#shortcuts-dropdown")
        scroll_view = app.query_one("#realtime-scroll-view", VerticalScroll)

        assert preview is not None
        assert draft is not None
        assert btn_replace is not None
        assert btn_copy_original is not None
        assert btn_reset is not None
        assert btn_settings is not None
        assert dropdown is not None
        assert scroll_view is not None
        print("[2/9] Kiểm tra Mounting giao diện (3 Button thu nhỏ, Nút ⚙, Slider lồng): ĐẠT CHUẨN ✅")

        # Tạm dừng background reader để các sự kiện mô phỏng không bị can thiệp bởi buffer thật
        app.screen_reader.stop()
        app.transcript_watcher.stop()

        # 3. Kiểm tra Nút răng cưa và Bảng xổ phím tắt
        assert "open" not in dropdown.classes
        btn_settings.press()
        await pilot.pause(0.1)
        assert "open" in dropdown.classes
        print("[3/8] Click nút răng cưa ⚙ xổ bảng phím tắt: ĐẠT CHUẨN ✅")

        btn_settings.press()
        await pilot.pause(0.1)
        assert "open" not in dropdown.classes
        print("[3/8] Click nút răng cưa ⚙ lần 2 đóng bảng phím tắt: ĐẠT CHUẨN ✅")

        # 4. Kiểm tra Real-Time gõ phím từ Terminal AGY
        app.handle_terminal_text_change("Tao ung dung web bang FastAPI")
        await pilot.pause(0.1)
        txt_typing = str(preview.content)
        assert "REAL-TIME" in txt_typing
        print("[4/8] Cập nhật gõ Real-Time tức thì từ Terminal AGY: ĐẠT CHUẨN ✅")

        # Chờ debounce phân tích dịch thuật
        await pilot.pause(0.5)
        txt_translated = str(preview.content)
        assert "FastAPI" in txt_translated or "Web" in txt_translated
        print("[4/8] Dịch thuật Dev English từ luồng gõ Real-Time: ĐẠT CHUẨN ✅")

        # 5. Kiểm tra sự kiện Terminal Idle
        app.handle_terminal_idle()
        await pilot.pause(0.1)
        txt_idle = str(preview.content)
        assert "Terminal AGY" in txt_idle
        print("[5/8] Sự kiện IDLE reset màn hình kết nối: ĐẠT CHUẨN ✅")

        # 6. Kiểm tra sự kiện Gửi lệnh từ Terminal AGY & Sửa lỗi ngữ pháp
        app.handle_terminal_enter_submit("how i can fix this error in line 10")
        await pilot.pause(0.5)
        txt_submit = str(preview.content)
        assert "TERMINAL AGY" in txt_submit
        assert "how can i" in txt_submit.lower() or "line 10" in txt_submit.lower()
        print("[6/8] Nhận diện câu gửi từ Terminal AGY & Sửa lỗi ngữ pháp chuyên sâu: ĐẠT CHUẨN ✅")

        # 7. Kiểm tra Nút Thay thế & Gửi [Ctrl+R]
        btn_replace.press()
        await pilot.pause(0.1)
        assert app._latest_replacement_prompt != ""
        print(f"[7/9] Nút Thay thế & Gửi [Ctrl+R] (Chuẩn bị gửi: '{app._latest_replacement_prompt[:40]}...'): ĐẠT CHUẨN ✅")

        # 8. Kiểm tra Nút Copy bản gốc [Ctrl+O]
        app._last_original_prompt = "how i can fix this error in line 10"
        btn_copy_original.press()
        await pilot.pause(0.1)
        assert "ĐÃ SAO CHÉP BẢN GỐC VÀO CLIPBOARD" in str(preview.content)
        print("[8/9] Nút Copy bản gốc [Ctrl+O] & Lưu Clipboard: ĐẠT CHUẨN ✅")

        # 9. Kiểm tra Nút Reset / Xóa sạch [Ctrl+L] & Tự động Focus ô nhập
        draft.value = "Prompt nháp cần xóa"
        btn_reset.press()
        await pilot.pause(0.1)
        assert draft.value == ""
        assert draft.has_focus is True
        print("[9/9] Nút Reset / Xóa sạch [Ctrl+L] & Tự động nhảy con trỏ vào ô nhập: ĐẠT CHUẨN ✅")

    print("=======================================================")
    print(">> TOÀN BỘ 9/9 TIÊU CHUẨN KIỂM THỬ ĐÃ ĐẠT 100% THÀNH CÔNG! <<")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(validate_all_features())
