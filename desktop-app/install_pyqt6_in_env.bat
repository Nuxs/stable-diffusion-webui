@echo off
chcp 65001 >nul
echo ============================================================
echo 在 Conda 环境中安装 PyQt6
echo ============================================================
echo.

REM 检查是否指定了环境名称
if "%1"=="" (
    echo 用法: .\install_pyqt6_in_env.bat [环境名称]
    echo 示例: .\install_pyqt6_in_env.bat sd-webui
    echo 或: .\install_pyqt6_in_env.bat base
    echo.
    set /p ENV_NAME="请输入环境名称 (直接回车使用当前环境): "
    if "!ENV_NAME!"=="" (
        set ENV_NAME=current
    )
) else (
    set ENV_NAME=%1
)

if /i "%ENV_NAME%"=="current" (
    echo 使用当前环境...
) else (
    echo 激活环境: %ENV_NAME%
    call conda activate %ENV_NAME%
    if %errorlevel% neq 0 (
        echo ✗ 无法激活环境: %ENV_NAME%
        pause
        exit /b 1
    )
)

echo.
echo 步骤 1: 检查当前安装...
python -c "try: import PyQt5; print('✓ PyQt5 已安装'); except: print('✗ PyQt5 未安装')" 2>nul
python -c "try: import PyQt6; print('✓ PyQt6 已安装'); except: print('✗ PyQt6 未安装')" 2>nul

echo.
echo 步骤 2: 卸载用户目录中的 PyQt6（如果存在）...
python -m pip uninstall -y PyQt6 PyQt6-WebEngine PyQt6-Qt6 PyQt6-WebEngine-Qt6 PyQt6-sip PyQt6_sip --user 2>nul

echo.
echo 步骤 3: 在当前环境安装 PyQt6...
python -m pip install --no-cache-dir PyQt6 PyQt6-WebEngine

if %errorlevel% neq 0 (
    echo.
    echo ✗ 安装失败
    pause
    exit /b 1
)

echo.
echo 步骤 4: 验证安装...
python -c "import PyQt6; import os; print('PyQt6 位置:', os.path.dirname(PyQt6.__file__))" 2>nul

echo.
echo 步骤 5: 测试导入...
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 可以正常导入！')"

if %errorlevel% == 0 (
    echo.
    echo ============================================================
    echo ✓ 安装成功！
    echo ============================================================
    echo.
    echo 现在可以运行应用了：
    if /i not "%ENV_NAME%"=="current" (
        echo   1. 激活环境: conda activate %ENV_NAME%
    )
    echo   2. 运行应用: python src\main.py
    echo   或使用: .\run_desktop.bat
    echo.
) else (
    echo.
    echo ✗ PyQt6 仍然无法导入
    echo 请检查 Visual C++ Redistributable 是否已安装
)

echo.
pause


