"""
Ứng dụng Giao diện Terminal AGY (AGY Terminal Bridge)
Trải nghiệm dòng lệnh Terminal đồng nhất (Inline Terminal Stream) - không chia tách ô nhập và ô trả lời.
Tích hợp 2 cửa sổ tối giản hỗ trợ học tiếng Anh & dịch nhanh.
"""
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Input
from textual.binding import Binding
from textual.timer import Timer
from textual import work

from config import HOTKEYS
from services.language_helper import process_prompt_for_learning
from services.agy_client import AGYClient
from .widgets import TerminalView, EnglishPanel, QuickTranslate


class AGYTerminalBridgeApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "AGY TERMINAL BRIDGE"

    BINDINGS = [
        Binding("f1", "toggle_shortcuts", "Phím tắt", show=False, priority=True),
        Binding(HOTKEYS["toggle_translate"], "toggle_translate", "Đổi chiều dịch", priority=True),
        Binding(HOTKEYS["send_english"], "send_english_prompt", "Gửi bản tiếng Anh", priority=True),
        Binding(HOTKEYS["focus_translate"], "focus_translate", "Tra từ", priority=True),
        Binding(HOTKEYS["escape"], "focus_input", "Về dòng lệnh", priority=True),
    ]

    def __init__(self):
        super().__init__()
        self.agy_client = AGYClient()
        self._debounce_timer: Timer | None = None
        self._command_history: list[str] = []
        self._history_index: int = -1

    def compose(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            # Cột trái: Luồng Terminal đồng nhất (chứa cả log, prompt input và response)
            yield TerminalView(id="terminal-view")

            # Cột phải: 2 cửa sổ tối giản hỗ trợ tiếng Anh
            with Vertical(id="sidebar-column"):
                yield EnglishPanel(id="english-panel")
                yield QuickTranslate(id="quick-translate")

        # Thanh trạng thái tối giản 1 dòng
        yield Static(
            " F1: Phím tắt [⚙] | Enter: Chạy | Ctrl+E: Gửi tiếng Anh | Ctrl+T: Đổi chiều | Ctrl+\\: Tra từ | Tab: Chuyển ô",
            id="status-bar"
        )

    def on_mount(self) -> None:
        self.query_one("#prompt-input", Input).focus()

    # --- Phím tắt & Actions ---

    def action_toggle_shortcuts(self) -> None:
        english_panel = self.query_one("#english-panel", EnglishPanel)
        english_panel.toggle_shortcuts()

    def action_toggle_translate(self) -> None:
        quick_translate = self.query_one("#quick-translate", QuickTranslate)
        quick_translate.toggle_direction()

    def action_focus_translate(self) -> None:
        self.query_one("#dict-input", Input).focus()

    def action_focus_input(self) -> None:
        self.query_one("#prompt-input", Input).focus()

    def action_send_english_prompt(self) -> None:
        english_panel = self.query_one("#english-panel", EnglishPanel)
        en_prompt = english_panel.get_english_prompt()
        term = self.query_one("#terminal-view", TerminalView)

        if not en_prompt:
            term.append_system_msg("Chưa có câu tiếng Anh nào trong English Learning Panel để gửi.")
            return

        self.dispatch_command_to_agy(en_prompt, is_english_override=True)

    # --- Phản hồi thời gian thực khi gõ Prompt ---

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "prompt-input":
            if self._debounce_timer:
                self._debounce_timer.stop()

            raw_text = event.value.strip()
            english_panel = self.query_one("#english-panel", EnglishPanel)

            if not raw_text:
                english_panel.clear_content()
                return

            # Phản hồi tức thì 0ms trên giao diện
            english_panel.show_analyzing(raw_text)

            # Nếu là slash command thì phân tích ngay lập tức
            if raw_text.startswith("/"):
                res = process_prompt_for_learning(raw_text)
                english_panel.update_result(res)
                return

            # Hẹn giờ 200ms để chạy phân tích ngôn ngữ và dịch kỹ thuật
            self._debounce_timer = self.set_timer(
                0.2,
                lambda: self._start_async_analysis(raw_text)
            )

    def _start_async_analysis(self, text: str) -> None:
        self.run_worker(self._async_analyze_prompt(text), exclusive=True)

    async def _async_analyze_prompt(self, text: str) -> None:
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, process_prompt_for_learning, text)
        english_panel = self.query_one("#english-panel", EnglishPanel)
        english_panel.update_result(result)

    # --- Xử lý thực thi lệnh Terminal & AGY trong cùng luồng ---

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "prompt-input":
            cmd = event.value.strip()
            if not cmd:
                return

            # Reset ô input ngay lập tức
            event.input.value = ""

            # Lưu vào lịch sử lệnh
            if not self._command_history or self._command_history[-1] != cmd:
                self._command_history.append(cmd)
            self._history_index = len(self._command_history)

            term = self.query_one("#terminal-view", TerminalView)

            # Xử lý lệnh xóa màn hình
            if cmd in ("/clear", "clear"):
                term.clear_screen()
                return

            # Xử lý lệnh thoát
            if cmd in ("/exit", "/quit", "exit", "quit"):
                self.exit()
                return

            self.dispatch_command_to_agy(cmd, is_english_override=False)

    @work(exclusive=False)
    async def dispatch_command_to_agy(self, cmd_line: str, is_english_override: bool = False) -> None:
        term = self.query_one("#terminal-view", TerminalView)
        
        # 1. Khóa lệnh vào luồng terminal và tạo placeholder cho phản hồi
        response_widget = term.start_command(cmd_line, is_english=is_english_override)

        # 2. Cập nhật English Panel ngay lập tức
        import asyncio
        loop = asyncio.get_event_loop()
        analysis = await loop.run_in_executor(None, process_prompt_for_learning, cmd_line)
        english_panel = self.query_one("#english-panel", EnglishPanel)
        english_panel.update_result(analysis)

        # 3. Thực thi qua AGY CLI và stream kết quả trực tiếp vào vị trí phản hồi
        accumulated = []
        try:
            async for chunk in self.agy_client.execute_command(cmd_line):
                accumulated.append(chunk)
                term.update_response(response_widget, "".join(accumulated))

            final_text = "".join(accumulated).strip()
            if final_text:
                term.update_response(response_widget, final_text)
            else:
                term.update_response(response_widget, "[dim](Lệnh hoàn tất, không có kết quả trả về)[/dim]")
        except Exception as exc:
            term.update_response(response_widget, f"[bold red]Lỗi: {str(exc)}[/bold red]")
        finally:
            # Cuộn xuống cuối và tiếp tục focus vào ô input ở vị trí mới
            term.scroll_end(animate=False)
            self.query_one("#prompt-input", Input).focus()
