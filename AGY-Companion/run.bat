@echo off
chcp 65001 >nul
title AGY Companion Launcher

cd /d "%~dp0"
call "%~dp0setup_env.bat"
if not defined PYTHON_EXE (
    echo [Lỗi] Không thể thiết lập môi trường Python!
    pause
    exit /b 1
)

echo ========================================================
echo      AGY DEV ENGLISH COMPANION & TERMINAL BRIDGE
echo ========================================================
echo   [1] Khoi chay Windows Terminal Split-Pane (Khuyen dung)
echo   [2] Khoi chay Companion App doc lap (companion.py)
echo   [3] Khoi chay Inline Terminal Stream (main.py)
echo ========================================================
echo.

choice /C 123 /T 5 /D 1 /M "Chon che do khoi chay (Tu dong chon [1] sau 5 giay)"
if errorlevel 3 goto inline
if errorlevel 2 goto companion
if errorlevel 1 goto split

:split
call "%~dp0launch_split.bat"
goto end

:companion
call "%~dp0run_companion.bat"
goto end

:inline
"%PYTHON_EXE%" main.py
goto end

:end
