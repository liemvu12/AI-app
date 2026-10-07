@echo off
chcp 65001 >nul
title AGY English Companion

echo Dang khoi dong AGY English Companion...
cd /d "%~dp0"

call "%~dp0setup_env.bat"
if not defined PYTHON_EXE (
    echo [Loi] Khong the thiet lap moi truong Python!
    pause
    exit /b 1
)

"%PYTHON_EXE%" companion.py --tui

pause
