@echo off
REM 运行桌面应用程序（从项目根目录）

cd /d %~dp0

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo 请先安装 Python 3.10 或更高版本
    pause
    exit /b 1
)

REM 检查 PyQt6 是否可以正常导入
python -c "from PyQt6.QtWidgets import QApplication" >nul 2>&1
if errorlevel 1 (
    echo ============================================================
    echo 错误: PyQt6 无法正常加载
    echo ============================================================
    echo.
    echo 检测到 PyQt6 DLL 加载失败，这通常是因为：
    echo 1. PyQt6 安装不完整或损坏
    echo 2. 缺少 Visual C++ Redistributable
    echo 3. Anaconda 环境与 pip 安装的包冲突
    echo.
    echo 请运行修复脚本：
    echo   .\fix_pyqt6_auto.bat
    echo.
    echo 或者手动执行：
    echo   1. 如果使用 Anaconda: conda install -c conda-forge pyqt
    echo   2. 否则: pip uninstall -y PyQt6 PyQt6-WebEngine ^&^& pip install --no-cache-dir PyQt6 PyQt6-WebEngine
    echo.
    pause
    exit /b 1
)

REM 运行应用
echo 正在启动 Stable Diffusion WebUI 桌面应用...
python src/main.py

pause


