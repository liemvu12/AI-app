"""
AGY English Companion (Cập nhật thời gian thực qua Console Buffer)
Đọc trực tiếp bộ đệm màn hình Terminal (Console Screen Buffer).
Khắc phục triệt để 100% lỗi phông chữ / lặp chữ do bộ gõ tiếng Việt Unikey / Telex / EVKey.
"""
import sys
import os
import threading

if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widgets import Static, Input, Button
from textual.binding import Binding
from textual.timer import Timer

from services.language_helper import process_prompt_for_learning
from services.translator import translate_text
from services.clipboard import copy_to_clipboard
from services.transcript_watcher import AGYTranscriptWatcher
from services.terminal_reader import TerminalScreenReader
from services.window_switcher import WindowSwitcher
from services.ollama_client import is_ollama_running
from ui.widgets.ollama_installer import OllamaInstallerModal


SHORTCUTS_HELP_TEXT = """[bold cyan]⚙ DANH SÁCH PHÍM TẮT HỆ THỐNG (HOTKEYS & SHORTCUTS)[/bold cyan]

[bold yellow]• Alt + A / F9 / Ctrl + Alt + A:[/bold yellow] [white]Chuyển đổi qua lại giữa Terminal AGY và Companion[/white]
[bold yellow]• Alt + Left:[/bold yellow] [white]Chuyển sang Terminal AGY (Khung trái)[/white]
[bold yellow]• Alt + Right:[/bold yellow] [white]Chuyển sang Companion & tự động nhảy con trỏ vào ô nhập nháp[/white]
[bold yellow]• Ctrl + Space:[/bold yellow] [white]Kích hoạt AI kiểm tra ngữ pháp & dịch khi đang ở Terminal AGY[/white]
[bold yellow]• Ctrl + R / Alt + R:[/bold yellow] [white]Tự động copy prompt chuẩn, xóa prompt cũ trong AGY, dán & gửi Enter[/white]
[bold yellow]• Ctrl + O:[/bold yellow] [white]Sao chép trực tiếp bản prompt gốc vào Clipboard[/white]
[bold yellow]• Ctrl + L / Esc:[/bold yellow] [white]Reset / Xóa sạch prompt nháp & đóng bảng phím tắt[/white]
[bold yellow]• Ctrl + T:[/bold yellow] [white]Đổi chiều dịch trong Quick Translate [VI ➔ EN] ⇄ [EN ➔ VI][/white]
[bold yellow]• Ctrl + \\:[/bold yellow] [white]Nhảy nhanh con trỏ đến ô tra từ Quick Translate[/white]
[bold yellow]• Tab:[/bold yellow] [white]Chuyển đổi con trỏ giữa ô soạn nháp và ô tra từ[/white]
[bold yellow]• F1:[/bold yellow] [white]Bật / tắt nhanh bảng phím tắt này[/white]

[dim italic]👉 Nhấn lại nút ⚙, phím F1 hoặc phím Esc để đóng danh sách.[/dim italic]"""


COMPANION_CSS = """
Screen {
    background: #0c0e14;
    color: #d1d5db;
    layout: vertical;
    overflow: hidden;
}

#english-panel {
    height: 65%;
    border-bottom: solid #262936;
    padding: 1;
    layout: vertical;
    overflow: hidden;
}

#header-bar {
    height: 1;
    layout: horizontal;
    margin-bottom: 1;
}

#english-title {
    width: 1fr;
    height: 1;
    color: #8b949e;
    text-style: bold;
}

#btn-settings {
    width: auto;
    min-width: 17;
    height: 1;
    min-height: 1;
    background: #21262d;
    color: #58a6ff;
    border: none;
    padding: 0 1;
    text-style: bold;
    text-align: center;
    content-align: center middle;
}

#btn-settings:hover {
    background: #30363d;
    color: #79c0ff;
}

#btn-settings:focus {
    background: #388bfd;
    color: #ffffff;
    text-style: bold;
}

#shortcuts-dropdown {
    display: none;
    height: auto;
    max-height: 13;
    background: #161b22;
    border: solid #30363d;
    padding: 1;
    margin-bottom: 1;
    overflow-y: auto;
}

#shortcuts-dropdown.open {
    display: block;
}

#shortcuts-content {
    color: #d1d5db;
}

#draft-input {
    height: 3;
    border: solid #262936;
    background: #0c0e14;
    color: #f3f4f6;
    margin-bottom: 1;
}

#draft-input:focus {
    border: solid #10b981;
}

#realtime-scroll-view {
    height: 1fr;
    background: #0c0e14;
    border: solid #262936;
    overflow-y: scroll;
    scrollbar-gutter: stable;
    scrollbar-size-vertical: 2;
    scrollbar-color: #388bfd #161b22;
    scrollbar-background: #0c0e14;
    padding: 0 1;
}

#english-preview {
    height: auto;
    color: #9ca3af;
    padding: 1 0;
}

#buttons-row {
    height: 1;
    margin-top: 1;
    layout: horizontal;
}

#btn-replace-prompt {
    width: 1fr;
    height: 1;
    min-height: 1;
    background: #1a1e29;
    color: #c9d1d9;
    border: none;
    padding: 0;
    text-align: center;
    content-align: center middle;
    margin-right: 1;
}

#btn-replace-prompt:hover {
    background: #262c3a;
    color: #ffffff;
}

#btn-replace-prompt:focus {
    background: #262c3a;
    color: #ffffff;
    text-style: bold;
}

#btn-copy-original {
    width: 1fr;
    height: 1;
    min-height: 1;
    background: #1a1e29;
    color: #c9d1d9;
    border: none;
    padding: 0;
    text-align: center;
    content-align: center middle;
    margin-right: 1;
}

#btn-copy-original:hover {
    background: #262c3a;
    color: #ffffff;
}

#btn-copy-original:focus {
    background: #262c3a;
    color: #ffffff;
    text-style: bold;
}

#btn-reset {
    width: 1fr;
    height: 1;
    min-height: 1;
    background: #1a1e29;
    color: #c9d1d9;
    border: none;
    padding: 0;
    text-align: center;
    content-align: center middle;
}

#btn-reset:hover {
    background: #262c3a;
    color: #ffffff;
}

#btn-reset:focus {
    background: #262c3a;
    color: #ffffff;
    text-style: bold;
}

#quick-translate-panel {
    height: 35%;
    padding: 1;
    layout: vertical;
}

#translate-title {
    height: 1;
    color: #9ca3af;
    text-style: bold;
    border-bottom: solid #1f2330;
    margin-bottom: 1;
}

#dict-input {
    height: 3;
    border: solid #262936;
    background: #0c0e14;
    color: #f3f4f6;
    margin-bottom: 1;
}

#dict-input:focus {
    border: solid #3b82f6;
}

#dict-result {
    height: 1fr;
    background: #0c0e14;
    border: none;
    overflow-y: auto;
    color: #10b981;
}

#status-bar {
    dock: bottom;
    height: 1;
    background: #141721;
    color: #6b7280;
    padding: 0 1;
    border-top: solid #262936;
}
"""


class AGYCompanionApp(App):
    CSS = COMPANION_CSS
    TITLE = "AGY DEV ENGLISH COMPANION"

    BINDINGS = [
        Binding("alt+a", "toggle_app_context", "Đổi app", priority=True),
        Binding("f9", "toggle_app_context", "Đổi app", priority=True),
        Binding("alt+left", "switch_to_agy", "Sang AGY", priority=True),
        Binding("alt+right", "focus_draft", "Vào ô nhập", priority=True),
        Binding("ctrl+r", "replace_prompt", "Thay thế & Gửi", priority=True),
        Binding("ctrl+o", "copy_original", "Copy bản gốc", priority=True),
        Binding("ctrl+l", "reset_all", "Reset / Xóa sạch", priority=True),
        Binding("ctrl+t", "toggle_translate", "Đổi chiều dịch", priority=True),
        Binding("tab", "switch_focus", "Chuyển ô", priority=True),
        Binding("ctrl+backslash", "focus_dict", "Tra từ", priority=True),
        Binding("escape", "reset_all", "Reset / Xóa sạch", priority=True),
        Binding("f1", "toggle_shortcuts", "Phím tắt", priority=True),
    ]

    def __init__(self):
        super().__init__()
        self._current_english_result: str = ""
        self._latest_replacement_prompt: str = ""
        self._last_original_prompt: str = ""
        self.source_lang = "vi"
        self.target_lang = "en"

        # Khởi tạo bộ chuyển đổi ngữ cảnh cửa sổ kèm callback tự động focus ô nhập và tự động thay thế
        self.window_switcher = WindowSwitcher(
            on_companion_focused=lambda: self.call_from_thread(self.focus_draft_input),
            on_auto_replace=lambda: self.call_from_thread(self.action_replace_prompt),
            on_trigger_ai_check=lambda: self.call_from_thread(self.action_trigger_ai_check)
        )

        # 1. Bộ đọc trực tiếp Console Screen Buffer (Loại bỏ 100% xung đột Unikey)
        self.screen_reader = TerminalScreenReader(
            on_text_change=self.handle_terminal_text_change,
            on_submit=self.handle_terminal_enter_submit,
            on_idle=self.handle_terminal_idle
        )

        # 2. Bộ theo dõi transcript (Safety net khi paste hoặc qua history)
        self.transcript_watcher = AGYTranscriptWatcher(on_new_prompt=self.handle_agy_transcript_prompt)

    def compose(self) -> ComposeResult:
        with Vertical(id="english-panel"):
            with Horizontal(id="header-bar"):
                yield Static("─ DEV ENGLISH ─", id="english-title")
                yield Button("[⚙ Phím tắt [F1]]", id="btn-settings", tooltip="Danh sách phím tắt hệ thống [F1]")
            with Vertical(id="shortcuts-dropdown"):
                yield Static(SHORTCUTS_HELP_TEXT, id="shortcuts-content")
            yield Input(
                placeholder="Soạn prompt nháp (nhấn Enter để dịch/sửa)...",
                id="draft-input"
            )
            with VerticalScroll(id="realtime-scroll-view"):
                yield Static(
                    "[dim]• Trạng thái:[/dim] [bold green]Đang kết nối trực tiếp Terminal AGY...[/bold green]\n"
                    "[dim]Nhấn Enter (tại ô nháp) hoặc Ctrl+Space (tại terminal) để kích hoạt AI.[/dim]",
                    id="english-preview"
                )
            with Horizontal(id="buttons-row"):
                yield Button("Thay thế & Gửi [Ctrl+R]", id="btn-replace-prompt")
                yield Button("Copy bản gốc [Ctrl+O]", id="btn-copy-original")
                yield Button("Reset / Xóa sạch [Ctrl+L]", id="btn-reset")

        with Vertical(id="quick-translate-panel"):
            yield Static("─ QUICK TRANSLATE: VI ➔ EN [Ctrl+T] ─", id="translate-title")
            yield Input(
                placeholder="Tra từ/cụm từ nhanh... (Enter)",
                id="dict-input"
            )
            yield Static("[dim]Kết quả tra cứu nhanh...[/dim]", id="dict-result")

        yield Static(
            " F1: Phím tắt [⚙] | Alt+A: Chuyển app | Ctrl+R: Thay & Gửi | Ctrl+O: Copy gốc | Ctrl+L: Reset | Ctrl+T: Dịch | Tab: Chuyển ô",
            id="status-bar"
        )

    def on_mount(self) -> None:
        self.screen_reader.start()
        self.transcript_watcher.start()
        self.window_switcher.start_global_hotkeys()
        self.focus_draft_input()
        
        if not is_ollama_running():
            self.push_screen(OllamaInstallerModal())
        else:
            self.query_one("#english-title").update("─ DEV ENGLISH [🟢 AI Pro Max] ─")

    def on_unmount(self) -> None:
        self.window_switcher.stop_global_hotkeys()
        self.screen_reader.stop()
        self.transcript_watcher.stop()

    def on_app_focus(self, event=None) -> None:
        """Tự động nhảy con trỏ thẳng vào ô nhập dữ liệu khi cửa sổ nhận focus"""
        self.focus_draft_input()

    def focus_draft_input(self) -> None:
        try:
            draft = self.query_one("#draft-input", Input)
            draft.focus()
        except Exception:
            pass
            
    def action_trigger_ai_check(self) -> None:
        """Kích hoạt kiểm tra ngữ pháp từ terminal (Ctrl+Space)"""
        text = self._last_original_prompt.strip()
        if text:
            # Chuyển cửa sổ sang companion để người dùng xem kết quả
            self.window_switcher.switch_to_companion()
            preview = self.query_one("#english-preview", Static)
            preview.update(
                f"[dim italic]🤖 AI đang phân tích ngữ nghĩa, vui lòng đợi...[/dim italic]\n\n"
                f"[dim]> \"{text}\"[/dim]"
            )
            self.run_worker(self._async_process_prompt(text), exclusive=True)

    # --- Console Buffer Handling từ Terminal ---

    def handle_terminal_idle(self) -> None:
        """Được gọi khi dòng lệnh trong Terminal AGY được xóa hoặc trở về trạng thái rỗng"""
        def _idle():
            self._last_original_prompt = ""
            self._render_terminal_idle()
        self._safe_call(_idle)

    def handle_terminal_text_change(self, text: str) -> None:
        """
        Được gọi tức thì khi nội dung dòng lệnh trên Terminal AGY thay đổi.
        """
        trimmed = text.strip()
        if not trimmed:
            self.handle_terminal_idle()
            return

        def _schedule():
            self._render_terminal_typing(trimmed)
            # Không gọi phân tích tự động nữa, chờ nhấn Ctrl+Space

        self._safe_call(_schedule)

    def _render_terminal_idle(self) -> None:
        preview = self.query_one("#english-preview", Static)
        status = "[🟢 AI Pro Max]" if is_ollama_running() else "[🔴 Dự phòng]"
        preview.update(
            f"[dim]• Trạng thái:[/dim] [bold green]Đang kết nối Terminal AGY {status}...[/bold green]\n"
            "[dim]Nhấn Enter (ở ô nháp) hoặc Ctrl+Space (ở Terminal) để kích hoạt AI.[/dim]"
        )

    def _render_terminal_typing(self, text: str) -> None:
        self._last_original_prompt = text
        preview = self.query_one("#english-preview", Static)
        length_hint = f"[dim]📏 Độ dài: [bold cyan]{len(text)} ký tự[/bold cyan][/dim]"
        if len(text) > 80:
            length_hint += " [dim yellow]| Thanh trượt bên phải [▲▼] đã kích hoạt để cuộn[/dim yellow]"

        preview.update(
            f"[bold yellow]🔴 ĐANG GÕ TRÊN TERMINAL:[/bold yellow] {length_hint}\n\n"
            f"[bold white]\"{text}\"[/bold white]\n\n"
            f"[dim italic]Nhấn [Ctrl+Space] để gửi AI sửa lỗi & tối ưu...[/dim italic]"
        )

    async def _async_analyze_terminal(self, text: str) -> None:
        pass # Không còn dùng nữa do bỏ debounce

    def handle_terminal_enter_submit(self, text: str) -> None:
        def _submit():
            self._last_original_prompt = text
            self.handle_terminal_idle()
        self._safe_call(_submit)

    def handle_agy_transcript_prompt(self, prompt: str) -> None:
        def _transcript():
            self._last_original_prompt = prompt
            res = process_prompt_for_learning(prompt)
            self._render_terminal_result(res, True)
        self._safe_call(_transcript)

    def _render_terminal_result(self, res: dict, is_submitted: bool = False) -> None:
        original = res.get("original", "")
        english_version = res.get("english_version", "")
        grammar_fixed = res.get("grammar_fixed", "")
        grammar_notes = res.get("grammar_notes", [])
        has_error = res.get("has_grammar_error", False)
        badge = res.get("badge", "")
        is_command = res.get("is_command", False)
        lang = res.get("lang", "")

        # Lưu lại prompt gốc và prompt đã sửa / tối ưu để phục vụ nút Thay thế
        self._last_original_prompt = original
        self._latest_replacement_prompt = english_version or grammar_fixed or original

        preview = self.query_one("#english-preview", Static)
        status_tag = "[⚡ ĐÃ GỬI TỪ TERMINAL AGY]" if is_submitted else "[🔴 REAL-TIME TỪ TERMINAL AGY]"

        length_hint = f"[dim]📏 Độ dài: [bold cyan]{len(original)} ký tự[/bold cyan][/dim]"
        if len(original) > 80 or len(english_version) > 80:
            length_hint += " [dim yellow]| Dùng thanh trượt bên phải [▲▼] để xem toàn bộ[/dim yellow]"

        if is_command:
            formatted = (
                f"[bold cyan]{status_tag} {badge}[/bold cyan] {length_hint}\n\n"
                f"[white]Lệnh CLI: {original}[/white]\n"
                f"[dim]💡 Lệnh hệ thống terminal (không cần dịch).[/dim]"
            )
        elif lang == "en" and has_error:
            # HIỂN THỊ CHI TIẾT SỬA LỖI NGỮ PHÁP TIẾNG ANH (PRO MAX LEVEL)
            notes_text = "\n".join([f"  • {n}" for n in grammar_notes[:6]])
            formatted = (
                f"[bold red]{status_tag} [EN GRAMMAR & SYNTAX ERROR DETECTED][/bold red] {length_hint}\n\n"
                f"[dim]Câu bạn gõ:[/dim] [white]\"{original}\"[/white]\n\n"
                f"[bold green]✔ Đã sửa ngữ pháp:[/bold green]\n"
                f"[bold white]\"{grammar_fixed}\"[/bold white]\n\n"
                f"[bold cyan]🚀 Dev Polish (Chuẩn kỹ thuật):[/bold cyan]\n"
                f"[bold cyan]\"{english_version}\"[/bold cyan]\n\n"
                f"[bold yellow]Chi tiết lỗi đã sửa:[/bold yellow]\n"
                f"{notes_text}\n\n"
                f"[bold green]👉 Nhấn nút [Thay thế prompt đã sửa] bên dưới (hoặc Ctrl+R) để áp dụng ngay![/bold green]"
            )
        elif lang == "en":
            formatted = (
                f"[bold green]{status_tag} [EN GRAMMAR ACCURATE][/bold green] {length_hint}\n\n"
                f"[dim]Câu bạn gõ:[/dim] [white]\"{original}\"[/white]\n\n"
                f"[bold cyan]Engineering Polish:[/bold cyan]\n"
                f"[bold cyan]\"{english_version}\"[/bold cyan]\n\n"
                f"[dim]💡 Ngữ pháp chuẩn xác.[/dim]\n\n"
                f"[dim]👉 Nhấn nút [Thay thế prompt đã sửa] bên dưới (hoặc Ctrl+R) để lấy câu tối ưu.[/dim]"
            )
        else:
            # Tiếng Việt dịch sang tiếng Anh kỹ thuật
            formatted = (
                f"[bold green]{status_tag} {badge}[/bold green] {length_hint}\n\n"
                f"[dim]Đang gõ (VI):[/dim] [white]\"{original}\"[/white]\n\n"
                f"[bold white]English Dev Version:[/bold white]\n"
                f"[bold cyan]\"{english_version}\"[/bold cyan]\n\n"
                f"[dim]💡 Đã tối ưu hóa sang Engineering English.[/dim]\n\n"
                f"[bold green]👉 Nhấn nút [Thay thế prompt đã sửa] bên dưới (hoặc Ctrl+R) để áp dụng ngay![/bold green]"
            )
        preview.update(formatted)

    def _safe_call(self, func, *args, **kwargs) -> None:
        if threading.current_thread() is threading.main_thread():
            func(*args, **kwargs)
        else:
            self.call_from_thread(func, *args, **kwargs)

    # --- Actions ---

    def action_toggle_translate(self) -> None:
        if self.source_lang == "vi":
            self.source_lang = "en"
            self.target_lang = "vi"
        else:
            self.source_lang = "vi"
            self.target_lang = "en"

        title_box = self.query_one("#translate-title", Static)
        title_box.update(f"─ QUICK TRANSLATE: {self.source_lang.upper()} ➔ {self.target_lang.upper()} [Ctrl+T] ─")

        inp = self.query_one("#dict-input", Input)
        if inp.value.strip():
            self._do_quick_translate(inp.value.strip())

    def action_switch_focus(self) -> None:
        draft = self.query_one("#draft-input", Input)
        dict_in = self.query_one("#dict-input", Input)
        if draft.has_focus:
            dict_in.focus()
        else:
            draft.focus()

    def action_focus_dict(self) -> None:
        self.query_one("#dict-input", Input).focus()

    def action_focus_draft(self) -> None:
        self.query_one("#draft-input", Input).focus()

    # --- Soạn nháp trên ô Draft ---

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "draft-input":
            text = event.value.strip()
            preview = self.query_one("#english-preview", Static)

            if not text:
                self._current_english_result = ""
                self._render_terminal_idle()
                return

            self._last_original_prompt = text
            preview.update(
                f"[dim italic]Đang nháp... Nhấn Enter để gửi cho AI phân tích.[/dim italic]\n\n"
                f"[dim]> \"{text}\"[/dim]"
            )

    async def _async_process_prompt(self, text: str) -> None:
        import asyncio
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, process_prompt_for_learning, text)
        
        self._current_english_result = res.get("english_version", "").strip()
        grammar_fixed = res.get("grammar_fixed", "")
        grammar_notes = res.get("grammar_notes", [])
        has_error = res.get("has_grammar_error", False)
        badge = res.get("badge", "")
        lang = res.get("lang", "")
        self._last_original_prompt = text
        self._latest_replacement_prompt = self._current_english_result or grammar_fixed or text

        preview = self.query_one("#english-preview", Static)
        length_hint = f"[dim]📏 Độ dài: [bold cyan]{len(text)} ký tự[/bold cyan][/dim]"
        if len(text) > 80 or len(self._current_english_result) > 80:
            length_hint += " [dim yellow]| Dùng thanh trượt bên phải [▲▼] để xem toàn bộ[/dim yellow]"

        if lang == "en" and has_error:
            notes_text = "\n".join([f"  • {n}" for n in grammar_notes[:4]])
            formatted = (
                f"[bold red]{badge} [PHÁT HIỆN LỖI NGỮ PHÁP][/bold red] {length_hint}\n\n"
                f"[dim]Bản gốc:[/dim] [white]\"{text}\"[/white]\n\n"
                f"[bold green]✔ Đã sửa ngữ pháp:[/bold green]\n"
                f"[bold white]\"{grammar_fixed}\"[/bold white]\n\n"
                f"[bold cyan]🚀 Dev Polish (Chuẩn kỹ thuật):[/bold cyan]\n"
                f"[bold cyan]\"{self._current_english_result}\"[/bold cyan]\n\n"
                f"[bold yellow]Chi tiết lỗi đã sửa:[/bold yellow]\n"
                f"{notes_text}\n\n"
                f"[bold green]👉 Nhấn nút [Thay thế & Gửi] bên dưới (hoặc Ctrl+R) để tự động gửi sang AGY![/bold green]"
            )
        else:
            formatted = (
                f"[bold green]{badge}[/bold green] {length_hint}\n\n"
                f"[bold white]English Dev Version:[/bold white]\n"
                f"[cyan]\"{self._current_english_result}\"[/cyan]\n\n"
                f"[dim]💡 {res.get('explanation', '')}[/dim]\n\n"
                f"[bold green]👉 Nhấn nút [Thay thế & Gửi] bên dưới (hoặc Ctrl+R) để tự động gửi sang AGY![/bold green]"
            )
        preview.update(formatted)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-settings":
            self.action_toggle_shortcuts()
        elif event.button.id == "btn-replace-prompt":
            self.action_replace_prompt()
        elif event.button.id == "btn-copy-original":
            self.action_copy_original()
        elif event.button.id == "btn-reset":
            self.action_reset_all()

    def action_toggle_shortcuts(self) -> None:
        """Bật/tắt xổ danh sách phím tắt từ nút răng cưa"""
        dd = self.query_one("#shortcuts-dropdown")
        if "open" in dd.classes:
            dd.remove_class("open")
        else:
            dd.add_class("open")

    def action_focus_draft(self) -> None:
        """Đặt ngay con trỏ vào ô nhập liệu nháp"""
        self.focus_draft_input()

    def action_toggle_app_context(self) -> None:
        """Chuyển đổi qua lại giữa AGY Terminal và Companion"""
        self.window_switcher.toggle_context()

    def action_switch_to_agy(self) -> None:
        """Chuyển nhanh tiêu điểm sang cửa sổ Terminal AGY"""
        self.window_switcher.switch_to_agy()

    def action_reset_all(self) -> None:
        """
        Xóa sạch toàn bộ prompt và kết quả trong app,
        hoặc đóng bảng phím tắt nếu đang mở.
        """
        dd = self.query_one("#shortcuts-dropdown")
        if "open" in dd.classes:
            dd.remove_class("open")
            return

        draft = self.query_one("#draft-input", Input)
        draft.value = ""

        self._render_terminal_idle()

        self._current_english_result = ""
        self._latest_replacement_prompt = ""
        self._last_original_prompt = ""

        # Đặt ngay con trỏ vào vị trí nhập tài liệu
        draft.focus()

    def action_replace_prompt(self) -> None:
        """
        Tự động:
        1. Lấy prompt mới đã sửa ngữ pháp / chuẩn hoá tiếng Anh kỹ thuật.
        2. Copy vào clipboard.
        3. Cập nhật vào ô draft-input.
        4. Chuyển sang AGY Terminal.
        5. Xóa prompt cũ trong AGY Terminal.
        6. Dán (Ctrl+V) prompt mới vào vị trí prompt cũ.
        7. Nhấn Enter để gửi đi ngay cho AGY!
        """
        replacement = self._latest_replacement_prompt.strip()
        if not replacement:
            draft = self.query_one("#draft-input", Input)
            if self._current_english_result:
                replacement = self._current_english_result.strip()
            elif draft.value.strip():
                replacement = draft.value.strip()

        preview = self.query_one("#english-preview", Static)
        if not replacement:
            preview.update("[bold yellow]⚠ Chưa có prompt nào được phân tích để thay thế![/bold yellow]")
            return

        # 1. Sao chép trực tiếp vào Windows Clipboard
        copy_to_clipboard(replacement)

        # 2. Cập nhật vào ô draft-input nếu có
        draft = self.query_one("#draft-input", Input)
        draft.value = replacement
        draft.cursor_position = len(replacement)

        # 3. Hiển thị thông báo trên màn hình
        length_hint = f"[dim]📏 Độ dài: {len(replacement)} ký tự[/dim]"
        preview.update(
            f"[bold green]✔ ĐANG TỰ ĐỘNG THAY THẾ & GỬI SANG TERMINAL AGY...[/bold green] {length_hint}\n\n"
            f"[bold white]Prompt chuẩn kỹ thuật:[/bold white]\n"
            f"[bold cyan]\"{replacement}\"[/bold cyan]\n\n"
            f"[bold green]🚀 Đang xóa prompt cũ ➔ Dán prompt mới ➔ Tự động gửi Enter sang AGY![/bold green]"
        )

        # 4. Kích hoạt quy trình tự động xóa prompt cũ, paste và gửi enter sang AGY
        old_prompt = self._last_original_prompt
        self.window_switcher.auto_replace_and_send_to_agy(old_prompt, replacement)

    def action_copy_original(self) -> None:
        """
        Sao chép trực tiếp bản prompt gốc (nguyên văn đang gõ trên terminal hoặc ô nháp) vào Clipboard.
        """
        text_to_copy = self._last_original_prompt.strip()
        if not text_to_copy:
            draft = self.query_one("#draft-input", Input)
            if draft.value.strip():
                text_to_copy = draft.value.strip()

        preview = self.query_one("#english-preview", Static)
        if not text_to_copy:
            preview.update("[bold yellow]⚠ Chưa có prompt gốc nào để sao chép![/bold yellow]")
            return

        success = copy_to_clipboard(text_to_copy)
        if success:
            length_hint = f"[dim]📏 Độ dài: {len(text_to_copy)} ký tự[/dim]"
            preview.update(
                f"[bold green]✔ ĐÃ SAO CHÉP BẢN GỐC VÀO CLIPBOARD![/bold green] {length_hint}\n\n"
                f"[bold white]Nội dung bản gốc:[/bold white]\n"
                f"[bold cyan]\"{text_to_copy}\"[/bold cyan]\n\n"
                f"[dim italic]✓ Đã lưu vào Clipboard, sẵn sàng dán (Ctrl+V) vào bất kỳ đâu.[/dim italic]"
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "draft-input":
            text = event.value.strip()
            if text:
                preview = self.query_one("#english-preview", Static)
                preview.update(
                    f"[dim italic]🤖 AI đang phân tích ngữ nghĩa, vui lòng đợi...[/dim italic]\n\n"
                    f"[dim]> \"{text}\"[/dim]"
                )
                self.run_worker(self._async_process_prompt(text), exclusive=True)
        elif event.input.id == "dict-input":
            val = event.value.strip()
            if val:
                self._do_quick_translate(val)

    def _do_quick_translate(self, text: str) -> None:
        result_box = self.query_one("#dict-result", Static)
        result_box.update("[dim italic]Đang tra cứu...[/dim italic]")

        def _work():
            translated = translate_text(text, source_lang=self.source_lang, target_lang=self.target_lang)
            copy_to_clipboard(translated)
            display = (
                f"[dim]Từ gốc ({self.source_lang.upper()}):[/dim] {text}\n"
                f"[bold green]Kết quả ({self.target_lang.upper()}):[/bold green] [bold underline]{translated}[/bold underline]\n"
                f"[dim italic]✓ Đã tự động sao chép kết quả vào Clipboard.[/dim italic]"
            )
            self.call_from_thread(result_box.update, display)

        import threading
        threading.Thread(target=_work, daemon=True).start()


def launch_split_terminal():
    """
    Kích hoạt Windows Terminal ở chế độ chia đôi màn hình Split-Pane:
    - Khung trái 67%: Terminal AGY nguyên bản (powershell agy)
    - Khung phải 33%: AGY Dev English Companion (--tui)
    Giống 100% khi chạy launch_split.bat.
    """
    if sys.platform == "win32":
        try:
            import ctypes
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)  # Ẩn console launcher trung gian
        except Exception:
            pass

    bridge_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = bridge_dir
    python_exe = os.path.join(bridge_dir, ".venv", "Scripts", "python.exe")
    companion_script = os.path.join(bridge_dir, "companion.py")
    standalone_exe = os.path.join(bridge_dir, "AGYCompanion.exe")
    dist_exe = os.path.join(bridge_dir, "dist", "AGYCompanion.exe")

    if getattr(sys, "frozen", False):
        companion_cmd = f'& "{sys.executable}" --tui'
    elif os.path.exists(python_exe) and os.path.exists(companion_script):
        companion_cmd = f'& "{python_exe}" "{companion_script}" --tui'
    elif os.path.exists(standalone_exe):
        companion_cmd = f'& "{standalone_exe}" --tui'
    elif os.path.exists(dist_exe):
        companion_cmd = f'& "{dist_exe}" --tui'
    else:
        companion_cmd = f'& python "{companion_script}" --tui'

    cmd = [
        "wt",
        "-d", workspace_dir,
        "powershell", "-NoExit", "-Command", "agy",
        ";",
        "split-pane", "-V", "-s", "0.33",
        "-d", bridge_dir if os.path.exists(bridge_dir) else workspace_dir,
        "powershell", "-NoExit", "-Command", companion_cmd
    ]

    import subprocess
    try:
        subprocess.Popen(cmd)
    except Exception:
        # Fallback nếu Windows Terminal không có sẵn
        try:
            subprocess.Popen(["powershell", "-NoExit", "-Command", "agy"], cwd=workspace_dir)
            subprocess.Popen(["powershell", "-NoExit", "-Command", companion_cmd], cwd=bridge_dir)
        except Exception:
            pass


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "--daemon":
            from services.console_daemon import main as daemon_main
            daemon_main()
            return
        elif arg in ("--tui", "--companion", "--app"):
            app = AGYCompanionApp()
            app.run()
            return

    # Khi người dùng mở trực tiếp AGYCompanion.exe (không tham số):
    # Khởi chạy Windows Terminal ở chế độ chia đôi màn hình Split-Pane:
    # Khung trái: Terminal AGY gốc (67%)
    # Khung phải: AGY Dev English Companion (--tui) (33%)
    # Giống hệt 100% khi mở file launch_split.bat
    launch_split_terminal()


if __name__ == "__main__":
    main()
