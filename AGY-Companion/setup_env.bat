@echo off
:: ===================================================================
:: AGY Companion — Auto Environment Setup & Dependency Bootstrapper
:: Tu dong kiem tra va khoi tao moi truong .venv tren may moi / sau khi clone
:: ===================================================================

set "SETUP_DIR=%~dp0"
if "%SETUP_DIR:~-1%"=="\" set "SETUP_DIR=%SETUP_DIR:~0,-1%"

:: 1. Kiem tra xem da co san .venv hop le chua (cuc bo hoac thu muc cha)
set "PYTHON_EXE="

if exist "%SETUP_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SETUP_DIR%\.venv\Scripts\python.exe"
    goto check_packages
)

if exist "%SETUP_DIR%\..\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SETUP_DIR%\..\.venv\Scripts\python.exe"
    goto check_packages
)

if exist "%SETUP_DIR%\..\..\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SETUP_DIR%\..\..\.venv\Scripts\python.exe"
    goto check_packages
)

:: 2. Neu chua co .venv o bat ky dau, tu dong tao moi tai %SETUP_DIR%\.venv
echo ===================================================================
echo       AGY DEV ENGLISH COMPANION - TU DONG THIET LAP MAY MOI
echo ===================================================================
echo  [Thong bao] Phat hien lan chay dau tien hoac chua co moi truong .venv!
echo  He thong dang tu dong khoi tao moi truong ao va cai dat thu vien...
echo ===================================================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo [LOI NGHIEP TRONG] Khong tim thay Python tren he thong!
    echo.
    echo Vui long cai dat Python 3.10 tro len:
    echo 1. Tai tu trang chu: https://www.python.org/downloads/
    echo 2. QUAN TRONG: Tick chon "Add Python to PATH" khi cai dat.
    echo.
    pause
    exit /b 1
)

echo [1/3] Dang tao moi truong ao [.venv]...
python -m venv "%SETUP_DIR%\.venv"
if errorlevel 1 (
    echo [LOI] Khong the tao thu muc .venv! Vui long kiem tra quyen ghi thu muc.
    pause
    exit /b 1
)

set "PYTHON_EXE=%SETUP_DIR%\.venv\Scripts\python.exe"

echo [2/3] Dang nang cap trinh quan ly goi pip...
"%PYTHON_EXE%" -m pip install --upgrade pip --quiet

echo [3/3] Dang cai dat cac thu vien can thiet tu requirements.txt...
"%PYTHON_EXE%" -m pip install -r "%SETUP_DIR%\requirements.txt"
if errorlevel 1 (
    echo.
    echo [LOI] Co loi xay ra khi cai dat thu vien tu requirements.txt!
    echo Vui long kiem tra lai ket noi Internet va thu lai.
    pause
    exit /b 1
)

echo.
echo [OK] Thiet lap moi truong hoan tat thanh cong!
echo ===================================================================
echo.
goto done

:check_packages
:: 3. Kiem tra nhanh xem cac package co ban da duoc cai dat chua
"%PYTHON_EXE%" -c "import textual, rich, deep_translator, pynput, psutil" >nul 2>&1
if errorlevel 1 (
    echo [AGY Companion] Phat hien thieu thu vien trong .venv, dang tu dong cai dat bo sung...
    "%PYTHON_EXE%" -m pip install -r "%SETUP_DIR%\requirements.txt"
)

:done
