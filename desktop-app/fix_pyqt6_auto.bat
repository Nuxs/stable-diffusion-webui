@echo off
REM 自动修复 PyQt6 DLL 加载问题
chcp 65001 >nul
echo ============================================================
echo PyQt6 DLL 加载问题自动修复工具
echo ============================================================
echo.

REM 检查是否在 Anaconda 环境
python -c "import sys; exit(0 if 'conda' in sys.executable.lower() or 'anaconda' in sys.executable.lower() else 1)" >nul 2>&1
if %errorlevel% == 0 (
    echo 检测到 Anaconda 环境，尝试使用 conda 安装 PyQt6...
    echo.
    
    REM 尝试使用 conda 安装
    conda install -c conda-forge pyqt -y
    if %errorlevel% == 0 (
        echo.
        echo ✓ conda 安装完成，测试导入...
        python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 可以正常导入！')" 2>nul
        if %errorlevel% == 0 (
            echo.
            echo ============================================================
            echo ✓ 修复成功！PyQt6 现在可以正常使用了
            echo ============================================================
            pause
            exit /b 0
        )
    )
    echo.
    echo conda 安装失败或无法解决问题，尝试 pip 重新安装...
    echo.
)

REM 完全卸载 PyQt6
echo 步骤 1: 卸载现有的 PyQt6...
python -m pip uninstall -y PyQt6 PyQt6-WebEngine PyQt6-Qt6 PyQt6-WebEngine-Qt6 PyQt6-sip PyQt6_sip 2>nul

REM 清理缓存
echo 步骤 2: 清理 pip 缓存...
python -m pip cache purge 2>nul

REM 重新安装
echo 步骤 3: 重新安装 PyQt6...
python -m pip install --no-cache-dir PyQt6 PyQt6-WebEngine
if %errorlevel% neq 0 (
    echo.
    echo ✗ 安装失败，请检查网络连接或手动安装
    pause
    exit /b 1
)

echo.
echo 步骤 4: 测试 PyQt6 导入...
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 可以正常导入！')"
if %errorlevel% == 0 (
    echo.
    echo ============================================================
    echo ✓ 修复成功！PyQt6 现在可以正常使用了
    echo ============================================================
    echo.
    echo 您现在可以运行应用了：
    echo   python src\main.py
    echo   或
    echo   .\run_desktop.bat
) else (
    echo.
    echo ✗ PyQt6 仍然无法导入
    echo.
    echo 可能的原因：
    echo 1. 缺少 Visual C++ Redistributable
    echo    下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo 2. 系统环境问题，建议重启计算机
    echo 3. 杀毒软件可能阻止了 DLL 加载
    echo.
    echo 请尝试：
    echo 1. 安装 Visual C++ Redistributable 并重启
    echo 2. 以管理员身份运行此脚本
    echo 3. 检查杀毒软件设置
)

echo.
pause


