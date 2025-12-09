@echo off
REM 运行桌面应用程序

cd /d %~dp0

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo 请先安装 Python 3.10 或更高版本
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 安装依赖失败
        pause
        exit /b 1
    )
)

REM 运行应用
python src/main.py

pause

