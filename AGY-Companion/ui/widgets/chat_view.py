"""
Widget Khung Chat chính (Main Chat View)
Hiển thị lịch sử hội thoại với AGY, hỗ trợ định dạng Markdown và syntax highlighting.
"""
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, RichLog
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text


class ChatView(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("💬 AGY CHAT STREAM (Luôn phản hồi Tiếng Việt)", id="chat-title")
        yield RichLog(id="chat-log", highlight=True, markup=True, wrap=True)

    def on_mount(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        welcome_md = Markdown(
            "### Chào mừng đến với AGY Terminal Bridge!\n"
            "- Nhập yêu cầu bằng **Tiếng Việt** hoặc **Tiếng Anh** ở thanh nhập liệu bên dưới.\n"
            "- AI sẽ **luôn luôn trả lời bằng Tiếng Việt chuẩn**.\n"
            "- Góc phải trên: Tự động dịch sang Tiếng Anh chuyên ngành hoặc sửa lỗi ngữ pháp.\n"
            "- Góc phải dưới: Widget tra cứu nhanh từ điển / Google Translate (`Ctrl+T` đổi chiều)."
        )
        log.write(welcome_md)

    def append_user_message(self, text: str, is_english_override: bool = False) -> None:
        log = self.query_one("#chat-log", RichLog)
        tag = "[GỬI BẢN TIẾNG ANH (Ctrl+E)]" if is_english_override else "[BẠN]"
        log.write(f"\n[bold cyan]👤 {tag}:[/bold cyan] {text}")

    def append_ai_chunk(self, chunk: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(chunk, end="")

    def append_ai_full_message(self, text: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[bold green]🤖 [AGY]:[/bold green]")
        log.write(Markdown(text))

    def append_system_info(self, info: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[bold yellow]⚡ [Hệ thống]:[/bold yellow] {info}")
