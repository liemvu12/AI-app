"""
Daemon đọc màn hình console terminal của AGY (Console Screen Reader Daemon)
Chạy trong tiến trình ngầm độc lập, đính kèm vào console của AGY và xuất chuỗi văn bản
chuẩn Unicode qua stdout theo thời gian thực mà không làm ảnh hưởng đến Textual UI.

Nguyên tắc cốt lõi:
1. GẮN KẾT BỀN VỮNG (Connection Locking): Khi đã đính kèm vào agy.exe, TUYỆT ĐỐI KHÔNG
   ngắt kết nối hoặc quét PID mới chừng nào tiến trình agy.exe đó vẫn còn sống.
2. LOẠI TRỪ 100% TIẾN TRÌNH RÁC: Tuyệt đối không bắt nhầm các tiến trình powershell.exe
   chạy ngầm tức thời (-Command) do hệ thống hoặc công cụ sinh ra.
3. ĐỌC CHÍNH XÁC VÙNG PROMPT: Quét xung quanh vị trí con trỏ cursor_y, nhận diện prompt '>',
   hỗ trợ nhiều dòng (multi-line) và lọc bỏ hoàn toàn các đường kẻ phân cách viền.
"""
import ctypes
from ctypes import wintypes
import sys
import time
import os
import tempfile
import psutil

if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

kernel32 = ctypes.windll.kernel32 if sys.platform == "win32" else None

LOG_FILE = os.path.join(tempfile.gettempdir(), "agy_console_daemon.log")


def _log(msg: str) -> None:
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            t = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{t}] {msg}\n")
    except Exception:
        pass


class COORD(ctypes.Structure):
    _fields_ = [("X", wintypes.SHORT), ("Y", wintypes.SHORT)]


class SMALL_RECT(ctypes.Structure):
    _fields_ = [
        ("Left", wintypes.SHORT),
        ("Top", wintypes.SHORT),
        ("Right", wintypes.SHORT),
        ("Bottom", wintypes.SHORT),
    ]


class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", wintypes.WORD),
        ("srWindow", SMALL_RECT),
        ("dwMaximumWindowSize", COORD),
    ]


def get_own_process_family() -> set[int]:
    """Thu thập PID của tiến trình hiện tại và các tiến trình cha/ông nội"""
    family = set()
    try:
        cur = psutil.Process(os.getpid())
        family.add(cur.pid)
        for child in cur.children(recursive=True):
            family.add(child.pid)
        parent = cur.parent()
        if parent:
            family.add(parent.pid)
            gp = parent.parent()
            if gp:
                family.add(gp.pid)
    except Exception:
        pass
    return family


def is_process_alive(pid: int | None) -> bool:
    """Kiểm tra tiến trình còn sống và không phải zombie"""
    if not pid:
        return False
    try:
        p = psutil.Process(pid)
        return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
    except Exception:
        return False


def is_agy_process(pid: int | None) -> bool:
    """Kiểm tra xem PID có phải là tiến trình agy.exe hay không"""
    if not pid:
        return False
    try:
        p = psutil.Process(pid)
        name = (p.name() or "").lower()
        return name == "agy.exe"
    except Exception:
        return False


def find_target_pid() -> int | None:
    """
    Tìm PID của Terminal AGY:
    1. Ưu tiên số 1: Tiến trình agy.exe đang chạy (chính xác 100%)
    2. Ưu tiên số 2: PowerShell tương tác mở agy (có cờ -NoExit, KHÔNG lấy lệnh tạm -Command)
    """
    exclude_pids = get_own_process_family()

    agy_procs = []
    ps_interactive_procs = []

    for proc in psutil.process_iter(["pid", "name", "create_time", "cmdline"]):
        try:
            pid = proc.info["pid"]
            if pid in exclude_pids or pid == os.getpid():
                continue

            name = (proc.info["name"] or "").lower()
            cmd_list = proc.info.get("cmdline") or []
            cmd_str = " ".join(cmd_list).lower()

            # Bỏ qua hoàn toàn companion (cả script và exe đóng gói)
            if any(x in cmd_str for x in ["companion.py", "companion.exe", "agycompanion"]):
                continue

            # 1. Tìm agy.exe
            if name == "agy.exe":
                agy_procs.append(proc)
                continue

            # 2. Tìm PowerShell tương tác (chỉ lấy PowerShell có -NoExit hoặc chạy agy, bỏ qua -Command tạm)
            if name in ("powershell.exe", "pwsh.exe"):
                # Bỏ qua các lệnh PowerShell chạy script tạm không có -NoExit
                if "-command" in cmd_str and "-noexit" not in cmd_str:
                    continue
                if "agy" in cmd_str:
                    ps_interactive_procs.append(proc)
                elif "-noexit" in cmd_str:
                    ps_interactive_procs.append(proc)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # 1. Ưu tiên agy.exe mới nhất
    if agy_procs:
        agy_procs.sort(key=lambda p: p.info["create_time"], reverse=True)
        return agy_procs[0].info["pid"]

    # 2. Nếu chưa thấy agy.exe thì lấy PowerShell tương tác mới nhất
    if ps_interactive_procs:
        ps_interactive_procs.sort(key=lambda p: p.info["create_time"], reverse=True)
        return ps_interactive_procs[0].info["pid"]

    return None


def is_border_line(s: str) -> bool:
    """Kiểm tra dòng viền giao diện (box drawing)"""
    s = s.strip()
    return len(s) > 5 and all(c in "─-=_│┌┐└┘├┤┬┴┼" for c in s)


def read_console_prompt(h_conout: int) -> str | None:
    """
    Đọc chính xác nội dung dòng nhập lệnh hiện tại trên màn hình Terminal của AGY.
    Tối ưu hóa:
    - Quét trực tiếp xung quanh vị trí con trỏ cursor_y
    - Nhận diện ký tự prompt: '>', 'agy>', '❯', '›', 'PS '
    - Hỗ trợ prompt dài nhiều dòng (multi-line)
    - Loại bỏ triệt để các đường viền giao diện và thanh trạng thái (esc to cancel)
    """
    if not kernel32:
        return None

    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    if not kernel32.GetConsoleScreenBufferInfo(h_conout, ctypes.byref(csbi)):
        return None

    width = csbi.dwSize.X
    cy = csbi.dwCursorPosition.Y
    top = csbi.srWindow.Top
    bottom = csbi.srWindow.Bottom

    # Đọc các dòng xung quanh vị trí con trỏ (tối đa 15 dòng trên và 10 dòng dưới)
    scan_start = max(top, cy - 15)
    scan_end = min(bottom, cy + 10)

    raw_lines: dict[int, str] = {}
    for y in range(scan_start, scan_end + 1):
        buf = ctypes.create_unicode_buffer(width)
        read_chars = wintypes.DWORD()
        if kernel32.ReadConsoleOutputCharacterW(h_conout, buf, width, COORD(0, y), ctypes.byref(read_chars)):
            raw_lines[y] = buf.value.rstrip()

    if not raw_lines:
        return None

    # 1. Tìm dòng chứa ký tự prompt bắt đầu quét từ cursor_y ngược lên
    marker_y = None
    for y in range(cy, scan_start - 1, -1):
        if y not in raw_lines:
            continue
        s = raw_lines[y].strip()
        if any(s.startswith(p) for p in ["agy>", ">", "❯", "›"]):
            marker_y = y
            break
        if s.startswith("PS ") and ">" in s:
            pos = s.rfind(">")
            return s[pos + 1:].strip()

    # 2. Fallback: nếu con trỏ bị AGY chuyển vị trí tạm thời, quét từ dưới lên
    if marker_y is None:
        for y in range(scan_end, scan_start - 1, -1):
            if y not in raw_lines:
                continue
            s = raw_lines[y].strip()
            if any(s.startswith(p) for p in ["agy>", ">", "❯", "›"]):
                marker_y = y
                break

    if marker_y is None:
        return None

    # Tách chuỗi sau ký tự prompt ở dòng đầu tiên
    line_m = raw_lines[marker_y]
    s_m = line_m.strip()
    prefix_len = 0
    for prefix in ["agy>", ">", "❯", "›"]:
        if s_m.startswith(prefix):
            prefix_len = line_m.find(prefix) + len(prefix)
            break

    first_line = line_m[prefix_len:].strip()
    prompt_lines = [first_line] if first_line else []

    # Thu thập các dòng nối tiếp bên dưới (multi-line)
    for y in range(marker_y + 1, min(scan_end + 1, marker_y + 15)):
        if y not in raw_lines:
            break
        s = raw_lines[y].strip()
        if is_border_line(s) or "esc to cancel" in s.lower() or not s:
            break
        prompt_lines.append(s)

    full_text = " ".join(line for line in prompt_lines if line).strip()
    return full_text


def main():
    _log("Console Daemon starting up (with Connection Locking)...")
    GENERIC_READ = 0x80000000
    GENERIC_WRITE = 0x40000000
    FILE_SHARE_READ = 1
    FILE_SHARE_WRITE = 2
    OPEN_EXISTING = 3

    current_attached_pid = None
    h_conout = None
    last_text = ""

    while True:
        try:
            # QUY TẮC KHÓA KẾT NỐI (CONNECTION LOCKING):
            # Nếu đang kết nối với agy.exe và nó vẫn đang chạy, GIỮ NGUYÊN KẾT NỐI, không quét PID mới!
            if (
                current_attached_pid
                and is_process_alive(current_attached_pid)
                and is_agy_process(current_attached_pid)
                and h_conout
                and h_conout != -1
            ):
                target_pid = current_attached_pid
            else:
                target_pid = find_target_pid()

            if not target_pid:
                time.sleep(0.4)
                continue

            # Nếu PID thay đổi hoặc chưa đính kèm
            if target_pid != current_attached_pid:
                if h_conout and h_conout != -1:
                    kernel32.CloseHandle(h_conout)
                    h_conout = None
                kernel32.FreeConsole()

                if kernel32.AttachConsole(target_pid):
                    current_attached_pid = target_pid
                    conout_name = "CONOUT" + chr(36)
                    h_conout = kernel32.CreateFileW(
                        conout_name,
                        GENERIC_READ | GENERIC_WRITE,
                        FILE_SHARE_READ | FILE_SHARE_WRITE,
                        None,
                        OPEN_EXISTING,
                        0,
                        None
                    )
                    _log(f"Attached to PID: {target_pid} (is_agy={is_agy_process(target_pid)}), handle={h_conout}")
                else:
                    _log(f"AttachConsole failed for PID: {target_pid}, err={kernel32.GetLastError()}")
                    time.sleep(0.4)
                    continue

            if not h_conout or h_conout == -1:
                time.sleep(0.2)
                continue

            # Đọc nội dung dòng lệnh theo thời gian thực
            current_text = read_console_prompt(h_conout)

            if current_text is not None:
                if current_text != last_text:
                    old_text = last_text
                    last_text = current_text

                    if current_text:
                        # Gửi sự kiện đang gõ trực tiếp lên stdout
                        print(f"CHANGE:{current_text}", flush=True)
                    else:
                        # Prompt đã trở về trống
                        print("IDLE:", flush=True)
                        if old_text:
                            print(f"SUBMIT:{old_text}", flush=True)

            time.sleep(0.06)

        except Exception as e:
            _log(f"Daemon loop exception: {e}")
            time.sleep(0.5)


if __name__ == "__main__":
    main()
