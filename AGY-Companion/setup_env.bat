@echo off
rem ===================================================================
rem AGY Companion - Auto Environment Setup and Dependency Bootstrapper
rem Tu dong kiem tra va khoi tao moi truong .venv tren may moi / sau khi clone
rem Tu dong phat hien va tu sua loi .venv hong (copy tu may khac / sai duong dan Python goc)
rem ===================================================================

set "SETUP_DIR=%~dp0"
if "%SETUP_DIR:~-1%"=="\" set "SETUP_DIR=%SETUP_DIR:~0,-1%"

set "PYTHON_EXE="

:: 1. Kiem tra .venv cuc bo
if not exist "%SETUP_DIR%\.venv\Scripts\python.exe" goto check_parent_1

:: Kiem tra xem Python cuc bo co chay duoc khong
"%SETUP_DIR%\.venv\Scripts\python.exe" -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=%SETUP_DIR%\.venv\Scripts\python.exe"
    goto check_packages
)

echo ===================================================================
echo  [Thong bao] Phat hien .venv bi loi hoac copy tu may khac!
echo  (Khong tim thay Python goc trong file pyvenv.cfg)
echo  Dang tu dong don dep va tao lai moi truong .venv cho may hien tai...
echo ===================================================================
rmdir /s /q "%SETUP_DIR%\.venv"
goto create_venv

:check_parent_1
if not exist "%SETUP_DIR%\..\.venv\Scripts\python.exe" goto check_parent_2
"%SETUP_DIR%\..\.venv\Scripts\python.exe" -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=%SETUP_DIR%\..\.venv\Scripts\python.exe"
    goto check_packages
)

:check_parent_2
if not exist "%SETUP_DIR%\..\..\.venv\Scripts\python.exe" goto create_venv
"%SETUP_DIR%\..\..\.venv\Scripts\python.exe" -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=%SETUP_DIR%\..\..\.venv\Scripts\python.exe"
    goto check_packages
)

:create_venv
echo ===================================================================
echo       AGY DEV ENGLISH COMPANION - TU DONG THIET LAP MAY MOI
echo ===================================================================
echo  [Thong bao] Dang khoi tao moi truong ao .venv va cai dat thu vien...
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
"%PYTHON_EXE%" -c "import textual, rich, deep_translator, pynput, psutil" >nul 2>&1
if errorlevel 1 (
    echo [AGY Companion] Phat hien thieu thu vien trong .venv, dang tu dong cai dat bo sung...
    "%PYTHON_EXE%" -m pip install -r "%SETUP_DIR%\requirements.txt"
    if errorlevel 1 (
        echo [Canh bao] Cai dat bo sung that bai. Dang tao lai .venv moi...
        rmdir /s /q "%SETUP_DIR%\.venv"
        goto create_venv
    )
)

:done
