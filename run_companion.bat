@echo off
chcp 65001 >nul
title AGY English Companion

echo Dang khoi dong AGY English Companion...
cd /d "%~dp0"

set "PYTHON_EXE=C:\Document\05.VsCodeAI\.venv\Scripts\python.exe"

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" companion.py
) else (
    python companion.py
)

pause
