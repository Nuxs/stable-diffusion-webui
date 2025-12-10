# 构建指南

本文档面向开发者，介绍如何从源代码构建和打包 Stable Diffusion WebUI Desktop。

---

## 目录

1. [环境准备](#环境准备)
2. [开发环境设置](#开发环境设置)
3. [运行和调试](#运行和调试)
4. [构建应用](#构建应用)
5. [测试打包结果](#测试打包结果)
6. [创建安装包](#创建安装包)
7. [故障排除](#故障排除)

---

## 环境准备

### 系统要求

- **操作系统**: Windows 10/11 (64位)
- **Python**: 3.10.x（推荐 3.10.11）
- **Git**: 用于克隆仓库
- **Visual Studio**: 用于编译某些 Python 包（可选）

### 安装 Python 3.10

```powershell
# 下载 Python 3.10.11
# https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe

# 或使用 Chocolatey
choco install python --version=3.10.11

# 验证安装
python --version  # 应显示 Python 3.10.11
```

### 克隆仓库

```bash
# 克隆主仓库
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui

# 进入桌面应用目录
cd desktop-app
```

---

## 开发环境设置

### 1. 创建虚拟环境

```powershell
# 在 desktop-app 目录
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate  # Windows PowerShell
# 或
.\venv\Scripts\activate.bat  # Windows CMD
```

### 2. 安装依赖

```powershell
# 安装桌面应用依赖
pip install -r requirements.txt

# 依赖列表：
# - PyQt6 >= 6.6.0
# - PyQt6-WebEngine >= 6.6.0
# - requests >= 2.31.0
# - pyinstaller >= 6.0.0
# - py7zr >= 0.20.0 (可选)
```

### 3. 项目结构

```
desktop-app/
├── src/                          # 源代码
│   ├── launcher.py               # 主入口（新）
│   ├── main_window.py            # 主窗口
│   ├── server_manager.py         # 服务器管理
│   ├── system_detector.py        # 系统检测（新）
│   ├── download_manager.py       # 下载管理（新）
│   ├── model_manager.py          # 模型管理（新）
│   ├── first_run_wizard.py       # 首次运行向导（新）
│   └── utils/                    # 工具模块
│       ├── config.py             # 配置管理
│       ├── logger.py             # 日志管理
│       ├── environment_manager.py# 环境管理
│       └── portable_python.py    # Portable Python（新）
│
├── config/                       # 配置文件（新）
│   └── components.json           # 组件配置
│
├── resources/                    # 资源文件
│   └── icon.ico                  # 应用图标
│
├── app.spec                      # PyInstaller 配置
├── build.py                      # 构建脚本
├── requirements.txt              # Python 依赖
├── rthook_pyqt6_fix.py          # PyQt6 运行时修复
└── README.md                     # 说明文档
```

---

## 运行和调试

### 开发模式运行

```powershell
# 确保在 desktop-app 目录且虚拟环境已激活
python src/launcher.py
```

**注意事项**：
- 开发模式会自动检测并使用系统中的 PyQt6
- 首次运行会触发首次运行向导（如果 `data/` 目录不存在）
- 日志输出到控制台和 `logs/app.log`

### 调试技巧

#### 1. 启用详细日志

```python
# 在 src/launcher.py 中修改日志级别
import logging
logging.basicConfig(level=logging.DEBUG)  # DEBUG 模式
```

#### 2. 跳过首次运行向导

```python
# 临时创建必要的目录结构
mkdir -p data/python-env
mkdir -p data/webui
mkdir -p data/models/Stable-diffusion
```

#### 3. 使用 IDE 调试

**VS Code 配置** (`.vscode/launch.json`):

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Launcher",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/launcher.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

---

## 构建应用

### 方法 1: 使用构建脚本（推荐）

```powershell
# 在 desktop-app 目录
python build.py
```

**构建过程**：

1. ✓ 检查 PyInstaller 和 PyQt6
2. ✓ 清理旧的构建文件 (`dist/`, `build/`)
3. ✓ 验证 `app.spec` 和配置文件
4. ✓ 执行 PyInstaller 打包
5. ✓ 输出构建结果

**输出位置**：
```
dist/StableDiffusionWebUI/
├── StableDiffusionWebUI.exe    # 主程序
└── _internal/                   # 依赖文件
    ├── PyQt6/
    ├── config/
    └── ...
```

### 方法 2: 直接使用 PyInstaller

```powershell
# 手动构建（如果 build.py 有问题）
pyinstaller app.spec --clean --noconfirm
```

### 构建选项

**修改 `app.spec` 中的配置**：

```python
# 控制台模式（调试用）
console=True  # 显示控制台窗口

# 单文件模式（不推荐）
# 注意：目录模式更稳定
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # 包含二进制文件
    ...
    exclude_binaries=False,  # 改为 False
)
# 并移除 COLLECT 部分
```

---

## 测试打包结果

### 基本测试

```powershell
# 1. 清理 data 目录（测试首次运行）
Remove-Item -Recurse -Force dist/StableDiffusionWebUI/data -ErrorAction SilentlyContinue

# 2. 运行打包的应用
cd dist/StableDiffusionWebUI
.\StableDiffusionWebUI.exe

# 3. 测试首次运行向导
# - 检查系统检测是否正常
# - 尝试选择不同的组件
# - 测试下载流程（可以取消）

# 4. 测试主界面
# - 检查 WebUI 是否正常加载
# - 测试基本功能
```

### 完整测试清单

- [ ] 首次运行向导
  - [ ] 系统信息检测准确
  - [ ] 推荐配置合理
  - [ ] 下载进度显示正常
  - [ ] 可以取消下载
  - [ ] 安装完成后正常启动

- [ ] 主界面
  - [ ] WebUI 正常加载
  - [ ] 服务器自动启动
  - [ ] 图像生成功能正常
  - [ ] 菜单和工具栏响应

- [ ] 错误处理
  - [ ] 缺少依赖时显示友好错误
  - [ ] 网络错误时能够重试
  - [ ] 磁盘空间不足时给出提示

### 在干净系统测试

**推荐使用虚拟机**：

1. 创建 Windows 10 虚拟机（VirtualBox / VMware）
2. **不安装** Python、Git 等开发工具
3. 安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
4. 复制 `dist/StableDiffusionWebUI/` 到虚拟机
5. 运行 `StableDiffusionWebUI.exe`
6. 测试完整的用户体验

---

## 创建安装包

### 使用 Inno Setup（可选）

```powershell
# 1. 安装 Inno Setup
# https://jrsoftware.org/isdl.php

# 2. 创建安装脚本（已有 installer.iss）

# 3. 编译安装包
iscc installer.iss

# 4. 输出
# Output/StableDiffusionDesktopSetup.exe
```

### 分发检查清单

- [ ] 包含所有必要的 DLL
- [ ] 配置文件完整
- [ ] README 和用户指南
- [ ] 许可证文件
- [ ] 版本号正确
- [ ] 数字签名（可选，推荐）

---

## 故障排除

### 常见构建问题

#### 问题 1: PyInstaller 找不到 PyQt6

```
ModuleNotFoundError: No module named 'PyQt6'
```

**解决方案**：
```powershell
# 确保在虚拟环境中
pip install PyQt6 PyQt6-WebEngine
```

#### 问题 2: 构建时 DLL 加载警告

```
WARNING: lib not found: Qt6Core.dll
```

**说明**：这是正常的，不影响最终打包结果。PyInstaller 会通过其他方式收集 DLL。

#### 问题 3: 打包后启动失败

**调试步骤**：
```powershell
# 1. 使用控制台模式重新构建
# 修改 app.spec: console=True

# 2. 运行并查看错误信息
dist\StableDiffusionWebUI\StableDiffusionWebUI.exe

# 3. 检查日志
type dist\StableDiffusionWebUI\logs\app.log
```

#### 问题 4: WebUI 无法加载

**检查清单**：
- [ ] `_internal/` 目录是否包含 WebUI 核心文件
- [ ] Python 环境是否正确设置
- [ ] 端口 7860 是否被占用
- [ ] 防火墙是否阻止

### 性能优化

#### 减小打包体积

```python
# 在 app.spec 中排除不必要的模块
excludes=[
    'test',
    'tests',
    'unittest',
    'distutils',
    'setuptools',
]
```

#### 加快构建速度

```powershell
# 1. 使用增量构建（不清理 build 目录）
pyinstaller app.spec --noconfirm
# 不使用 --clean

# 2. 使用 UPX 压缩（可选，可能导致 DLL 问题）
# 在 app.spec 中
upx=True,
upx_exclude=['Qt6Core.dll', 'Qt6Gui.dll'],  # 排除关键 DLL
```

---

## 高级主题

### 自定义配置

#### 修改组件配置

编辑 `config/components.json`：

```json
{
  "models": {
    "my-custom-model": {
      "id": "my-custom-model",
      "name": "My Custom Model",
      "size_bytes": 4000000000,
      "url": "https://example.com/model.safetensors",
      "recommended": true
    }
  }
}
```

#### 添加镜像源

创建 `config/mirrors.json`：

```json
{
  "pypi": [
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://mirrors.aliyun.com/pypi/simple"
  ],
  "huggingface": [
    "https://hf-mirror.com"
  ]
}
```

### CI/CD 集成

#### GitHub Actions 示例

```yaml
name: Build Desktop App

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd desktop-app
          pip install -r requirements.txt
      
      - name: Build application
        run: |
          cd desktop-app
          python build.py
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: StableDiffusionDesktop
          path: desktop-app/dist/StableDiffusionWebUI/
```

---

## 参考资料

- [PyInstaller 文档](https://pyinstaller.org/en/stable/)
- [PyQt6 文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [ARCHITECTURE_ANALYSIS.md](ARCHITECTURE_ANALYSIS.md) - 详细架构文档

---

## 贡献指南

如果您想贡献代码：

1. Fork 仓库
2. 创建特性分支
3. 遵循代码风格（PEP 8）
4. 添加必要的测试
5. 更新文档
6. 提交 Pull Request

---

## 获取帮助

- **构建问题**：查看本文档的故障排除章节
- **功能请求**：提交 GitHub Issue
- **技术讨论**：加入 Discord/论坛

---

<div align="center">
Happy Building! 🚀
</div>

