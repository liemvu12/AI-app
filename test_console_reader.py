"""
Test reading console buffer from running process
"""
import ctypes
from ctypes import wintypes
import sys
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

def read_line_from_pid(pid):
    kernel32.FreeConsole()
    ok = kernel32.AttachConsole(pid)
    print(f"AttachConsole({pid}) -> {ok}")
    if not ok:
        err = kernel32.GetLastError()
        print(f"  Error code: {err}")
        return None

    # Get stdout handle of attached console
    h_out = kernel32.GetStdHandle(-11) # STD_OUTPUT_HANDLE = -11
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    if not kernel32.GetConsoleScreenBufferInfo(h_out, ctypes.byref(csbi)):
        print("  GetConsoleScreenBufferInfo failed:", kernel32.GetLastError())
        kernel32.FreeConsole()
        return None

    print(f"  Buffer size: {csbi.dwSize.X}x{csbi.dwSize.Y}, Cursor: ({csbi.dwCursorPosition.X}, {csbi.dwCursorPosition.Y})")
    
    # Read the current line where cursor is
    cursor_y = csbi.dwCursorPosition.Y
    width = csbi.dwSize.X
    buf = ctypes.create_unicode_buffer(width)
    read_chars = wintypes.DWORD()
    coord = COORD(0, cursor_y)
    
    if kernel32.ReadConsoleOutputCharacterW(h_out, buf, width, coord, ctypes.byref(read_chars)):
        line_text = buf.value.rstrip()
        print(f"  Current line text: '{line_text}'")
        kernel32.FreeConsole()
        return line_text

    kernel32.FreeConsole()
    return None

if __name__ == "__main__":
    import subprocess
    # Find agy pid
    out = subprocess.check_output(["powershell", "-Command", "(Get-Process -Name 'agy' -ErrorAction SilentlyContinue).Id"]).decode().strip()
    pids = [int(p) for p in out.split() if p.isdigit()]
    print("Found AGY PIDs:", pids)
    for p in pids:
        read_line_from_pid(p)
