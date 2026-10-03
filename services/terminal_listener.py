"""
Module lắng nghe bàn phím thời gian thực trên Terminal (Real-time Terminal Keystroke Listener)
Bắt các ký tự người dùng đang gõ trong Terminal (PowerShell, Windows Terminal, CMD, AGY)
và cập nhật ngay lập tức sang Companion trước khi người dùng nhấn Enter.
"""
import ctypes
import os
import threading
from typing import Callable
from pynput import keyboard

# Danh sách các tiến trình terminal được theo dõi
TERMINAL_PROCESSES = {
    "windowsterminal.exe",
    "powershell.exe",
    "pwsh.exe",
    "cmd.exe",
    "agy.exe",
    "conhost.exe",
    "code.exe",
    "bash.exe",
    "mintty.exe"
}


def get_foreground_process_name() -> str:
    """
    Lấy tên file thực thi (.exe) của cửa sổ đang có tiêu điểm (Focus).
    """
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""

        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return ""

        # PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        h_proc = kernel32.OpenProcess(0x1000, False, pid)
        if not h_proc:
            return ""

        buf = ctypes.create_unicode_buffer(512)
        size = ctypes.c_ulong(512)
        kernel32.QueryFullProcessImageNameW(h_proc, 0, buf, ctypes.byref(size))
        kernel32.CloseHandle(h_proc)

        path = buf.value.lower()
        return os.path.basename(path)
    except Exception:
        return ""


class TerminalKeystrokeListener:
    def __init__(
        self,
        on_text_change: Callable[[str], None],
        on_enter_submit: Callable[[str], None] | None = None
    ):
        self.on_text_change = on_text_change
        self.on_enter_submit = on_enter_submit
        self.buffer = ""
        self._listener: keyboard.Listener | None = None
        self._running = False
        self._lock = threading.Lock()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        self._running = False
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass

    def _is_terminal_focused(self) -> bool:
        proc_name = get_foreground_process_name()
        if not proc_name:
            # Nếu không lấy được tên process thì cho phép bắt (đảm bảo không bị miss)
            return True
        return proc_name in TERMINAL_PROCESSES

    def _on_press(self, key) -> None:
        if not self._running:
            return

        # Chỉ bắt phím khi người dùng đang thao tác trong cửa sổ Terminal
        if not self._is_terminal_focused():
            return

        with self._lock:
            # 1. Phím Enter: Đã gửi lệnh
            if key == keyboard.Key.enter:
                submitted_text = self.buffer.strip()
                self.buffer = ""
                if submitted_text and self.on_enter_submit:
                    self.on_enter_submit(submitted_text)
                return

            # 2. Phím Backspace: Xóa ký tự cuối
            if key == keyboard.Key.backspace:
                if self.buffer:
                    self.buffer = self.buffer[:-1]
                    self.on_text_change(self.buffer)
                return

            # 3. Phím Esc hoặc Ctrl+C: Hủy dòng lệnh hiện tại
            if key == keyboard.Key.esc:
                self.buffer = ""
                self.on_text_change("")
                return

            # 4. Phím Space
            if key == keyboard.Key.space:
                self.buffer += " "
                self.on_text_change(self.buffer)
                return

            # 5. Ký tự chữ / số / ký hiệu
            try:
                if hasattr(key, "char") and key.char:
                    # Bỏ qua các ký tự điều khiển (ví dụ Ctrl+C, Ctrl+V)
                    if ord(key.char) >= 32 or key.char in "\t":
                        self.buffer += key.char
                        self.on_text_change(self.buffer)
            except Exception:
                pass
