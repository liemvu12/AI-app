"""
Test extracting current AGY prompt line
"""
import ctypes
from ctypes import wintypes
import sys
import re
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

kernel32 = ctypes.windll.kernel32

class COORD(ctypes.Structure):
    _fields_ = [("X", wintypes.SHORT), ("Y", wintypes.SHORT)]

class SMALL_RECT(ctypes.Structure):
    _fields_ = [
        ("Left", wintypes.SHORT),
        ("Top", wintypes.SHORT),
        ("Right", wintypes.SHORT),
        ("Bottom", wintypes.SHORT)
    ]

class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", wintypes.WORD),
        ("srWindow", SMALL_RECT),
        ("dwMaximumWindowSize", COORD)
    ]

def get_current_agy_prompt(pid):
    kernel32.FreeConsole()
    if not kernel32.AttachConsole(pid):
        return None

    GENERIC_READ = 0x80000000
    GENERIC_WRITE = 0x40000000
    FILE_SHARE_READ = 1
    FILE_SHARE_WRITE = 2
    OPEN_EXISTING = 3

    h = kernel32.CreateFileW(
        "CONOUT$",
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        0,
        None
    )

    if h == -1 or not h:
        kernel32.FreeConsole()
        return None

    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    if not kernel32.GetConsoleScreenBufferInfo(h, ctypes.byref(csbi)):
        kernel32.CloseHandle(h)
        kernel32.FreeConsole()
        return None

    width = csbi.dwSize.X
    cursor_y = csbi.dwCursorPosition.Y

    # Scan from cursor_y down to cursor_y - 3 to find line starting with '>'
    extracted_prompt = ""
    for y in range(cursor_y, max(-1, cursor_y - 4), -1):
        buf = ctypes.create_unicode_buffer(width)
        read_chars = wintypes.DWORD()
        if kernel32.ReadConsoleOutputCharacterW(h, buf, width, COORD(0, y), ctypes.byref(read_chars)):
            raw_line = buf.value.rstrip()
            if raw_line.startswith(">"):
                # Strip leading '> '
                extracted_prompt = raw_line[1:].strip()
                break

    kernel32.CloseHandle(h)
    kernel32.FreeConsole()
    return extracted_prompt

if __name__ == "__main__":
    import subprocess
    out = subprocess.check_output(["powershell", "-Command", "(Get-Process -Name 'agy' -ErrorAction SilentlyContinue).Id"]).decode().strip()
    pids = [int(p) for p in out.split() if p.isdigit()]
    for p in pids:
        res = get_current_agy_prompt(p)
        print(f"PID {p} prompt: '{res}'")
