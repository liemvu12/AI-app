"""
Tiện ích sao chép vào Clipboard trên Windows bằng Windows Native API (ctypes)
Không cần cài đặt thêm thư viện ngoài, tốc độ tức thì (<1ms).
"""
import ctypes


def copy_to_clipboard(text: str) -> bool:
    """
    Sao chép chuỗi văn bản vào Windows Clipboard.
    """
    if not text:
        return False

    try:
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32

        # Khai báo kiểu trả về và tham số chuẩn cho Windows 64-bit
        kernel32.GlobalAlloc.restype = ctypes.c_void_p
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]

        # Mã hóa chuỗi UTF-16LE cho CF_UNICODETEXT (13)
        encoded = text.encode("utf-16le") + b"\x00\x00"
        
        # GMEM_MOVEABLE = 0x0002
        h_mem = kernel32.GlobalAlloc(0x0002, len(encoded))
        if not h_mem:
            return False

        ptr = kernel32.GlobalLock(h_mem)
        if not ptr:
            return False

        ctypes.memmove(ptr, encoded, len(encoded))
        kernel32.GlobalUnlock(h_mem)

        if not user32.OpenClipboard(0):
            return False

        user32.EmptyClipboard()
        user32.SetClipboardData(13, h_mem)  # 13 = CF_UNICODETEXT
        user32.CloseClipboard()
        return True
    except Exception:
        # Fallback an toàn qua PowerShell nếu gặp lỗi
        try:
            import subprocess
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Set-Clipboard", "-Value", text],
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True
        except Exception:
            return False
