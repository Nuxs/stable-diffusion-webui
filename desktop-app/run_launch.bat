@echo off
REM 从 desktop-app 目录运行项目根目录的 launch.py

cd /d %~dp0
cd ..

REM 检查 launch.py 是否存在
if not exist "launch.py" (
    echo 错误: 在项目根目录找不到 launch.py
    echo 当前目录: %CD%
    pause
    exit /b 1
)

REM 运行 launch.py
echo 正在运行 launch.py...
python launch.py --skip-torch-cuda-test

pause


