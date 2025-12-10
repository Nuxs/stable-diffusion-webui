@echo off
chcp 65001 >nul
echo ============================================================
echo PyQt6 快速修复工具
echo ============================================================
echo.

echo 步骤 1: 完全卸载 PyQt6...
python -m pip uninstall -y PyQt6 PyQt6-WebEngine PyQt6-Qt6 PyQt6-WebEngine-Qt6 PyQt6-sip PyQt6_sip 2>nul

echo.
echo 步骤 2: 清理缓存...
python -m pip cache purge 2>nul

echo.
echo 步骤 3: 重新安装 PyQt6（安装到当前环境）...
python -m pip install --no-cache-dir --force-reinstall PyQt6 PyQt6-WebEngine

if %errorlevel% neq 0 (
    echo.
    echo ✗ 安装失败
    pause
    exit /b 1
)

echo.
echo 步骤 4: 测试导入...
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 可以正常导入！')"

if %errorlevel% == 0 (
    echo.
    echo ============================================================
    echo ✓ 修复成功！
    echo ============================================================
    echo.
    echo 现在可以运行应用了：
    echo   .\run_desktop.bat
) else (
    echo.
    echo ✗ 仍然无法导入
    echo.
    echo 请尝试：
    echo 1. 重启计算机
    echo 2. 安装 Visual C++ Redistributable:
    echo    https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo 3. 使用 conda 安装: conda install -c conda-forge pyqt
)

echo.
pause


