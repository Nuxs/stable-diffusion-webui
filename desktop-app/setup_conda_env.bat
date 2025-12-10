@echo off
chcp 65001 >nul
echo ============================================================
echo 创建新的 Conda 环境并安装 PyQt6
echo ============================================================
echo.

REM 检查是否已存在环境
conda env list | findstr "sd-webui" >nul 2>&1
if %errorlevel% == 0 (
    echo 环境 'sd-webui' 已存在
    echo.
    echo 如果环境已存在且包含所需包，可以直接使用
    echo 运行: conda activate sd-webui
    echo.
    set /p choice="是否删除并重新创建? (y/n): "
    if /i "%choice%"=="y" (
        echo 删除现有环境...
        conda env remove -n sd-webui -y
    ) else (
        echo 使用现有环境...
        call conda activate sd-webui
        goto :install
    )
)

echo.
echo 步骤 1: 导出当前环境的包列表...
conda list --export > %TEMP%\conda_packages.txt 2>nul
pip freeze > %TEMP%\pip_packages.txt 2>nul
echo ✓ 已导出包列表

echo.
echo 步骤 2: 创建新的 conda 环境 'sd-webui'（包含当前环境的所有包）...
conda create -n sd-webui python=3.12 -y
if %errorlevel% neq 0 (
    echo ✗ 创建环境失败
    pause
    exit /b 1
)

:install
echo.
echo 步骤 3: 激活环境...
call conda activate sd-webui
if %errorlevel% neq 0 (
    echo ✗ 激活环境失败
    pause
    exit /b 1
)

echo.
echo 步骤 4: 安装当前环境的包（如果是从现有环境创建的）...
if exist %TEMP%\conda_packages.txt (
    echo 从当前环境安装 conda 包...
    conda install --file %TEMP%\conda_packages.txt -y 2>nul
)
if exist %TEMP%\pip_packages.txt (
    echo 从当前环境安装 pip 包...
    pip install -r %TEMP%\pip_packages.txt 2>nul
)

echo.
echo 步骤 5: 安装 PyQt6...
conda install -c conda-forge pyqt -y
if %errorlevel% neq 0 (
    echo.
    echo conda 安装失败，尝试使用 pip...
    pip install PyQt6 PyQt6-WebEngine
)

echo.
echo 步骤 6: 测试 PyQt6...
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 可以正常导入！')"

if %errorlevel% == 0 (
    echo.
    echo ============================================================
    echo ✓ 环境设置成功！
    echo ============================================================
    echo.
    echo 使用方法：
    echo   1. 激活环境: conda activate sd-webui
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

