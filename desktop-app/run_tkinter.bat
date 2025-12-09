@echo off
REM 运行 Tkinter 版本的桌面应用（无需 PyQt6）

cd /d %~dp0

echo ========================================
echo Stable Diffusion WebUI - Tkinter 版本
echo ========================================
echo.
echo 此版本使用 Python 内置的 tkinter，无需 PyQt6
echo.

python src/main_tkinter.py

pause


