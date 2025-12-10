@echo off
chcp 65001 >nul
echo ============================================================
echo 使用完整 PyQt6 配置构建应用
echo ============================================================
echo.

cd /d %~dp0

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    pause
    exit /b 1
)

REM 清理旧的构建
echo 清理旧的构建文件...
echo.

REM 尝试关闭可能正在运行的进程
tasklist /FI "IMAGENAME eq StableDiffusionWebUI.exe" 2>NUL | find /I /N "StableDiffusionWebUI.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo 发现正在运行的进程，正在关闭...
    taskkill /F /IM StableDiffusionWebUI.exe >NUL 2>&1
    timeout /t 2 /nobreak >NUL
)

REM 删除旧的构建目录（简单直接，如果失败 PyInstaller 的 --clean 会处理）
if exist dist (
    rmdir /s /q dist 2>NUL
)
if exist build (
    rmdir /s /q build 2>NUL
)
echo 清理完成
echo.

REM 使用完整的 PyQt6 配置构建
echo 开始构建（使用 app_pyqt6_complete.spec）...
echo.
REM 使用 --clean 参数确保清理旧的构建文件
python -m PyInstaller app_pyqt6_complete.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ============================================================
    echo 构建失败！
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 构建完成！
echo ============================================================
echo.
echo 输出目录: dist\StableDiffusionWebUI
echo.
echo 验证构建结果:
echo   1. 检查 DLL 文件: dir dist\StableDiffusionWebUI\_internal\PyQt6\Qt6\bin\*.dll
echo   2. 检查插件: dir dist\StableDiffusionWebUI\_internal\PyQt6\Qt6\plugins
echo   3. 运行测试: cd dist\StableDiffusionWebUI ^&^& StableDiffusionWebUI.exe
echo.
pause

