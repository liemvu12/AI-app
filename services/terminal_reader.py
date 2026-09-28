"""
Trình quản lý Console Screen Reader (Client Runner)
Khởi chạy console_daemon.py như một tiến trình ngầm độc lập để đọc màn hình AGY
mà không can thiệp vào Console Handle của Textual UI.
Tự động giám sát (supervisor) và phục hồi tự động (auto-restart) nếu tiến trình ngầm bị gián đoạn.
"""
import subprocess
import sys
import os
import time
import threading
from typing import Callable

DAEMON_SCRIPT = os.path.join(os.path.dirname(__file__), "console_daemon.py")


class TerminalScreenReader:
    def __init__(
        self,
        on_text_change: Callable[[str], None],
        on_submit: Callable[[str], None] | None = None,
        on_idle: Callable[[], None] | None = None
    ):
        self.on_text_change = on_text_change
        self.on_submit = on_submit
        self.on_idle = on_idle
        self._proc: subprocess.Popen | None = None
        self._running = False
        self._supervisor_thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._supervisor_thread = threading.Thread(target=self._supervise_daemon, daemon=True)
        self._supervisor_thread.start()

    def stop(self) -> None:
        self._running = False
        if self._proc:
            try:
                import psutil
                p = psutil.Process(self._proc.pid)
                for child in p.children(recursive=True):
                    try:
                        child.terminate()
                    except Exception:
                        pass
                p.terminate()
            except Exception:
                pass
            self._proc = None

    def _supervise_daemon(self) -> None:
        """Vòng lặp giám sát: đảm bảo daemon luôn hoạt động liên tục và tự phục hồi khi cần"""
        CREATE_NO_WINDOW = 0x08000000
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"

        while self._running:
            try:
                if getattr(sys, "frozen", False):
                    daemon_cmd = [sys.executable, "--daemon"]
                else:
                    daemon_cmd = [sys.executable, "-u", DAEMON_SCRIPT]

                self._proc = subprocess.Popen(
                    daemon_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env=env,
                    creationflags=CREATE_NO_WINDOW
                )

                self._read_stdout()
            except Exception:
                pass

            if self._running:
                time.sleep(1.0)

    def _read_stdout(self) -> None:
        while self._running and self._proc and self._proc.stdout:
            try:
                line = self._proc.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue

                if line.startswith("CHANGE:"):
                    text = line[7:].strip()
                    self.on_text_change(text)
                elif line.startswith("IDLE:"):
                    if self.on_idle:
                        self.on_idle()
                    else:
                        self.on_text_change("")
                elif line.startswith("SUBMIT:"):
                    text = line[7:].strip()
                    if self.on_submit:
                        self.on_submit(text)
            except Exception:
                break
