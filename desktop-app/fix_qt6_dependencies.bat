@echo off
chcp 65001 >nul
echo ============================================================
echo 修复 Qt6 DLL 依赖问题
echo ============================================================
echo.

REM 激活环境
if "%1"=="" (
    set ENV_NAME=sd-webui
) else (
    set ENV_NAME=%1
)

echo 激活环境: %ENV_NAME%
call conda activate %ENV_NAME%
if %errorlevel% neq 0 (
    echo ✗ 无法激活环境
    pause
    exit /b 1
)

echo.
echo 步骤 1: 安装完整的 Qt6 运行时依赖...
echo.

REM 尝试安装 conda-forge 的 Qt6 相关包
conda install -c conda-forge qt-main qt-webengine -y
if %errorlevel% neq 0 (
    echo ⚠ conda 安装失败，继续尝试其他方法...
)

echo.
echo 步骤 2: 安装 Visual C++ 运行时...
conda install -c conda-forge vc14_runtime vcomp14 vs2015_runtime -y

echo.
echo 步骤 3: 安装 Universal C Runtime (UCRT)...
conda install -c conda-forge ucrt -y

echo.
echo 步骤 4: 测试 PyQt6...
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 可以正常导入！')"

if %errorlevel% == 0 (
    echo.
    echo ============================================================
    echo ✓ 修复成功！
    echo ============================================================
) else (
    echo.
    echo ✗ 仍然无法导入
    echo.
    echo 建议：
    echo 1. 安装/更新 Visual C++ Redistributable:
    echo    https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo 2. 重启计算机
    echo 3. 检查 Windows 更新
)

echo.
pause


