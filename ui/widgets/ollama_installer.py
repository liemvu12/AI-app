from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Button, ProgressBar
from textual.worker import Worker
from services.ollama_client import install_ollama_silently, pull_model_with_progress

class OllamaInstallerModal(ModalScreen[bool]):
    CSS = """
    OllamaInstallerModal {
        align: center middle;
    }
    
    #installer-dialog {
        width: 60;
        height: auto;
        padding: 2;
        background: #161b22;
        border: solid #30363d;
    }
    
    #installer-title {
        text-style: bold;
        color: #58a6ff;
        margin-bottom: 1;
    }
    
    #installer-buttons {
        layout: horizontal;
        align: right middle;
        margin-top: 2;
    }
    
    Button {
        margin-left: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Vertical(id="installer-dialog"):
            yield Label("🚀 Kích hoạt tính năng AI Pro Max (Ollama)", id="installer-title")
            yield Label("Ứng dụng phát hiện máy bạn chưa cài đặt Ollama. Đây là tính năng giúp sửa lỗi tiếng Anh siêu thông minh và bảo mật 100% bằng cách chạy AI cục bộ.\n\nBạn có muốn tự động tải và cài đặt Ollama (kèm model qwen2.5:1.5b) không?", id="installer-desc")
            
            yield Label("", id="status-label")
            yield ProgressBar(total=100, show_eta=False, id="progress-bar")
            
            with Horizontal(id="installer-buttons"):
                yield Button("Bỏ qua", variant="default", id="btn-cancel")
                yield Button("Cài đặt ngay", variant="primary", id="btn-install")

    def on_mount(self) -> None:
        self.query_one("#progress-bar").display = False
        self.query_one("#status-label").display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(False)
        elif event.button.id == "btn-install":
            self.start_installation()

    def start_installation(self) -> None:
        self.query_one("#btn-cancel").disabled = True
        self.query_one("#btn-install").disabled = True
        self.query_one("#installer-desc").display = False
        self.query_one("#progress-bar").display = True
        self.query_one("#status-label").display = True
        
        self.run_worker(self._install_worker, exclusive=True, thread=True)

    def _install_worker(self) -> None:
        status_label = self.query_one("#status-label", Label)
        progress_bar = self.query_one("#progress-bar", ProgressBar)

        def set_status(msg):
            self.app.call_from_thread(status_label.update, msg)

        def set_progress(downloaded, total):
            if total > 0:
                pct = int((downloaded / total) * 100)
                self.app.call_from_thread(progress_bar.update, progress=pct)

        success = install_ollama_silently(set_progress, set_status)
        if not success:
            set_status("[red]Cài đặt thất bại. Vui lòng cài thủ công tại ollama.com[/red]")
            self.app.call_from_thread(lambda: self.query_one("#btn-cancel").update("Đóng"))
            self.app.call_from_thread(lambda: setattr(self.query_one("#btn-cancel"), "disabled", False))
            return

        set_status("Cài đặt thành công! Đang tải model qwen2.5:1.5b (khoảng 1GB)...")
        self.app.call_from_thread(progress_bar.update, progress=0)
        
        def pull_progress(completed, total, status_msg):
            if total > 0:
                pct = int((completed / total) * 100)
                self.app.call_from_thread(progress_bar.update, progress=pct)
            self.app.call_from_thread(status_label.update, f"Đang tải model: {status_msg}")

        pull_success = pull_model_with_progress("qwen2.5:1.5b", pull_progress)
        
        if pull_success:
            set_status("[green]Hoàn tất! AI Pro Max đã sẵn sàng.[/green]")
        else:
            set_status("[yellow]Tải model lỗi hoặc chưa tải xong. Bạn có thể tự tải sau.[/yellow]")

        import time
        time.sleep(2)
        self.app.call_from_thread(self.dismiss, True)
