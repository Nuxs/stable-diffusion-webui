@echo off
REM 安装脚本 - 安装桌面应用所需的依赖

cd /d %~dp0

echo ========================================
echo Stable Diffusion WebUI 桌面应用安装
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python
    echo 请先安装 Python 3.10 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] Python 版本:
python --version
echo.

REM 升级 pip
echo [信息] 升级 pip...
python -m pip install --upgrade pip
echo.

REM 安装依赖
echo [信息] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 现在可以运行 run.bat 启动应用程序
echo.
pause

