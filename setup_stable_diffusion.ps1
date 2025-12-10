# Stable Diffusion WebUI Windows 11 安装脚本
# 请以管理员权限运行此脚本

# 设置执行策略
Set-ExecutionPolicy Bypass -Scope Process -Force

# 检查是否以管理员权限运行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "请以管理员权限运行此脚本！" -ForegroundColor Red
    Exit
}

# 创建日志函数
function Write-Log {
    param($Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
}

Write-Log "开始安装 Stable Diffusion WebUI 环境..."

# 首先检查并删除现有的venv目录
if (Test-Path "venv") {
    Write-Log "删除现有的Python虚拟环境..."
    Remove-Item -Recurse -Force "venv"
}

# 检查Python版本 - 需要确保安装3.10.6版本
$pythonInstalled = $false
$pythonCmd = $null

# 检查是否已安装Python 3.10
foreach ($testCmd in @("python3.10", "python3", "python")) {
    try {
        $version = & $testCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($version -eq "3.10") {
            $pythonInstalled = $true
            $pythonCmd = $testCmd
            Write-Log "找到兼容的Python版本: $testCmd ($version)"
            break
        }
    } catch {
        # 命令不存在或不是有效的Python，继续尝试下一个
    }
}

# 如果没有找到Python 3.10，则安装它
if (-not $pythonInstalled) {
    Write-Log "需要安装Python 3.10.6 (稳定版本)..."
    $pythonUrl = "https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-3.10.6-amd64.exe"
    
    Write-Log "下载Python 3.10.6..."
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
    
    Write-Log "安装Python 3.10.6 (这可能需要一些时间)..."
    # 安装Python，并将其添加到PATH中，但不注册为默认Python
    Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0" -Wait
    Remove-Item $pythonInstaller
    
    # 安装后确认Python安装路径
    $pythonCmd = "python"
    # 检查Python版本 - 为了确认安装成功
    try {
        $pythonVersion = & $pythonCmd --version
        Write-Log "已安装: $pythonVersion"
    } catch {
        Write-Log "警告: Python安装后无法验证版本。请确保Python 3.10.6已正确安装。"
    }
}

# 检查并安装 Git
Write-Log "检查 Git 安装..."
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Log "正在下载并安装 Git..."
    $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.41.0.windows.1/Git-2.41.0-64-bit.exe"
    $gitInstaller = "$env:TEMP\Git-2.41.0-64-bit.exe"
    Invoke-WebRequest -Uri $gitUrl -OutFile $gitInstaller
    Start-Process -FilePath $gitInstaller -ArgumentList "/VERYSILENT", "/NORESTART" -Wait
    Remove-Item $gitInstaller
}

# 检查是否已克隆仓库
if (-not (Test-Path "launch.py")) {
    Write-Log "正在克隆Stable Diffusion WebUI仓库..."
    git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git .
}

# 创建虚拟环境 - 使用Python 3.10
Write-Log "创建新的Python 3.10虚拟环境..."
& $pythonCmd -m venv venv

# 激活虚拟环境
Write-Log "激活虚拟环境..."
$activateScript = ".\venv\Scripts\activate.ps1"
if (Test-Path $activateScript) {
    . $activateScript
} else {
    Write-Log "错误: 找不到虚拟环境激活脚本。请手动激活环境。"
    Exit
}

# 安装依赖
Write-Log "安装Python依赖..."
python -m pip install --upgrade pip

# 安装特定版本的torch和torchvision
Write-Log "安装Pytorch (兼容版本)..."
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118

# 安装其他依赖
if (Test-Path "requirements.txt") {
    Write-Log "安装requirements.txt中的依赖..."
    pip install -r requirements.txt
} else {
    Write-Log "警告: 找不到requirements.txt文件"
}

# 下载模型（可选，取决于用户需求）
Write-Log "创建模型目录..."
$modelDirs = @("models/Stable-diffusion", "models/VAE", "models/Lora", "models/ControlNet")
foreach ($dir in $modelDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
    }
}

Write-Log "环境配置完成！"
Write-Log "你现在可以通过运行 'webui.bat' 来启动 Stable Diffusion WebUI"

# 添加启动说明
Write-Host "`n=== 使用说明 ===" -ForegroundColor Green
Write-Host "1. 请确保已下载所需的模型文件并放置在相应目录中"
Write-Host "2. 运行 webui.bat 启动界面"
Write-Host "3. 首次启动可能需要一些时间来下载额外依赖"
Write-Host "4. 访问 http://localhost:7860 即可使用 WebUI"
Write-Host "==================`n" 