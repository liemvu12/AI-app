"""
Widget Khung Học Tiếng Anh Tối Giản (Minimalist English Learning & Polish Panel)
Cập nhật thời gian thực bản dịch tiếng Anh kỹ thuật hoặc sửa lỗi ngữ pháp.
"""
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button

SHORTCUTS_HELP_TEXT = """[bold cyan]⚙ DANH SÁCH PHÍM TẮT HỆ THỐNG (HOTKEYS & SHORTCUTS)[/bold cyan]

[bold yellow]• Enter:[/bold yellow] [white]Chạy lệnh trong Terminal[/white]
[bold yellow]• Ctrl + E:[/bold yellow] [white]Gửi câu tiếng Anh đã dịch/sửa lỗi sang AGY[/white]
[bold yellow]• Ctrl + T:[/bold yellow] [white]Đổi chiều dịch trong Quick Translate [VI ➔ EN] ⇄ [EN ➔ VI][/white]
[bold yellow]• Ctrl + \\:[/bold yellow] [white]Nhảy nhanh con trỏ đến ô tra từ Quick Translate[/white]
[bold yellow]• Tab / Shift+Tab:[/bold yellow] [white]Chuyển đổi qua lại giữa dòng lệnh và ô tra từ[/white]
[bold yellow]• Esc:[/bold yellow] [white]Trở về nhanh dòng lệnh Terminal agy>[/white]
[bold yellow]• F1:[/bold yellow] [white]Bật / tắt nhanh danh sách phím tắt này[/white]

[dim italic]👉 Nhấn lại nút [⚙ Phím tắt], phím F1 hoặc phím Esc để đóng.[/dim italic]"""


class EnglishPanel(Vertical):
    current_english_prompt: str = ""

    def compose(self) -> ComposeResult:
        with Horizontal(id="header-bar"):
            yield Static("─ DEV ENGLISH ─", id="english-title")
            yield Button("[⚙ Phím tắt [F1]]", id="btn-settings", tooltip="Danh sách phím tắt [F1]")
        with Vertical(id="shortcuts-dropdown"):
            yield Static(SHORTCUTS_HELP_TEXT, id="shortcuts-content")
        yield Static(
            "[dim]Gõ prompt ở dòng lệnh bên trái để xem bản dịch tiếng Anh kỹ thuật hoặc bản sửa lỗi ngữ pháp tại đây...[/dim]",
            id="english-content"
        )
        yield Static("[dim]Ctrl+E: Gửi câu tiếng Anh này sang AGY[/dim]", id="english-footer")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-settings":
            self.toggle_shortcuts()

    def toggle_shortcuts(self) -> None:
        dropdown = self.query_one("#shortcuts-dropdown")
        if "open" in dropdown.classes:
            dropdown.remove_class("open")
        else:
            dropdown.add_class("open")

    def show_analyzing(self, text: str) -> None:
        """
        Hiển thị trạng thái phản hồi tức thì 0ms khi người dùng vừa gõ phím.
        """
        content_box = self.query_one("#english-content", Static)
        if text.startswith("/"):
            content_box.update(
                f"[bold cyan]Lệnh hệ thống CLI:[/bold cyan] [white]{text}[/white]\n"
                f"[dim](Slash command - thực thi trực tiếp, không cần dịch)[/dim]"
            )
        else:
            content_box.update(
                f"[dim italic]Đang phân tích & dịch tiếng Anh kỹ thuật...[/dim italic]\n\n"
                f"[dim]> \"{text}\"[/dim]"
            )

    def clear_content(self) -> None:
        self.current_english_prompt = ""
        content_box = self.query_one("#english-content", Static)
        content_box.update("[dim]Chờ prompt...[/dim]")

    def update_result(self, result: dict) -> None:
        self.current_english_prompt = result.get("english_version", "").strip()
        badge = result.get("badge", "")
        explanation = result.get("explanation", "")
        is_command = result.get("is_command", False)

        content_box = self.query_one("#english-content", Static)
        
        if not self.current_english_prompt:
            content_box.update("[dim]Chờ prompt...[/dim]")
            return

        if is_command:
            content_box.update(
                f"[bold cyan]{badge}[/bold cyan]\n\n"
                f"[white]{self.current_english_prompt}[/white]\n\n"
                f"[dim]💡 {explanation}[/dim]"
            )
        else:
            content_box.update(
                f"[bold green]{badge}[/bold green]\n\n"
                f"[bold white]English Dev Version:[/bold white]\n"
                f"[cyan]\"{self.current_english_prompt}\"[/cyan]\n\n"
                f"[dim]💡 {explanation}[/dim]\n\n"
                f"[bold yellow]>> Bấm Ctrl+E để gửi câu EN này cho AGY <<[/bold yellow]"
            )

    def get_english_prompt(self) -> str:
        return self.current_english_prompt
