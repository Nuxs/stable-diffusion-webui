@echo off
REM 使用 conda 环境运行桌面应用程序

cd /d %~dp0

REM 检查 conda 环境是否存在
conda env list | findstr "sd-webui" >nul 2>&1
if errorlevel 1 (
    echo ============================================================
    echo 错误: 未找到 'sd-webui' conda 环境
    echo ============================================================
    echo.
    echo 请先运行: .\setup_conda_env.bat
    echo.
    pause
    exit /b 1
)

REM 激活 conda 环境
call conda activate sd-webui
if errorlevel 1 (
    echo 错误: 无法激活 conda 环境
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
    echo 请运行修复脚本: .\fix_pyqt6_simple.bat
    echo.
    pause
    exit /b 1
)

REM 运行应用
echo 正在启动 Stable Diffusion WebUI 桌面应用...
python src/main.py

pause


