"""
Entry point cho ứng dụng AGY Terminal Bridge
"""
import sys
import os

# Đảm bảo UTF-8 trên Windows console
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from ui import AGYTerminalBridgeApp


def main():
    app = AGYTerminalBridgeApp()
    app.run()


if __name__ == "__main__":
    main()
