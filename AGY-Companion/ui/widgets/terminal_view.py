"""
Widget Terminal Dòng Lệnh Đồng Nhất (Inline Terminal Stream)
Không chia tách ô nhập prompt và ô phản hồi; prompt luôn nằm nối tiếp ngay sau
các phản hồi trước đó, cuộn cùng một luồng như terminal/bash/powershell thật.
"""
from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Static, Input
from rich.markdown import Markdown


class TerminalView(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Static(
            "[dim]AGY Terminal Console [CLI Interface][/dim]\n"
            "[dim]Hỗ trợ đầy đủ lệnh: /help, /model, /effort, /skills, /agents, /new, /clear[/dim]\n"
            "[dim]───────────────────────────────────────────────────────────────────────[/dim]\n",
            id="terminal-banner"
        )
        with Horizontal(id="active-input-row"):
            yield Static("agy> ", id="prompt-prefix")
            yield Input(placeholder="Nhập lệnh hoặc prompt...", id="prompt-input")

    def start_command(self, cmd: str, is_english: bool = False) -> Static:
        """
        Ghi nhận lệnh người dùng vừa nhập trực tiếp vào luồng terminal
        và tạo placeholder cho phản hồi của AI/hệ thống ngay bên dưới.
        """
        input_row = self.query_one("#active-input-row")
        
        # 1. Khóa dòng lệnh đã gõ thành văn bản tĩnh trong luồng
        tag = " [dim](Sent as English prompt)[/dim]" if is_english else ""
        cmd_widget = Static(f"[bold green]agy>[/bold green] [bold white]{cmd}[/bold white]{tag}", classes="term-cmd")
        self.mount(cmd_widget, before=input_row)

        # 2. Tạo placeholder cho output
        response_widget = Static("[dim italic]Đang xử lý...[/dim italic]", classes="term-response")
        self.mount(response_widget, before=input_row)
        
        self.scroll_end(animate=False)
        return response_widget

    def update_response(self, response_widget: Static, text: str) -> None:
        """
        Cập nhật nội dung phản hồi theo thời gian thực (hỗ trợ render Markdown)
        """
        if not text.strip():
            response_widget.update("")
            return

        if "```" in text or "# " in text or "\n- " in text or "\n* " in text:
            response_widget.update(Markdown(text))
        else:
            response_widget.update(text)
            
        self.scroll_end(animate=False)

    def append_system_msg(self, msg: str) -> None:
        """
        Chèn thông báo hệ thống vào luồng terminal
        """
        input_row = self.query_one("#active-input-row")
        msg_widget = Static(f"[dim yellow]! {msg}[/dim yellow]", classes="term-system")
        self.mount(msg_widget, before=input_row)
        self.scroll_end(animate=False)

    def clear_screen(self) -> None:
        """
        Xóa sạch màn hình, giữ lại banner và dòng input hiện tại
        """
        input_row = self.query_one("#active-input-row")
        for child in list(self.children):
            if child != input_row and child.id != "terminal-banner":
                child.remove()
        self.scroll_end(animate=False)
