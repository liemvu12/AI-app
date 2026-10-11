@echo off
title Dang nhap Shopee QR Code
echo ========================================================
echo   DANG NHAP SHOPEE QUA MA QR - 1-CLICK LOGIN
echo ========================================================
echo.
cd /d "%~dp0"
python auth.py
echo.
echo ========================================================
echo   Hoan tat qua trinh dang nhap.
echo ========================================================
pause
