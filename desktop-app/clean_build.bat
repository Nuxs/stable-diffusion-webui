@echo off
chcp 65001 >nul
echo ============================================================
echo 清理构建文件
echo ============================================================
echo.

cd /d %~dp0

REM 关闭可能正在运行的进程
echo 1. 关闭正在运行的 StableDiffusionWebUI.exe...
tasklist /FI "IMAGENAME eq StableDiffusionWebUI.exe" 2>NUL | find /I /N "StableDiffusionWebUI.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo    发现进程，正在关闭...
    taskkill /F /IM StableDiffusionWebUI.exe
    if errorlevel 1 (
        echo    无法关闭进程，可能需要管理员权限
    ) else (
        echo    ✓ 进程已关闭
        timeout /t 2 /nobreak >NUL
    )
) else (
    echo    ✓ 没有正在运行的进程
)

echo.
echo 2. 删除构建目录...
if exist dist (
    echo    正在删除 dist 目录...
    rmdir /s /q dist
    if exist dist (
        echo    ✗ 删除失败，可能文件被占用
        echo    请手动关闭相关程序后删除
    ) else (
        echo    ✓ dist 目录已删除
    )
) else (
    echo    ✓ dist 目录不存在
)

if exist build (
    echo    正在删除 build 目录...
    rmdir /s /q build
    if exist build (
        echo    ✗ 删除失败
    ) else (
        echo    ✓ build 目录已删除
    )
) else (
    echo    ✓ build 目录不存在
)

echo.
echo 3. 清理 PyInstaller 缓存...
if exist "%LOCALAPPDATA%\pyinstaller" (
    echo    正在清理 PyInstaller 缓存...
    rmdir /s /q "%LOCALAPPDATA%\pyinstaller" 2>NUL
    echo    ✓ 缓存已清理
) else (
    echo    ✓ 没有缓存需要清理
)

echo.
echo ============================================================
echo 清理完成！
echo ============================================================
echo.
pause


