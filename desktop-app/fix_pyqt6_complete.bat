@echo off
REM 完整修复 PyQt6 DLL 问题

echo ========================================
echo PyQt6 DLL 问题完整修复工具
echo ========================================
echo.

echo [步骤 1/3] 卸载 PyQt6...
pip uninstall -y PyQt6 PyQt6-WebEngine PyQt6-Qt6 PyQt6-WebEngine-Qt6 PyQt6-sip
if errorlevel 1 (
    echo 警告: 卸载过程中出现错误，继续...
)
echo.

echo [步骤 2/3] 清理缓存...
pip cache purge
echo.

echo [步骤 3/3] 重新安装 PyQt6...
pip install --no-cache-dir PyQt6 PyQt6-WebEngine
if errorlevel 1 (
    echo 错误: 安装失败
    pause
    exit /b 1
)
echo.

echo ========================================
echo 安装完成！正在测试...
echo ========================================
echo.

python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 可以正常导入！')"
if errorlevel 1 (
    echo.
    echo ✗ PyQt6 仍然无法导入
    echo.
    echo 请尝试以下步骤:
    echo 1. 安装 Visual C++ Redistributable:
    echo    https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo 2. 重启计算机
    echo 3. 重新运行此脚本
) else (
    echo.
    echo ✓ 修复成功！现在可以运行应用了
)

echo.
pause



