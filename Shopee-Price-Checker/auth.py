"""
auth.py
Quản lý phiên đăng nhập Shopee bằng mã QR:
1. Mở trực tiếp trình duyệt Edge (hoặc Chrome) có giao diện toàn màn hình hiển thị mã QR Shopee.
2. Lắng nghe trực tiếp trạng thái quét QR từ Shopee (NEW -> SCANNED -> CONFIRMED).
3. Tự động lưu phiên vào session_state.json và đóng trình duyệt khi thành công.
"""

import sys
import os
import json
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent
SESSION_FILE = BASE_DIR / "session_state.json"
SHOPEE_LOGIN_URL = "https://shopee.vn/buyer/login"


def _log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _real_login_cookie(cookies) -> bool:
    """Cookie SPC_EC/SPC_ST của khách có thể là '-' hoặc rỗng => chỉ tính khi có giá trị thật."""
    for c in cookies:
        if c.get("name") in ("SPC_EC", "SPC_ST"):
            v = (c.get("value") or "").strip().strip('"')
            if len(v) > 5 and v != "-":
                return True
    return False


def is_session_valid(session_path: Path = SESSION_FILE) -> bool:
    """Kiểm tra file session có tồn tại và chứa cookie đăng nhập thật không."""
    if not session_path.exists():
        return False
    try:
        with open(session_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return _real_login_cookie(data.get("cookies", []))
    except Exception as e:
        print(f"[!] Lỗi khi đọc session: {e}")
        return False


def _print_qr_terminal(data: str):
    """Vẽ mã QR ngay trong terminal để người dùng có thể quét trực tiếp từ terminal nếu muốn."""
    try:
        import qrcode
    except ImportError:
        return
    os.system("")  # Bật ANSI escape trên Windows console
    qr = qrcode.QRCode(border=2, error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(data)
    qr.make()
    m = qr.get_matrix()
    if len(m) % 2:
        m.append([False] * len(m[0]))
    lines = []
    for r in range(0, len(m), 2):
        row = ""
        for c in range(len(m[r])):
            top, bot = m[r][c], m[r + 1][c]
            fg = "30" if top else "97"
            bg = "40" if bot else "107"
            row += f"\x1b[{fg};{bg}m\u2580"
        lines.append(row + "\x1b[0m")
    print("\n".join(lines), flush=True)


def login_with_qr(session_path: Path = SESSION_FILE, timeout_sec: int = 180):
    from playwright.sync_api import sync_playwright

    print("=" * 65)
    print("🚀 ĐĂNG NHẬP SHOPEE QUA MÃ QR")
    print("=" * 65)
    print("👉 Trình duyệt Edge sẽ tự động mở trang Shopee với mã QR.")
    print("👉 Hãy mở app Shopee trên điện thoại quét mã và nhấn 'Xác nhận'.")
    print("=" * 65)

    with sync_playwright() as p:
        _log("1/4 Khởi chạy trình duyệt Edge...")
        browser = None
        for channel in ("msedge", "chrome", None):
            name = channel or "Chromium"
            try:
                browser = p.chromium.launch(
                    channel=channel,
                    headless=False,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--start-maximized"
                    ]
                )
                _log(f"    ✓ Đang sử dụng: {name} (phiên bản {browser.version})")
                break
            except Exception as e:
                _log(f"    (bỏ qua {name}: {str(e).splitlines()[0]})")

        if browser is None:
            _log("❌ Không mở được trình duyệt nào trên máy.")
            return False

        # no_viewport=True để cửa sổ mở đúng tỷ lệ toàn màn hình thật trên máy người dùng
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Lắng nghe trạng thái quét QR từ API của Shopee
        qr_scanned = False
        qr_confirmed = False
        last_qr_url = None

        def handle_response(response):
            nonlocal qr_scanned, qr_confirmed, last_qr_url
            url = response.url
            if "authentication/gen_qrcode" in url and response.status == 200:
                try:
                    data = response.json().get("data", {})
                    qid = data.get("qrcode_id")
                    if qid:
                        last_qr_url = f"https://shopee.vn/universal-link/qrcode-login?id={qid}"
                except Exception:
                    pass
            elif "authentication/qrcode_status" in url and response.status == 200:
                try:
                    status = response.json().get("data", {}).get("status")
                    if status == "SCANNED" and not qr_scanned:
                        qr_scanned = True
                        _log("📱 [ĐÃ QUÉT THÀNH CÔNG] Hãy bấm 'Xác nhận đăng nhập' trên điện thoại!")
                    elif status == "CONFIRMED":
                        qr_confirmed = True
                        _log("🎉 [ĐÃ BẤM XÁC NHẬN] Đang hoàn tất lưu phiên...")
                except Exception:
                    pass

        page.on("response", handle_response)

        try:
            from playwright_stealth import Stealth
            Stealth().apply_stealth_sync(page)
        except Exception:
            pass

        _log(f"2/4 Mở trang đăng nhập Shopee...")
        try:
            page.goto(SHOPEE_LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            _log(f"    (goto: {e})")

        _log("3/4 Tự động kích hoạt hiển thị mã QR trên màn hình...")
        for attempt in range(1, 6):
            if page.locator("a[href*='login/qr']").count() > 0:
                try:
                    page.locator("a[href*='login/qr']").first.click()
                    _log("    ✓ Đã chuyển sang chế độ quét mã QR!")
                    break
                except Exception:
                    pass
            elif page.get_by_text("Scan QR code with Shopee App").count() > 0 or page.get_by_text("Quét mã QR bằng ứng dụng Shopee").count() > 0:
                _log("    ✓ Khung mã QR đã sẵn sàng trên màn hình!")
                break
            time.sleep(1.5)

        # Đưa cửa sổ lên phía trước
        try:
            page.bring_to_front()
        except Exception:
            pass

        time.sleep(2)
        if last_qr_url:
            print("\n👇 BẠN CŨNG CÓ THỂ QUÉT TRỰC TIẾP MÃ QR NÀY TRONG TERMINAL:\n", flush=True)
            _print_qr_terminal(last_qr_url)

        _log("4/4 Đang chờ bạn quét mã QR và xác nhận trên điện thoại...")
        start_time = time.time()
        logged_in = False

        while time.time() - start_time < timeout_sec:
            # Điều kiện thành công: Shopee báo CONFIRMED hoặc có cookie SPC_EC thật và URL thoát khỏi login
            if qr_confirmed or (_real_login_cookie(context.cookies()) and "login" not in page.url):
                _log("✅ ĐĂNG NHẬP THÀNH CÔNG!")
                logged_in = True
                time.sleep(3)
                break
            time.sleep(1.5)

        if logged_in:
            context.storage_state(path=str(session_path))
            _log(f"[+] Đã lưu phiên làm việc an toàn vào: {session_path.name}")
            _log("[+] Bạn có thể đóng trình duyệt hoặc hệ thống sẽ tự động đóng sau 2 giây.")
            time.sleep(2)
            browser.close()
            return True
        else:
            _log("❌ Hết thời gian chờ đăng nhập (Timeout). Vui lòng thử lại.")
            browser.close()
            return False


def ensure_session(session_path: Path = SESSION_FILE) -> bool:
    """Đảm bảo hệ thống đã có session hợp lệ. Nếu chưa có, kích hoạt đăng nhập QR."""
    if is_session_valid(session_path):
        print(f"[✓] Đã tìm thấy phiên đăng nhập hợp lệ ({session_path.name}).")
        return True
    print("[!] Chưa có phiên đăng nhập hoặc phiên đã hết hạn.")
    return login_with_qr(session_path)


if __name__ == "__main__":
    if "--check" in sys.argv:
        if is_session_valid():
            print("VALID")
            sys.exit(0)
        print("INVALID")
        sys.exit(1)

    if not ensure_session():
        sys.exit(1)
