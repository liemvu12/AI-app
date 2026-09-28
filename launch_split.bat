@echo off
chcp 65001 >nul
title AGY Workspace Launcher (Split Terminal)

set "WORKSPACE_DIR=C:\Document\05.VsCodeAI"
set "BRIDGE_DIR=C:\Document\05.VsCodeAI\agy_terminal_bridge"
set "PYTHON_EXE=C:\Document\05.VsCodeAI\.venv\Scripts\python.exe"
set "STANDALONE_EXE=C:\Document\05.VsCodeAI\AGYCompanion.exe"

if exist "%PYTHON_EXE%" (
    set "COMPANION_CMD=\"%PYTHON_EXE%\" companion.py --tui"
) else if exist "%STANDALONE_EXE%" (
    set "COMPANION_CMD=\"%STANDALONE_EXE%\" --tui"
) else (
    set "COMPANION_CMD=\"%BRIDGE_DIR%\dist\AGYCompanion.exe\" --tui"
)

echo Dang khoi chay Windows Terminal voi 2 man hinh song song:
echo [Khung trai 67%%]: Terminal AGY nguyen ban (Full 100%% tinh nang, slash commands, interactive)
echo [Khung phai 33%%]: AGY Dev English Companion (Toi uu hoa tieng Anh va tra tu nhanh)

wt -d "%WORKSPACE_DIR%" powershell -NoExit -Command "agy" `; split-pane -V -s 0.33 -d "%BRIDGE_DIR%" powershell -NoExit -Command "%COMPANION_CMD%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [Luu y] Neu Windows Terminal khong ho tro hoac bao loi, mo 2 cua so doc lap:
    start "AGY Terminal" /D "%WORKSPACE_DIR%" powershell -NoExit -Command "agy"
    start "AGY Companion" /D "%BRIDGE_DIR%" %COMPANION_CMD%
)
