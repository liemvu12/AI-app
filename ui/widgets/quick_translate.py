"""
Widget Tra cứu nhanh Google Translate Tối Giản (Minimalist Quick Translate)
Chuyển đổi chiều dịch bằng Ctrl+T. Giao diện đơn giản với đường kẻ tối giản.
"""
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Input
from textual import work
from services.translator import translate_text


class QuickTranslate(Vertical):
    source_lang: str = "vi"
    target_lang: str = "en"

    def compose(self) -> ComposeResult:
        yield Static("─ QUICK TRANSLATE: VI ➔ EN [Ctrl+T] ─", id="quick-translate-title")
        yield Input(placeholder="Tra từ hoặc cụm từ... (Enter)", id="dict-input")
        yield Static("[dim]Kết quả tra cứu nhanh...[/dim]", id="dict-result")

    def toggle_direction(self) -> None:
        """
        Đảo chiều dịch giữa VI -> EN và EN -> VI
        """
        if self.source_lang == "vi":
            self.source_lang = "en"
            self.target_lang = "vi"
        else:
            self.source_lang = "vi"
            self.target_lang = "en"

        title_box = self.query_one("#quick-translate-title", Static)
        title_box.update(f"─ QUICK TRANSLATE: {self.source_lang.upper()} ➔ {self.target_lang.upper()} [Ctrl+T] ─")
        
        # Nếu có nội dung sẵn trong ô tra từ thì dịch lại ngay lập tức
        inp = self.query_one("#dict-input", Input)
        if inp.value.strip():
            self.request_translation(inp.value.strip())

    @work(exclusive=True, thread=True)
    def request_translation(self, text: str) -> None:
        result_box = self.query_one("#dict-result", Static)
        self.app.call_from_thread(result_box.update, "[dim italic]Đang tra cứu...[/dim italic]")
        
        translated = translate_text(text, source_lang=self.source_lang, target_lang=self.target_lang)
        
        display_text = (
            f"[dim]Từ gốc ({self.source_lang.upper()}):[/dim] {text}\n"
            f"[bold green]Kết quả ({self.target_lang.upper()}):[/bold green] [bold underline]{translated}[/bold underline]"
        )
        self.app.call_from_thread(result_box.update, display_text)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "dict-input":
            val = event.value.strip()
            if val:
                self.request_translation(val)
