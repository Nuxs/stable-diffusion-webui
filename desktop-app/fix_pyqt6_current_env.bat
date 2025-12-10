@echo off
chcp 65001 >nul
echo ============================================================
echo 在当前 Conda 环境安装 PyQt6
echo ============================================================
echo.

REM 检查当前环境
python -c "import sys; print('当前 Python:', sys.executable)" 2>nul

echo.
echo 步骤 1: 卸载用户目录中的 PyQt6...
echo.

REM 使用 Python 脚本检查和卸载用户目录的 PyQt6
python -c "import site; import os; import subprocess; import sys; user_site = site.getusersitepackages(); pyqt6_path = os.path.join(user_site, 'PyQt6'); exists = os.path.exists(pyqt6_path); print('FOUND' if exists else 'NOT_FOUND'); sys.exit(0 if exists else 1)" >nul 2>&1
if %errorlevel% == 0 (
    echo 找到用户目录中的 PyQt6，正在卸载...
    python -m pip uninstall -y PyQt6 PyQt6-WebEngine PyQt6-Qt6 PyQt6-WebEngine-Qt6 PyQt6-sip PyQt6_sip --user 2>nul
    echo ✓ 已卸载用户目录中的 PyQt6
) else (
    echo 未找到用户目录中的 PyQt6
)

echo.
echo 步骤 2: 卸载当前环境中的 PyQt6（如果存在）...
python -m pip uninstall -y PyQt6 PyQt6-WebEngine PyQt6-Qt6 PyQt6-WebEngine-Qt6 PyQt6-sip PyQt6_sip 2>nul

echo.
echo 步骤 3: 清理 pip 缓存...
python -m pip cache purge 2>nul

echo.
echo 步骤 4: 在当前 Conda 环境安装 PyQt6...
echo （使用 pip 安装到当前环境，不需要管理员权限）
echo.
python -m pip install --no-cache-dir PyQt6 PyQt6-WebEngine

if %errorlevel% neq 0 (
    echo.
    echo ✗ 安装失败
    echo.
    echo 如果遇到权限问题，请尝试：
    echo 1. 以管理员身份运行此脚本
    echo 2. 或者使用: conda install -c conda-forge pyqt -y（需要管理员权限）
    pause
    exit /b 1
)

echo.
echo 步骤 5: 验证安装位置...
python -c "import PyQt6; import os; print('PyQt6 位置:', os.path.dirname(PyQt6.__file__))" 2>nul

echo.
echo 步骤 6: 测试 PyQt6 导入...
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 可以正常导入！')"

if %errorlevel% == 0 (
    echo.
    echo ============================================================
    echo ✓ 修复成功！
    echo ============================================================
    echo.
    echo PyQt6 已安装到当前 Conda 环境
    echo 现在可以运行应用了：
    echo   .\run_desktop.bat
    echo.
) else (
    echo.
    echo ✗ PyQt6 仍然无法导入
    echo.
    echo 可能的原因：
    echo 1. 缺少 Visual C++ Redistributable
    echo    下载: https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo 2. 需要重启计算机
    echo 3. 杀毒软件可能阻止了 DLL 加载
    echo.
)

echo.
pause

