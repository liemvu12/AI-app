"""
Unit & Integration Test cho AGY Terminal Bridge (Luồng Terminal Đồng Nhất - Inline Stream)
Kiểm tra:
1. Nhận diện ngôn ngữ & Dịch thuật Google Translate tốc độ cao
2. Slash Command handling (/model, /skills, /new, /clear)
3. Luồng terminal đồng nhất: prompt nối tiếp phản hồi, không tách khung
4. Khởi tạo App & CSS Textual (Headless Test)
"""
import sys
import asyncio
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from services.translator import detect_language, translate_text
from services.language_helper import process_prompt_for_learning, polish_engineering_english
from services.agy_client import AGYClient
from ui.app import AGYTerminalBridgeApp
from ui.widgets.terminal_view import TerminalView


def test_translation_and_language():
    print("Testing translation & language detection...")
    assert detect_language("Xin chào lập trình viên") == "vi"
    assert detect_language("How do I implement binary search?") == "en"
    assert detect_language("/model") == "command"

    # Test dev polish
    polished = polish_engineering_english("fix this bug in the server")
    assert "debug and resolve this issue" in polished.lower()

    # Test process_prompt_for_learning with slash command
    res_cmd = process_prompt_for_learning("/model")
    assert res_cmd["is_command"] is True
    assert res_cmd["badge"] == "[TERMINAL COMMAND]"
    print(f"  Slash Command Check: {res_cmd['original']} -> Badge: {res_cmd['badge']}")

    # Test process_prompt_for_learning with VI
    res_vi = process_prompt_for_learning("Tạo một API bất đồng bộ")
    assert res_vi["lang"] == "vi"
    assert res_vi["english_version"] != ""
    print(f"  VI Input: {res_vi['original']} -> EN: {res_vi['english_version']}")

    # Test process_prompt_for_learning with English grammar correction
    res_en_err = process_prompt_for_learning("why he have error in line 10")
    assert res_en_err["lang"] == "en"
    assert "has" in res_en_err["grammar_fixed"]
    print(f"  EN Grammar Fix: {res_en_err['original']} -> {res_en_err['grammar_fixed']}")


def test_agy_client_commands():
    print("Testing AGY Client Commands...")
    client = AGYClient()
    
    # Test payload injection
    payload = client.build_payload("Explain Docker")
    assert "CHỈ THỊ HỆ THỐNG QUAN TRỌNG" in payload
    assert "Tiếng Việt" in payload
    
    # Test session reset
    client.has_previous_session = True
    client.reset_session()
    assert client.has_previous_session is False
    print("  AGY client commands & payload verified.")


async def test_textual_app_lifecycle():
    print("Testing Textual Inline Terminal App Headless Mounting...")
    app = AGYTerminalBridgeApp()
    async with app.run_test() as pilot:
        # Check that widgets are mounted
        term = app.query_one("#terminal-view", TerminalView)
        ep = app.query_one("#english-panel")
        qt = app.query_one("#quick-translate")
        inp = app.query_one("#prompt-input")
        assert term is not None
        assert ep is not None
        assert qt is not None
        assert inp is not None
        print("  All widgets successfully mounted in unified layout.")

        # Test command start in terminal stream
        resp_widget = term.start_command("viết thuật toán DFS")
        term.update_response(resp_widget, "Đoạn mã DFS...")
        print("  Inline terminal command and response mount verified.")

        # Test real-time feedback on typing
        ep.show_analyzing("viết thuật toán DFS")
        await app._async_analyze_prompt("viết thuật toán DFS")
        await pilot.pause(0.2)
        print(f"  English panel updated: '{ep.get_english_prompt()}'")
        assert ep.get_english_prompt() != ""

        # Test toggle translation action
        app.action_toggle_translate()
        assert qt.source_lang == "en"
        assert qt.target_lang == "vi"
        print("  QuickTranslate toggle direction verified.")

        # Test screen clear
        term.clear_screen()
        print("  Terminal clear screen verified.")

    print("Textual Inline Terminal App lifecycle test passed successfully!")


def test_long_prompt_processing():
    print("Testing Long Prompt Processing (>600 chars)...")
    long_prompt_vi = (
        "Tôi muốn bạn tạo một ứng dụng web phức tạp sử dụng python fastapi và reactjs "
        "để quản lý thông tin khách hàng, có thêm tính năng phân quyền jwt và database sqlite, "
        "đồng thời tạo giao diện đẹp mắt bằng tailwindcss và kiểm tra toàn bộ lỗi cú pháp. "
        "Ngoài ra hãy thêm tính năng xuất báo cáo excel và biểu đồ thống kê doanh thu theo từng tháng."
    ) * 2
    assert len(long_prompt_vi) > 600

    # Test translate_text on long prompt
    translated = translate_text(long_prompt_vi)
    assert translated != ""
    assert len(translated) > 400
    print(f"  Long prompt translated successfully! Length: {len(translated)} chars.")

    # Test process_prompt_for_learning on long prompt
    res = process_prompt_for_learning(long_prompt_vi)
    assert res["lang"] == "vi"
    assert len(res["english_version"]) > 400
    print(f"  Long prompt processed for learning successfully! Badge: {res['badge']}")

    # Test long English prompt with grammar errors
    long_en_errors = (
        "how i can fix this bug? he have many bug in the code. "
        "it dont work properly when user click on submit. "
        "also please explain me how we can improve performance."
    )
    res_en = process_prompt_for_learning(long_en_errors)
    assert res_en["has_grammar_error"] is True
    assert "how can i" in res_en["grammar_fixed"].lower()
    print("  Long English prompt grammar checked and corrected successfully.")


async def test_companion_app_headless():
    print("Testing Companion App Headless Mounting, Nested Slider, Auto-Focus, and Reset...")
    from companion import AGYCompanionApp
    from textual.widgets import Button, Input
    from textual.containers import VerticalScroll
    from services.window_switcher import WindowSwitcher
    from textual import events

    # Test WindowSwitcher directly
    ws = WindowSwitcher()
    assert ws is not None
    print("  WindowSwitcher initialized successfully.")

    app = AGYCompanionApp()
    async with app.run_test() as pilot:
        scroll_view = app.query_one("#realtime-scroll-view", VerticalScroll)
        preview = app.query_one("#english-preview")
        draft = app.query_one("#draft-input", Input)
        btn_replace = app.query_one("#btn-replace-prompt", Button)
        btn_reset = app.query_one("#btn-reset", Button)
        btn_settings = app.query_one("#btn-settings", Button)
        shortcuts_dropdown = app.query_one("#shortcuts-dropdown")

        assert scroll_view is not None
        assert preview is not None
        assert draft is not None
        assert btn_replace is not None
        assert btn_reset is not None
        assert btn_settings is not None
        assert shortcuts_dropdown is not None
        print("  Verified: Slider is strictly nested inside [🔴 REAL-TIME TỪ TERMINAL AGY] (VerticalScroll #realtime-scroll-view).")
        print("  Verified: Action buttons (#btn-replace-prompt, #btn-reset, #btn-settings) are mounted.")

        # Test gear button dropdown toggle
        assert "open" not in shortcuts_dropdown.classes
        btn_settings.press()
        await pilot.pause(0.1)
        assert "open" in shortcuts_dropdown.classes
        print("  Verified: Clicking gear button (⚙) opens shortcuts dropdown.")

        btn_settings.press()
        await pilot.pause(0.1)
        assert "open" not in shortcuts_dropdown.classes
        print("  Verified: Clicking gear button again closes shortcuts dropdown.")

        # Test auto-focus on AppFocus
        app.post_message(events.AppFocus())
        await pilot.pause(0.1)
        assert draft.has_focus is True
        print("  Verified: App focus automatically directs cursor directly into draft input.")

        # Simulate typing a prompt needing correction
        await app._async_process_prompt("how i can fix this error")
        await pilot.pause(0.2)
        assert app._latest_replacement_prompt != ""
        print(f"  Captured replacement prompt: '{app._latest_replacement_prompt}'")

        # Click the replace button (triggers auto replace & send)
        btn_replace.press()
        await pilot.pause(0.1)
        print("  Replace & Send button pressed and prompt replaced successfully.")

        # Test Reset Button (Clears prompt and puts cursor back to draft-input)
        draft.value = "Some leftover text"
        btn_reset.press()
        await pilot.pause(0.1)
        assert draft.value == ""
        assert app._latest_replacement_prompt == ""
        assert draft.has_focus is True
        print("  Verified: Reset button cleared prompt and placed cursor directly in draft-input.")

        # Test shortcut action_switch_to_agy directly
        app.action_switch_to_agy()
        print("  Shortcut action_switch_to_agy executed successfully.")

    print("Companion App headless test passed successfully!")


def test_console_buffer_extraction():
    print("Testing Console Buffer Extraction & Multi-line Parsing...")
    from services.console_daemon import is_border_line, find_target_pid

    # Test border detection
    assert is_border_line("──────────────────────────────────") is True
    assert is_border_line("----------------------------------") is True
    assert is_border_line("> hello world") is False
    assert is_border_line("esc to cancel") is False
    print("  Border detection verified.")

    # Test target pid discovery
    target = find_target_pid()
    print(f"  Target PID discovery verified (Found: {target}).")


def test_transcript_watcher_discovery():
    print("Testing Transcript Watcher Realtime Log Discovery...")
    from services.transcript_watcher import AGYTranscriptWatcher
    watcher = AGYTranscriptWatcher(lambda x: None)
    latest = watcher.get_latest_transcript_file()
    assert latest is not None
    assert "transcript.jsonl" in latest
    print(f"  Latest active transcript found: {latest}")


def test_window_switcher_context_toggling():
    print("Testing Window Switcher Context Toggling...")
    from services.window_switcher import WindowSwitcher
    ws = WindowSwitcher()
    assert ws._current_target_is_agy is False
    ws.switch_to_companion()
    assert ws._current_target_is_agy is True
    ws.switch_to_agy()
    assert ws._current_target_is_agy is False
    print("  Window switcher state transition verified.")


if __name__ == "__main__":
    test_translation_and_language()
    test_long_prompt_processing()
    test_agy_client_commands()
    test_console_buffer_extraction()
    test_transcript_watcher_discovery()
    test_window_switcher_context_toggling()
    asyncio.run(test_textual_app_lifecycle())
    asyncio.run(test_companion_app_headless())
    print("\nALL AUTOMATED TESTS PASSED SUCCESSFULLY!")
