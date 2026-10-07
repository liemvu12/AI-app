@echo off
chcp 65001 >nul
title AGY Workspace Launcher (Split Terminal)

set "BRIDGE_DIR=%~dp0"
if "%BRIDGE_DIR:~-1%"=="\" set "BRIDGE_DIR=%BRIDGE_DIR:~0,-1%"
set "WORKSPACE_DIR=%BRIDGE_DIR%"

call "%BRIDGE_DIR%\setup_env.bat"
if not defined PYTHON_EXE (
    echo [Loi] Khong the thiet lap moi truong Python!
    pause
    exit /b 1
)

set "COMPANION_CMD=& \"%PYTHON_EXE%\" \"%BRIDGE_DIR%\companion.py\" --tui"

echo Dang khoi chay Windows Terminal voi 2 man hinh song song:
echo [Khung trai 67%%]: Terminal AGY nguyen ban (Full 100%% tinh nang, slash commands, interactive)
echo [Khung phai 33%%]: AGY Dev English Companion (Toi uu hoa tieng Anh va tra tu nhanh)

wt -d "%WORKSPACE_DIR%" powershell -NoExit -Command "agy" `; split-pane -V -s 0.33 -d "%BRIDGE_DIR%" powershell -NoExit -Command "%COMPANION_CMD%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [Luu y] Neu Windows Terminal khong ho tro hoac bao loi, mo 2 cua so doc lap:
    start "AGY Terminal" /D "%WORKSPACE_DIR%" powershell -NoExit -Command "agy"
    start "AGY Companion" /D "%BRIDGE_DIR%" powershell -NoExit -Command "%COMPANION_CMD%"
)
