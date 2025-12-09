@echo off
REM 快速修复 PyQt6 - 使用 conda（推荐，因为使用 Anaconda）

echo ========================================
echo PyQt6 修复工具
echo ========================================
echo.

echo 检测到您使用 Anaconda，建议使用 conda 安装 PyQt6
echo.

echo [选项 1] 使用 conda 安装（推荐）
echo 执行: conda install -c conda-forge pyqt
echo.

echo [选项 2] 使用 pip 重新安装
echo 执行以下命令:
echo   pip uninstall -y PyQt6 PyQt6-WebEngine
echo   pip install --no-cache-dir PyQt6 PyQt6-WebEngine
echo.

echo [选项 3] 安装特定版本（如果最新版有问题）
echo   pip install PyQt6==6.6.0 PyQt6-WebEngine==6.6.0
echo.

echo ========================================
echo 正在尝试使用 conda 安装...
echo ========================================
echo.

conda install -c conda-forge pyqt -y
if errorlevel 1 (
    echo.
    echo conda 安装失败，尝试使用 pip...
    echo.
    pip uninstall -y PyQt6 PyQt6-WebEngine PyQt6-Qt6 PyQt6-WebEngine-Qt6 PyQt6-sip
    pip install --no-cache-dir PyQt6 PyQt6-WebEngine
)

echo.
echo ========================================
echo 测试安装...
echo ========================================
echo.

python -c "from PyQt6.QtWidgets import QApplication; print('✓ 成功！PyQt6 可以正常导入')" 2>nul
if errorlevel 1 (
    echo ✗ PyQt6 仍然无法导入
    echo.
    echo 请尝试:
    echo 1. 重启计算机
    echo 2. 使用官方 Python（而不是 Anaconda）
    echo 3. 查看 CRITICAL_FIX.md 获取更多帮助
) else (
    echo.
    echo ✓ 修复成功！现在可以运行应用了
    echo   运行: python src/main.py
)

echo.
pause


