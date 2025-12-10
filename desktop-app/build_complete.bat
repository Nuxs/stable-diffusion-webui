@echo off
chcp 65001 >nul
echo ============================================================
echo 完整打包脚本（分离式方案）
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

REM 运行完整打包脚本
echo 开始完整打包流程...
echo.
python build_complete.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo 打包失败！
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 打包完成！
echo ============================================================
echo.
echo 输出目录: dist\StableDiffusionWebUI
echo.
echo 验证构建结果:
echo   1. 检查应用: dir dist\StableDiffusionWebUI\StableDiffusionWebUI.exe
echo   2. 检查环境包: dir dist\StableDiffusionWebUI\environment\venv.*
echo   3. 检查总大小（应该约4-5GB）: dir dist\StableDiffusionWebUI
echo   4. 运行测试: cd dist\StableDiffusionWebUI ^&^& StableDiffusionWebUI.exe
echo.
pause
