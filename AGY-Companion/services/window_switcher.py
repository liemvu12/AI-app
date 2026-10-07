"""
Dịch vụ chuyển đổi ngữ cảnh nhanh giữa các ứng dụng (Fast App Context Switcher)
Hỗ trợ:
1. Chuyển đổi giữa AGY Terminal và Companion App qua phím tắt toàn cục (Global Hotkey: Alt+A, F9).
2. Chuyển đổi giữa 2 khung chia đôi màn hình trong Windows Terminal Split-Pane (Alt+Left, Alt+Right).
3. Tương thích cả chế độ cửa sổ độc lập (Win32 BringWindowToTop/SetForegroundWindow).
"""
import sys
import os
import time
import threading
import ctypes
from ctypes import wintypes
import psutil
from pynput.keyboard import Controller, Key, GlobalHotKeys

user32 = ctypes.windll.user32 if sys.platform == "win32" else None
kernel32 = ctypes.windll.kernel32 if sys.platform == "win32" else None
keyboard_controller = Controller()


class WindowSwitcher:
    def __init__(
        self,
        companion_hwnd: int | None = None,
        on_companion_focused=None,
        on_auto_replace=None,
        on_trigger_ai_check=None
    ):
        self.companion_hwnd = companion_hwnd or (kernel32.GetConsoleWindow() if kernel32 else None)
        self.on_companion_focused = on_companion_focused
        self.on_auto_replace = on_auto_replace
        self.on_trigger_ai_check = on_trigger_ai_check
        self.hotkey_listener: GlobalHotKeys | None = None
        self._last_switch_time = 0.0
        self._current_target_is_agy = False

    def find_agy_pids_and_hwnds(self) -> list[int]:
        """
        Tìm HWND của tiến trình AGY Terminal hoặc PowerShell / Windows Terminal chứa AGY.
        """
        if not user32:
            return []

        agy_pids = set()
        wt_pids = set()
        ps_pids = set()

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                name = (proc.info["name"] or "").lower()
                pid = proc.info["pid"]
                if "agy" in name:
                    agy_pids.add(pid)
                elif "windowsterminal" in name:
                    wt_pids.add(pid)
                elif name in ("powershell.exe", "pwsh.exe", "cmd.exe"):
                    ps_pids.add(pid)
            except Exception:
                pass

        target_pids = agy_pids or ps_pids or wt_pids
        target_hwnds = []

        def enum_cb(hwnd, _):
            if user32.IsWindowVisible(hwnd):
                w_pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(w_pid))
                if w_pid.value in target_pids and hwnd != self.companion_hwnd:
                    target_hwnds.append(hwnd)
            return True

        if target_pids:
            WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

        return target_hwnds

    def focus_hwnd(self, hwnd: int) -> bool:
        """
        Đưa cửa sổ chỉ định lên trên cùng và kích hoạt focus (Bypass Windows foreground lock).
        """
        if not user32 or not hwnd or not user32.IsWindow(hwnd):
            return False

        try:
            # Khôi phục nếu đang bị Minimize
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE

            fg_hwnd = user32.GetForegroundWindow()
            fg_thread = user32.GetWindowThreadProcessId(fg_hwnd, None)
            app_thread = kernel32.GetCurrentThreadId()

            if fg_thread != app_thread:
                user32.AttachThreadInput(fg_thread, app_thread, True)
                user32.BringWindowToTop(hwnd)
                user32.SetForegroundWindow(hwnd)
                user32.AttachThreadInput(fg_thread, app_thread, False)
            else:
                user32.BringWindowToTop(hwnd)
                user32.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False

    def is_in_windows_terminal(self) -> bool:
        """
        Kiểm tra xem cửa sổ hiện tại có phải là Windows Terminal hay không.
        """
        if not user32:
            return False
        try:
            fg = user32.GetForegroundWindow()
            if not fg:
                return False
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(fg, ctypes.byref(pid))
            proc = psutil.Process(pid.value)
            return "terminal" in proc.name().lower()
        except Exception:
            return False

    def switch_to_agy(self) -> bool:
        """
        Chuyển ngữ cảnh sang AGY Terminal:
        - Nếu trong Windows Terminal Split-Pane: Gửi phím Alt + Left để sang khung AGY bên trái.
        - Nếu là cửa sổ độc lập: Đưa cửa sổ AGY lên trước mặt.
        """
        self._current_target_is_agy = False
        now = time.time()
        if now - self._last_switch_time < 0.15:
            return True
        self._last_switch_time = now

        # 1. Thử gửi Alt+Left trước (hỗ trợ Windows Terminal Split-Pane)
        try:
            keyboard_controller.press(Key.alt)
            keyboard_controller.press(Key.left)
            keyboard_controller.release(Key.left)
            keyboard_controller.release(Key.alt)
        except Exception:
            pass

        # 2. Đồng thời tìm HWND của AGY để focus nếu đang ở cửa sổ riêng
        hwnds = self.find_agy_pids_and_hwnds()
        if hwnds:
            return self.focus_hwnd(hwnds[0])
        return True

    def switch_to_companion(self) -> bool:
        """
        Chuyển ngữ cảnh sang Companion App:
        - Nếu trong Windows Terminal Split-Pane: Gửi phím Alt + Right để sang khung Companion bên phải.
        - Nếu là cửa sổ độc lập: Đưa cửa sổ Companion lên trước mặt.
        - Tự động gọi callback đặt con trỏ vào ô nhập dữ liệu.
        """
        self._current_target_is_agy = True
        now = time.time()
        if now - self._last_switch_time < 0.15:
            return True
        self._last_switch_time = now

        # 1. Thử gửi Alt+Right (hỗ trợ Windows Terminal Split-Pane)
        try:
            keyboard_controller.press(Key.alt)
            keyboard_controller.press(Key.right)
            keyboard_controller.release(Key.right)
            keyboard_controller.release(Key.alt)
        except Exception:
            pass

        # 2. Focus cửa sổ Companion
        if self.companion_hwnd:
            self.focus_hwnd(self.companion_hwnd)

        # 3. Kích hoạt đặt con trỏ vào ô nhập dữ liệu
        if self.on_companion_focused:
            try:
                self.on_companion_focused()
            except Exception:
                pass
        return True

    def toggle_context(self) -> None:
        """
        Đảo ngữ cảnh qua lại giữa AGY Terminal và Companion App.
        """
        if not user32:
            self.switch_to_agy()
            return

        if self.is_in_windows_terminal():
            if self._current_target_is_agy:
                self.switch_to_agy()
            else:
                self.switch_to_companion()
            return

        fg = user32.GetForegroundWindow()
        if fg == self.companion_hwnd:
            self.switch_to_agy()
        else:
            self.switch_to_companion()

    def auto_replace_and_send_to_agy(self, old_prompt: str, new_prompt: str) -> None:
        """
        Quy trình tự động thay thế và gửi prompt sang AGY:
        1. Chuyển sang AGY Terminal.
        2. Xóa sạch prompt cũ trong AGY Terminal.
        3. Dán prompt mới (Ctrl+V).
        4. Nhấn Enter gửi đi.
        """
        def _task():
            # 1. Chuyển tiêu điểm sang AGY Terminal
            self.switch_to_agy()
            time.sleep(0.08)

            # 2. Xóa prompt cũ
            keyboard_controller.press(Key.end)
            keyboard_controller.release(Key.end)
            time.sleep(0.02)

            del_count = max(len(old_prompt) + 20, 50)
            for _ in range(del_count):
                keyboard_controller.press(Key.backspace)
                keyboard_controller.release(Key.backspace)
            time.sleep(0.04)

            # 3. Dán prompt mới (Ctrl + V)
            keyboard_controller.press(Key.ctrl)
            keyboard_controller.press('v')
            keyboard_controller.release('v')
            keyboard_controller.release(Key.ctrl)
            time.sleep(0.05)

            # 4. Gửi Enter
            keyboard_controller.press(Key.enter)
            keyboard_controller.release(Key.enter)

        threading.Thread(target=_task, daemon=True).start()

    def start_global_hotkeys(self) -> None:
        """
        Khởi động bộ lắng nghe phím tắt toàn cục:
        - Alt+A, F9, Ctrl+Alt+A: Đổi ngữ cảnh giữa AGY và Companion.
        - Alt+R, Ctrl+Alt+R: Tự động thay thế prompt cũ bằng prompt mới và Enter sang AGY.
        - Ctrl+Space: Gửi nội dung sang AI để xử lý.
        """
        if self.hotkey_listener:
            return

        hotkeys = {
            '<alt>+a': self.toggle_context,
            '<f9>': self.toggle_context,
            '<ctrl>+<alt>+a': self.toggle_context,
        }

        if self.on_auto_replace:
            hotkeys['<alt>+r'] = self.on_auto_replace
            hotkeys['<ctrl>+<alt>+r'] = self.on_auto_replace
            
        if self.on_trigger_ai_check:
            hotkeys['<ctrl>+<space>'] = self.on_trigger_ai_check

        try:
            self.hotkey_listener = GlobalHotKeys(hotkeys)
            self.hotkey_listener.daemon = True
            self.hotkey_listener.start()
        except Exception:
            pass

    def stop_global_hotkeys(self) -> None:
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
            self.hotkey_listener = None
