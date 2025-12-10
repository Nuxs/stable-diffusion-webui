# Stable Diffusion WebUI 桌面版 - 架构分析与重构方案

## 文档版本
- **创建日期**: 2024-12-10
- **版本**: v1.0
- **分析范围**: `python build.py` 构建流程完整链路

---

## 目录
1. [执行摘要](#执行摘要)
2. [当前架构分析](#当前架构分析)
3. [数据链路图](#数据链路图)
4. [痛点分析](#痛点分析)
5. [重构方案](#重构方案)
6. [实施路线图](#实施路线图)

---

## 执行摘要

### 当前状态
桌面版使用 **PyQt6 + PyInstaller** 打包方案，采用**分离式环境管理**（venv 独立压缩），构建产物约 4-5GB（应用 ~600MB + venv.7z ~3-4GB）。

### 核心痛点
**无法开箱即用** - 资源和依赖未完整整合，需要：
- 首次运行时解压 Python 环境（5-10分钟）
- 手动下载 Stable Diffusion 模型
- 依赖外部 7-Zip 或特定解压工具
- venv 环境可能与目标系统不兼容

### 推荐方案
**混合打包 + 智能引导方案**（详见第5章）

---

## 当前架构分析

### 2.1 构建流程架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      BUILD PIPELINE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. 准备阶段 (build.py)                                          │
│     ├── 检查 PyInstaller                                        │
│     ├── 检查 PyQt6 DLL 路径                                     │
│     ├── 清理旧构建 (dist/, build/)                              │
│     └── 验证 app.spec + rthook_pyqt6_fix.py                     │
│                                                                  │
│  2. 收集阶段 (app.spec)                                         │
│     ├── PyQt6 依赖收集                                          │
│     │   ├── Qt6/bin/*.dll (所有 Qt DLL)                         │
│     │   ├── Qt6/plugins/* (平台插件、图像格式等)                │
│     │   └── Qt6/qml/* (WebEngine QML 模块)                      │
│     │                                                            │
│     ├── WebUI 核心文件收集                                       │
│     │   ├── 核心目录: modules, scripts, javascript, html        │
│     │   ├── 配置目录: configs, textual_inversion_templates      │
│     │   ├── 扩展目录: extensions-builtin                        │
│     │   └── 核心文件: launch.py, webui.py, requirements.txt     │
│     │                                                            │
│     └── 排除大文件                                               │
│         ├── models/ (模型文件，数GB)                            │
│         ├── outputs/ (输出文件)                                 │
│         ├── repositories/ (Git 仓库)                            │
│         └── venv/ (虚拟环境，单独处理)                          │
│                                                                  │
│  3. 打包阶段 (PyInstaller)                                      │
│     ├── Analysis: 依赖分析 + hook 注入                          │
│     ├── PYZ: Python 字节码压缩                                  │
│     ├── EXE: 生成可执行文件 (exclude_binaries=True)             │
│     └── COLLECT: 收集到目录 (目录模式)                          │
│                                                                  │
│  4. 环境包创建 (可选, create_environment_package.py)             │
│     ├── 检测 venv/ 存在                                         │
│     ├── 7z 压缩 (mx=5, 多线程)                                  │
│     │   └── 排除: __pycache__, *.pyc, test/                     │
│     ├── 输出: environment/venv.7z (~3-4GB)                      │
│     └── 复制到 dist/StableDiffusionWebUI/environment/           │
│                                                                  │
│  5. 输出结构                                                     │
│     dist/StableDiffusionWebUI/                                   │
│     ├── StableDiffusionWebUI.exe (~50MB)                         │
│     ├── _internal/ (~550MB)                                      │
│     │   ├── PyQt6/                                               │
│     │   ├── modules/                                             │
│     │   ├── scripts/                                             │
│     │   └── ... (WebUI 核心文件)                                │
│     ├── environment/ (可选)                                      │
│     │   └── venv.7z (~3-4GB)                                     │
│     └── README.txt                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 运行时架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    RUNTIME ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  启动流程 (StableDiffusionWebUI.exe)                             │
│  ═════════════════════════════════════════                       │
│                                                                  │
│  1. main.py: 入口点                                              │
│     │                                                            │
│     ├─> setup_pyqt6_dll_path()                                  │
│     │   ├── 检测打包模式 (frozen)                               │
│     │   ├── 定位 DLL 路径: _internal/PyQt6/Qt6/bin              │
│     │   ├── 使用 3 种方法添加 DLL 搜索路径:                      │
│     │   │   ① AddDllDirectory (Windows API)                     │
│     │   │   ② os.add_dll_directory (Python 3.8+)                │
│     │   │   ③ PATH 环境变量                                     │
│     │   └── 预加载 Qt6Core.dll                                  │
│     │                                                            │
│     ├─> setup_runtime_environment()                             │
│     │   └── environment_manager.py                              │
│     │       ├── 检查 venv/ 是否存在                             │
│     │       ├── 不存在 → 解压 environment/venv.7z               │
│     │       │   ├── 优先使用 7z 命令                            │
│     │       │   └── 备用: py7zr / zipfile                       │
│     │       └── 返回 python.exe 路径                            │
│     │                                                            │
│     └─> 导入 PyQt6 + 启动主窗口                                 │
│                                                                  │
│  2. MainWindow (main_window.py)                                  │
│     │                                                            │
│     ├─> 初始化 UI                                                │
│     │   ├── QWebEngineView (嵌入式浏览器)                        │
│     │   ├── 菜单栏 (文件/视图/服务器/帮助)                       │
│     │   ├── 工具栏 (重新加载/浏览器打开)                         │
│     │   └── 状态栏 (进度条 + 状态提示)                          │
│     │                                                            │
│     └─> 初始化 ServerManager                                    │
│                                                                  │
│  3. ServerManager (server_manager.py)                            │
│     │                                                            │
│     ├─> start_server()                                          │
│     │   │                                                        │
│     │   ├── 1. 确定 Python 解释器                               │
│     │   │   ├── 优先: environment_manager 提供的 venv python    │
│     │   │   ├── 次选: 项目根目录 venv/Scripts/python.exe        │
│     │   │   ├── 后备: 系统 Python 3.10                          │
│     │   │   └── 验证版本必须是 3.10                             │
│     │   │                                                        │
│     │   ├── 2. 定位 WebUI 启动脚本                              │
│     │   │   ├── 优先: project_root/launch.py                    │
│     │   │   └── 备用: project_root/webui.py                     │
│     │   │                                                        │
│     │   ├── 3. 构建启动命令                                      │
│     │   │   python.exe launch.py --port 7860 \                  │
│     │   │       --skip-python-version-check                     │
│     │   │                                                        │
│     │   ├── 4. 后台启动进程                                      │
│     │   │   ├── subprocess.Popen                                │
│     │   │   ├── cwd = project_root                              │
│     │   │   └── 捕获 stdout/stderr                              │
│     │   │                                                        │
│     │   └── 5. 监听服务器就绪                                    │
│     │       ├── 定时检查端口 (每2秒)                            │
│     │       ├── 解析服务器输出 (URL)                            │
│     │       └── 发送 server_ready 信号                          │
│     │                                                            │
│     └─> check_server_status()                                   │
│         ├── 检测进程存活                                         │
│         ├── 检测端口可访问                                       │
│         └── HTTP 健康检查                                        │
│                                                                  │
│  4. WebUI 加载                                                   │
│     │                                                            │
│     └─> QWebEngineView.setUrl(http://127.0.0.1:7860)           │
│         └── 显示 Gradio WebUI                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 关键组件详解

#### 2.3.1 PyQt6 DLL 加载机制

**问题背景**：PyQt6 依赖 Qt6 DLL，Windows 上 DLL 搜索路径机制复杂。

**解决方案**：多层冗余
1. **Runtime Hook** (`rthook_pyqt6_fix.py`)：PyInstaller 运行时最早执行
2. **Main 入口** (`main.py::setup_pyqt6_dll_path`)：导入 PyQt6 之前设置
3. **PATH 环境变量**：最兼容的方案

**关键路径**：
```
dist/StableDiffusionWebUI/
└── _internal/
    └── PyQt6/
        └── Qt6/
            ├── bin/           ← DLL 所在位置
            │   ├── Qt6Core.dll
            │   ├── Qt6Gui.dll
            │   ├── Qt6WebEngineCore.dll
            │   └── ... (60+ DLL)
            │
            ├── plugins/       ← Qt 插件 (必需)
            │   ├── platforms/
            │   ├── imageformats/
            │   └── ...
            │
            └── qml/           ← WebEngine QML (必需)
```

#### 2.3.2 环境管理机制

**分离式打包方案**：
- **原理**：venv 环境 (8GB+) 太大，不直接打包到 exe
- **实现**：压缩为 `venv.7z` (~3-4GB)，首次运行解压

**流程**：
```python
# environment_manager.py
1. 检测 venv/Scripts/python.exe
   ↓ 不存在
2. 查找 environment/venv.7z
   ↓
3. 解压（5-10分钟）
   - 优先: 7z 命令 (最快)
   - 备用: py7zr 库
   - 最后: zipfile 模块
   ↓
4. 验证 python.exe
   ↓
5. 返回路径给 ServerManager
```

**痛点**：
- 首次运行等待时间长
- 需要额外工具 (7-Zip)
- 解压后占用 8GB+ 空间
- 不同系统可能不兼容（Windows 版本、CPU 架构）

#### 2.3.3 WebUI 核心文件打包

**打包内容** (`app.spec` 第 114-164 行)：

| 目录/文件 | 大小估算 | 说明 |
|----------|---------|------|
| `modules/` | ~20MB | WebUI 核心模块 (Python) |
| `scripts/` | ~1MB | 扩展脚本 |
| `javascript/` | ~500KB | 前端 JS |
| `html/` | ~200KB | 前端 HTML 模板 |
| `configs/` | ~100KB | 配置文件 |
| `extensions-builtin/` | ~5MB | 内置扩展 |
| `launch.py, webui.py` | ~50KB | 启动脚本 |
| `requirements*.txt` | ~10KB | 依赖列表 |

**排除内容**：
| 目录 | 排除原因 |
|-----|---------|
| `models/` | 模型文件 (5-50GB)，用户自行下载 |
| `outputs/` | 运行时生成 |
| `repositories/` | Git 子模块，体积大 (~1GB) |
| `venv/` | 单独处理（分离式打包） |
| `cache/`, `tmp/` | 临时文件 |

---

## 数据链路图

### 3.1 构建时数据流

```
┌───────────────────┐
│  源代码仓库       │
│  stable-diffusion-│
│  webui/           │
└─────┬─────────────┘
      │
      ├─────────────────────────────────────────┐
      │                                         │
      ▼                                         ▼
┌──────────────────┐                   ┌────────────────┐
│ desktop-app/     │                   │ venv/          │
│ ├── src/         │                   │ (Python 3.10)  │
│ ├── app.spec     │                   │ ├── torch      │
│ └── build.py     │                   │ ├── gradio     │
└─────┬────────────┘                   │ └── ...        │
      │                                 └────┬───────────┘
      │                                      │
      ▼                                      ▼
┌──────────────────┐              ┌─────────────────────┐
│ PyInstaller      │              │ 7z 压缩             │
│ + app.spec       │              │ create_environment_ │
│                  │              │ package.py          │
└─────┬────────────┘              └────┬────────────────┘
      │                                │
      │                                │
      ├────────────────────────────────┤
      │                                │
      ▼                                ▼
┌────────────────────────────────────────────────┐
│ dist/StableDiffusionWebUI/                     │
│ ├── StableDiffusionWebUI.exe (~50MB)           │
│ ├── _internal/ (~550MB)                        │
│ │   ├── PyQt6/ (~300MB)                        │
│ │   ├── modules/, scripts/, ... (~200MB)       │
│ │   └── 其他依赖 (~50MB)                       │
│ └── environment/                               │
│     └── venv.7z (~3-4GB)                       │
└────────────────────────────────────────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │ 分发到目标机器   │
          └──────────────────┘
```

### 3.2 运行时数据流

```
        用户双击 StableDiffusionWebUI.exe
                    │
                    ▼
        ┌───────────────────────┐
        │ 1. DLL 路径设置       │
        │    (main.py)          │
        └───────┬───────────────┘
                │
                ▼
        ┌───────────────────────┐
        │ 2. 环境检测/解压      │
        │    (environment_      │
        │     manager.py)       │
        │                       │
        │  首次运行:            │
        │  venv.7z → venv/      │
        │  (5-10分钟)           │
        └───────┬───────────────┘
                │
                ▼
        ┌───────────────────────┐
        │ 3. 启动 Qt 主窗口     │
        │    (MainWindow)       │
        └───────┬───────────────┘
                │
                ▼
        ┌───────────────────────┐
        │ 4. 启动 WebUI 服务器  │
        │    (ServerManager)    │
        │                       │
        │  venv/python.exe      │
        │  launch.py            │
        │  --port 7860          │
        └───────┬───────────────┘
                │
                │ subprocess
                │
                ▼
        ┌───────────────────────┐
        │ 5. WebUI 后端进程     │
        │    (Gradio Server)    │
        │                       │
        │  - 加载模型           │
        │  - 启动 HTTP 服务     │
        │  - 监听 127.0.0.1:7860│
        └───────┬───────────────┘
                │
                │ HTTP
                │
                ▼
        ┌───────────────────────┐
        │ 6. QWebEngineView     │
        │    加载 WebUI         │
        │                       │
        │  http://127.0.0.1:7860│
        └───────────────────────┘
                │
                ▼
        ┌───────────────────────┐
        │ 用户交互 (生成图像)   │
        └───────────────────────┘
```

### 3.3 依赖关系图

```
StableDiffusionWebUI.exe
│
├─ PyQt6 + Qt6 DLL
│  ├─ Qt6Core.dll
│  ├─ Qt6Gui.dll
│  ├─ Qt6WebEngineCore.dll
│  └─ 插件 (platforms, imageformats, ...)
│
├─ Python 环境 (venv/)
│  ├─ Python 3.10.x
│  ├─ torch (PyTorch)
│  ├─ gradio
│  ├─ transformers
│  └─ 其他 Python 包 (~2000个)
│
├─ WebUI 核心文件
│  ├─ launch.py, webui.py
│  ├─ modules/
│  ├─ scripts/
│  └─ javascript/, html/
│
└─ Stable Diffusion 模型 (用户提供)
   ├─ models/Stable-diffusion/*.safetensors
   └─ models/VAE, Lora, ...
```

---

## 痛点分析

### 4.1 痛点1: 首次运行体验差

**问题描述**：
- 用户双击 `.exe` 后，需要等待 5-10 分钟解压 Python 环境
- 解压过程无详细进度提示，用户体验差
- 解压失败率高（需要 7-Zip、磁盘空间不足等）

**影响**：
- ❌ 无法做到"真正的"开箱即用
- ❌ 用户流失率高（等待过程中可能放弃）
- ❌ 技术门槛：普通用户不知道如何安装 7-Zip

**根本原因**：
- venv 环境体积大 (8GB 解压后)
- PyInstaller 不适合打包完整 Python 环境

### 4.2 痛点2: 模型文件未整合

**问题描述**：
- Stable Diffusion 模型 (5-50GB) 完全未打包
- 用户需要：
  1. 手动下载模型（HuggingFace / Civitai）
  2. 放到正确目录 (`models/Stable-diffusion/`)
  3. 重启应用

**影响**：
- ❌ 技术门槛极高：普通用户不知道去哪下载模型
- ❌ 初次运行无法生成任何图像（报错）
- ❌ 与"桌面版"定位不符（桌面版应该简化操作）

**根本原因**：
- 模型文件版权问题（无法直接分发）
- 文件体积过大（单个模型 5-10GB）

### 4.3 痛点3: 依赖兼容性问题

**问题描述**：
- venv 环境在不同 Windows 版本可能不兼容
  - Python 编译版本不同
  - DLL 依赖 (MSVC Runtime, CUDA 版本)
- torch 版本固定，不支持新显卡

**影响**：
- ❌ 某些系统上无法运行（报 DLL 缺失错误）
- ❌ 新显卡用户性能差（用了旧版 CUDA）

**根本原因**：
- Python 环境不是跨系统的（编译依赖）
- 未动态检测硬件并安装合适版本

### 4.4 痛点4: 更新困难

**问题描述**：
- 每次 WebUI 更新，需要：
  1. 重新打包整个应用 (~5GB)
  2. 用户重新下载完整安装包
  3. 用户旧的输出、配置需要手动迁移

**影响**：
- ❌ 开发者维护成本高
- ❌ 用户更新体验差（重新下载 5GB）
- ❌ 无增量更新机制

**根本原因**：
- 整体打包策略，无模块化设计
- 未区分"核心应用" vs "WebUI 内容"

### 4.5 痛点5: 体积过大

**问题描述**：
- 当前打包产物：~4-5GB（不含模型）
  - 应用本身：~600MB
  - venv.7z：~3-4GB
- 加上模型：总计 10-50GB

**影响**：
- ❌ 下载时间长（网络慢的用户需数小时）
- ❌ 存储压力（用户需要 20GB+ 空闲空间）
- ❌ 分发成本高（CDN 流量费用）

**根本原因**：
- 打包了完整 Python 环境（包含不必要的包）
- 未压缩优化（DLL、Python 库）

### 4.6 痛点6: 缺少依赖检测和引导

**问题描述**：
- 应用假设用户已有：
  - Visual C++ Redistributable
  - 足够磁盘空间
  - 管理员权限（解压到 Program Files）
- 缺失依赖时，报错信息不友好

**影响**：
- ❌ 普通用户看到错误后不知道如何解决
- ❌ 支持成本高（大量"无法启动"的问题）

### 4.7 痛点总结表

| 痛点 | 严重程度 | 影响范围 | 解决难度 |
|-----|---------|---------|---------|
| 1. 首次运行体验差 | 🔴 高 | 所有用户 | 🟡 中 |
| 2. 模型文件未整合 | 🔴 高 | 所有用户 | 🔴 高 |
| 3. 依赖兼容性问题 | 🟡 中 | 部分用户 | 🟡 中 |
| 4. 更新困难 | 🟡 中 | 开发者+用户 | 🟢 低 |
| 5. 体积过大 | 🟢 低 | 网络慢用户 | 🟡 中 |
| 6. 缺少依赖检测 | 🟡 中 | 技术小白 | 🟢 低 |

---

## 重构方案

### 5.1 方案对比

| 方案 | 开箱即用 | 体积 | 兼容性 | 更新 | 开发成本 |
|-----|---------|------|-------|------|---------|
| **方案A: 完全内嵌** | ⭐⭐⭐⭐⭐ | 🔴 15-50GB | ⭐⭐⭐ | 🔴 困难 | 🟡 中 |
| **方案B: 在线下载** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **方案C: 混合打包** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 🟡 中 |
| **当前方案 (分离式)** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

### 5.2 推荐方案：混合打包 + 智能引导

#### 核心思想
1. **轻量级核心应用** (~200MB)：仅打包 PyQt6 + 桌面应用代码
2. **智能环境管理器**：首次运行检测并引导用户安装依赖
3. **模块化内容**：WebUI 内容、Python 环境、模型分离管理
4. **增量更新**：只更新变化的部分

#### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                  新架构: 混合打包方案                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  【打包产物】                                                │
│                                                              │
│  1. 核心启动器 (StableDiffusionDesktop.exe) - 200MB         │
│     ├── PyQt6 + WebEngine                                    │
│     ├── 智能引导模块                                         │
│     └── 下载/解压管理器                                      │
│                                                              │
│  2. 内容包 (可选下载)                                        │
│     ├── webui-core.zip (~50MB)                               │
│     │   └── modules/, scripts/, javascript/, ...            │
│     │                                                        │
│     ├── python-env-3.10-cpu.zip (~2GB)                       │
│     ├── python-env-3.10-cuda118.zip (~4GB)                   │
│     ├── python-env-3.10-cuda121.zip (~4GB)                   │
│     │                                                        │
│     └── models/ (引导下载)                                   │
│         ├── sd-v1-5.safetensors (4GB)                        │
│         └── sd-xl-base.safetensors (7GB)                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 5.2.1 智能引导流程

```python
# 新增：launcher.py (替代 main.py)

class SmartLauncher:
    def __init__(self):
        self.app_dir = Path(sys.executable).parent
        self.data_dir = self.app_dir / "data"  # 存放数据
        self.config = LauncherConfig()
    
    def check_and_setup_environment(self):
        """智能检测和设置环境"""
        
        # 1. 检测系统环境
        system_info = self.detect_system()
        # - OS 版本
        # - CUDA 可用性（nvidia-smi）
        # - 可用磁盘空间
        # - Visual C++ Runtime
        
        # 2. 检测 Python 环境
        if not self.check_python_env():
            # 显示引导界面
            env_type = self.show_env_selection_dialog(system_info)
            # - CPU Only (~2GB)
            # - CUDA 11.8 (~4GB)
            # - CUDA 12.1 (~4GB)
            
            # 下载/解压 Python 环境
            self.download_and_install_env(env_type, 
                progress_callback=self.update_progress)
        
        # 3. 检测 WebUI 核心文件
        if not self.check_webui_core():
            self.download_and_install_webui(
                progress_callback=self.update_progress)
        
        # 4. 检测模型文件
        if not self.check_models():
            # 显示模型选择界面
            models = self.show_model_selection_dialog()
            # - SD 1.5 (推荐, 4GB)
            # - SDXL (高质量, 7GB)
            # - 稍后手动下载
            
            if models:
                self.download_models(models,
                    progress_callback=self.update_progress)
        
        # 5. 验证完整性
        self.verify_installation()
        
        return True
```

#### 5.2.2 模块化目录结构

```
StableDiffusionDesktop/
├── StableDiffusionDesktop.exe      # 核心启动器 (200MB)
│
├── _internal/                       # PyInstaller 内部文件
│   └── PyQt6/                       # Qt DLL
│
├── data/                            # 数据目录 (用户可配置路径)
│   │
│   ├── python-env/                  # Python 环境
│   │   ├── python.exe
│   │   ├── Lib/
│   │   └── Scripts/
│   │
│   ├── webui/                       # WebUI 核心文件
│   │   ├── modules/
│   │   ├── scripts/
│   │   ├── javascript/
│   │   ├── launch.py
│   │   └── webui.py
│   │
│   ├── models/                      # 模型文件
│   │   ├── Stable-diffusion/
│   │   │   ├── sd_v1-5.safetensors (用户选择下载)
│   │   │   └── sdxl_base.safetensors
│   │   ├── VAE/
│   │   └── Lora/
│   │
│   ├── outputs/                     # 输出文件
│   │
│   └── config/                      # 配置文件
│       ├── app_config.json
│       └── webui_config.json
│
├── cache/                           # 缓存 (下载的安装包)
│   ├── webui-core-v1.7.0.zip
│   ├── python-env-cpu-v1.0.zip
│   └── sd_v1-5.safetensors.part
│
├── logs/                            # 日志
│
└── README.txt

```

#### 5.2.3 下载管理器

```python
# 新增：download_manager.py

class DownloadManager:
    """智能下载管理器"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.mirrors = self.load_mirrors()  # CDN 镜像列表
    
    def download_file(self, 
                      file_id: str,  # "python-env-cpu"
                      progress_callback: Callable = None,
                      verify_callback: Callable = None):
        """
        下载文件，支持：
        - 断点续传
        - 多线程下载
        - 镜像切换
        - MD5 校验
        """
        
        # 1. 获取下载信息
        download_info = self.get_download_info(file_id)
        # {
        #   "url": "https://cdn.example.com/python-env-cpu.zip",
        #   "mirrors": ["https://mirror1.com/...", ...],
        #   "size": 2147483648,
        #   "md5": "abc123...",
        # }
        
        # 2. 检查缓存
        cached_file = self.cache_dir / f"{file_id}.zip"
        if cached_file.exists():
            if self.verify_md5(cached_file, download_info["md5"]):
                return cached_file  # 已下载，直接返回
        
        # 3. 多线程下载
        self.download_with_resume(
            url=download_info["url"],
            output=cached_file,
            total_size=download_info["size"],
            progress_callback=progress_callback,
            mirrors=download_info["mirrors"]
        )
        
        # 4. 校验
        if not self.verify_md5(cached_file, download_info["md5"]):
            raise DownloadError("文件校验失败")
        
        return cached_file
    
    def extract_archive(self, archive_path: Path, 
                       target_dir: Path,
                       progress_callback: Callable = None):
        """
        智能解压，支持：
        - zip, 7z, tar.gz
        - 进度显示
        - 并行解压
        """
        pass
```

#### 5.2.4 引导 UI 界面

**首次启动流程**：

```
┌──────────────────────────────────────────────────────┐
│        欢迎使用 Stable Diffusion Desktop!             │
├──────────────────────────────────────────────────────┤
│                                                       │
│  检测到这是首次运行，需要下载以下组件：               │
│                                                       │
│  [✓] 核心应用                         已安装          │
│  [ ] Python 环境                      需要下载 2.1GB  │
│  [ ] WebUI 核心                       需要下载 45MB   │
│  [ ] Stable Diffusion 1.5 模型       需要下载 4.2GB  │
│                                                       │
│  ────────────────────────────────────────────────    │
│                                                       │
│  显卡: NVIDIA RTX 3060                                │
│  推荐: Python 环境 (CUDA 11.8)                        │
│  可用空间: 125GB / 500GB                              │
│                                                       │
│  ────────────────────────────────────────────────    │
│                                                       │
│  总下载大小: 6.3GB                                    │
│  预计时间: 15分钟 (50 Mbps)                          │
│                                                       │
│  [ 自定义 ]              [ 开始下载 ]  [ 稍后设置 ]  │
│                                                       │
└──────────────────────────────────────────────────────┘
```

**下载进度界面**：

```
┌──────────────────────────────────────────────────────┐
│        正在下载和安装组件...                          │
├──────────────────────────────────────────────────────┤
│                                                       │
│  当前: Python 环境 (CUDA 11.8)                        │
│  ████████████████░░░░░░░░░  65%  (1.4GB / 2.1GB)     │
│  速度: 8.5 MB/s    剩余时间: 约 2 分钟               │
│                                                       │
│  ────────────────────────────────────────────────    │
│                                                       │
│  已完成:                                              │
│  ✓ WebUI 核心 (45MB)                                 │
│                                                       │
│  等待中:                                              │
│  - Stable Diffusion 1.5 模型 (4.2GB)                 │
│                                                       │
│  ────────────────────────────────────────────────    │
│                                                       │
│  整体进度: 25%  (1.6GB / 6.3GB)                      │
│                                                       │
│  [ 暂停 ]  [ 取消 ]                                  │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### 5.3 方案实施细节

#### 5.3.1 Python 环境处理

**方案选择**：

| 方案 | 优点 | 缺点 | 推荐 |
|-----|------|------|------|
| 嵌入式 Python | 体积小 (~50MB) | 需要在线安装包 | ✅ 推荐 |
| Portable Python | 开箱即用 | 体积大 (~500MB) | ⚠️ 备选 |
| Conda 环境 | 环境隔离好 | 超大 (~5GB) | ❌ 不推荐 |

**推荐：嵌入式 Python + pip 在线安装**

```python
# 实现示例
class PythonEnvManager:
    def setup_portable_python(self, env_dir: Path):
        """设置 Portable Python 环境"""
        
        # 1. 下载 Python embeddable package
        # https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip
        python_zip = self.download_file(
            "python-3.10.11-embed-amd64.zip",
            progress_callback=self.update_progress
        )
        
        # 2. 解压到 env_dir
        self.extract_archive(python_zip, env_dir)
        
        # 3. 获取 pip（下载 get-pip.py）
        get_pip = self.download_file("get-pip.py")
        subprocess.run([
            str(env_dir / "python.exe"),
            str(get_pip),
            "--no-warn-script-location"
        ])
        
        # 4. 安装 WebUI 依赖
        requirements = self.data_dir / "webui" / "requirements_versions.txt"
        subprocess.run([
            str(env_dir / "Scripts" / "pip.exe"),
            "install", "-r", str(requirements),
            "--index-url", "https://pypi.tuna.tsinghua.edu.cn/simple"  # 使用国内镜像
        ])
        
        # 5. 根据硬件选择 PyTorch 版本
        if self.has_cuda():
            cuda_version = self.detect_cuda_version()  # 11.8 or 12.1
            torch_url = f"https://download.pytorch.org/whl/cu{cuda_version}"
            subprocess.run([
                str(env_dir / "Scripts" / "pip.exe"),
                "install", "torch", "torchvision",
                "--index-url", torch_url
            ])
        else:
            subprocess.run([
                str(env_dir / "Scripts" / "pip.exe"),
                "install", "torch", "torchvision",
                "--index-url", "https://download.pytorch.org/whl/cpu"
            ])
```

**优化点**：
1. 使用国内镜像加速下载（清华、阿里云）
2. 并行下载 PyPI 包
3. 缓存已下载的 wheel 文件
4. 提供"离线安装包"选项（预下载所有依赖）

#### 5.3.2 模型文件处理

**方案**：引导式下载 + 本地管理

```python
class ModelManager:
    """模型管理器"""
    
    # 预定义模型库
    AVAILABLE_MODELS = {
        "sd-v1-5": {
            "name": "Stable Diffusion 1.5",
            "description": "最经典的版本，速度快，适合入门",
            "size": "4.27 GB",
            "url": "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors",
            "mirrors": [
                "https://hf-mirror.com/...",  # 国内镜像
            ],
            "md5": "cc6cb27103417325ff94f52b7a5d2dde",
            "recommended": True,
        },
        "sdxl-base": {
            "name": "Stable Diffusion XL Base",
            "description": "更高质量，但速度较慢，需要更强显卡",
            "size": "6.94 GB",
            "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
            "md5": "...",
            "recommended": False,
            "requirements": {
                "vram": 10 * 1024,  # 10GB VRAM
            }
        },
        # ... 更多模型
    }
    
    def show_model_selection_ui(self):
        """显示模型选择界面"""
        
        dialog = ModelSelectionDialog()
        
        for model_id, info in self.AVAILABLE_MODELS.items():
            # 检查硬件要求
            can_run = self.check_model_requirements(info.get("requirements"))
            
            dialog.add_model(
                name=info["name"],
                description=info["description"],
                size=info["size"],
                recommended=info.get("recommended", False),
                enabled=can_run,
                reason="" if can_run else "显存不足"
            )
        
        selected_models = dialog.exec()
        return selected_models
    
    def download_model(self, model_id: str, progress_callback=None):
        """下载模型"""
        info = self.AVAILABLE_MODELS[model_id]
        
        # 使用 DownloadManager 下载
        model_file = self.download_manager.download_file(
            file_id=model_id,
            url=info["url"],
            mirrors=info.get("mirrors", []),
            md5=info["md5"],
            progress_callback=progress_callback
        )
        
        # 移动到模型目录
        target = self.models_dir / "Stable-diffusion" / model_file.name
        shutil.move(model_file, target)
        
        return target
```

**UI 设计**：

```
┌──────────────────────────────────────────────────────┐
│        选择要下载的模型                               │
├──────────────────────────────────────────────────────┤
│                                                       │
│  [✓] Stable Diffusion 1.5               (推荐)       │
│      最经典的版本，速度快，适合入门                   │
│      大小: 4.27 GB                                    │
│                                                       │
│  [ ] Stable Diffusion XL Base                        │
│      更高质量，但速度较慢                             │
│      大小: 6.94 GB                                    │
│      ⚠️  需要至少 10GB 显存 (您的显卡: 6GB)           │
│                                                       │
│  [ ] DreamShaper 8                                   │
│      社区微调版本，更真实的人像                       │
│      大小: 2.13 GB                                    │
│                                                       │
│  ────────────────────────────────────────────────    │
│                                                       │
│  💡 提示: 您也可以稍后手动下载模型并放入              │
│     data/models/Stable-diffusion/ 目录               │
│                                                       │
│  [ 全部跳过 ]           [ 确认下载 (4.27 GB) ]      │
│                                                       │
└──────────────────────────────────────────────────────┘
```

#### 5.3.3 更新机制

**增量更新方案**：

```python
class UpdateManager:
    """更新管理器"""
    
    def check_for_updates(self):
        """检查更新"""
        
        current_version = self.get_current_version()
        # {
        #   "app": "1.0.0",
        #   "webui": "1.7.0",
        #   "python-env": "1.0"
        # }
        
        # 从服务器获取最新版本信息
        latest_versions = self.fetch_latest_versions()
        
        updates_available = []
        
        # 检查各组件
        if latest_versions["app"] > current_version["app"]:
            updates_available.append({
                "component": "app",
                "current": current_version["app"],
                "latest": latest_versions["app"],
                "size": "50 MB",
                "changelog": "- 修复了启动器崩溃问题\n- 优化了下载速度"
            })
        
        if latest_versions["webui"] > current_version["webui"]:
            updates_available.append({
                "component": "webui",
                "current": current_version["webui"],
                "latest": latest_versions["webui"],
                "size": "15 MB",
                "changelog": "- 新增 ControlNet 支持\n- 修复了生成速度问题"
            })
        
        return updates_available
    
    def apply_update(self, component: str, progress_callback=None):
        """应用更新"""
        
        if component == "app":
            # 下载新的 exe
            new_exe = self.download_manager.download_file(
                f"app-{latest_version}.exe",
                progress_callback=progress_callback
            )
            
            # 使用自更新机制（启动新 exe，旧 exe 退出并被替换）
            self.apply_self_update(new_exe)
        
        elif component == "webui":
            # 下载 patch 文件
            patch = self.download_manager.download_file(
                f"webui-{current_version}-to-{latest_version}.patch.zip",
                progress_callback=progress_callback
            )
            
            # 应用 patch（只替换变化的文件）
            self.apply_patch(patch, self.webui_dir)
```

### 5.4 方案优势总结

| 特性 | 当前方案 | 新方案 | 改进 |
|-----|---------|--------|------|
| **首次启动时间** | 5-10分钟（解压） | 30秒（引导UI） | ⬆️ **10x** |
| **开箱即用** | ❌ 需要模型 | ⭐⭐⭐⭐ 引导下载 | ⬆️ **大幅提升** |
| **安装包大小** | 4-5GB | 200MB (核心) + 按需下载 | ⬇️ **20x** |
| **兼容性** | ⭐⭐⭐ 固定环境 | ⭐⭐⭐⭐⭐ 动态检测 | ⬆️ **提升** |
| **更新体验** | 重新下载 5GB | 增量更新 10-50MB | ⬆️ **100x** |
| **用户体验** | ⭐⭐ 技术门槛高 | ⭐⭐⭐⭐ 引导式 | ⬆️ **大幅提升** |
| **开发维护** | 🟡 中 | 🟢 低（模块化） | ⬆️ **提升** |

---

## 实施路线图

### 6.1 阶段划分

#### 🎯 阶段1: 核心重构 (2-3周)

**目标**：建立新的启动器架构

**任务清单**：

1. **重构启动器** (3天)
   - [ ] 创建 `launcher.py`，替代 `main.py`
   - [ ] 实现系统检测模块 (`system_detector.py`)
     - [ ] 检测 OS 版本
     - [ ] 检测 CUDA 可用性
     - [ ] 检测磁盘空间
     - [ ] 检测 VC++ Runtime
   - [ ] 实现配置管理 (`launcher_config.py`)

2. **下载管理器** (4天)
   - [ ] 实现基础下载功能 (`download_manager.py`)
     - [ ] HTTP 下载（requests）
     - [ ] 进度回调
     - [ ] MD5 校验
   - [ ] 实现高级功能
     - [ ] 断点续传
     - [ ] 多线程下载
     - [ ] 镜像切换
   - [ ] 实现解压功能
     - [ ] 支持 zip, 7z
     - [ ] 进度显示

3. **环境管理器重构** (3天)
   - [ ] 重写 `environment_manager.py`
     - [ ] 支持 Portable Python
     - [ ] 在线安装依赖
     - [ ] 根据硬件选择 PyTorch 版本
   - [ ] 添加环境验证
     - [ ] 检查 Python 版本
     - [ ] 检查必要包安装

4. **引导 UI** (4天)
   - [ ] 设计首次运行 UI (`first_run_wizard.py`)
     - [ ] 欢迎页面
     - [ ] 组件选择页面
     - [ ] 下载进度页面
     - [ ] 完成页面
   - [ ] 集成到主窗口

#### 🎯 阶段2: 模块化内容 (1-2周)

**目标**：分离 WebUI 内容和模型管理

**任务清单**：

1. **模型管理器** (3天)
   - [ ] 创建 `model_manager.py`
   - [ ] 定义模型库（JSON配置）
   - [ ] 实现模型选择 UI
   - [ ] 集成到首次运行向导

2. **WebUI 内容管理** (2天)
   - [ ] 修改 `app.spec`，排除 WebUI 核心文件
   - [ ] 创建 `webui_manager.py`
   - [ ] 实现 WebUI 下载和解压
   - [ ] 版本管理

3. **模块化打包** (2天)
   - [ ] 修改 `build.py`，生成核心启动器
   - [ ] 创建内容包构建脚本
     - [ ] `build_webui_package.py`
     - [ ] `build_python_env.py`
   - [ ] 测试打包流程

#### 🎯 阶段3: 更新机制 (1周)

**目标**：实现增量更新

**任务清单**：

1. **更新检查** (2天)
   - [ ] 创建 `update_manager.py`
   - [ ] 实现版本比对逻辑
   - [ ] 设计更新 API（服务端）

2. **更新应用** (2天)
   - [ ] 实现自更新机制（替换 exe）
   - [ ] 实现 patch 应用逻辑
   - [ ] 添加回滚功能

3. **更新 UI** (1天)
   - [ ] 创建更新提示对话框
   - [ ] 创建更新进度界面

#### 🎯 阶段4: 优化和测试 (1-2周)

**目标**：性能优化和兼容性测试

**任务清单**：

1. **性能优化** (3天)
   - [ ] 优化下载速度（多线程、CDN）
   - [ ] 优化解压速度（并行）
   - [ ] 减少启动时间

2. **兼容性测试** (3天)
   - [ ] 测试不同 Windows 版本
     - [ ] Windows 10 (1809, 1903, 21H2)
     - [ ] Windows 11
   - [ ] 测试不同硬件配置
     - [ ] NVIDIA GPU (不同 CUDA 版本)
     - [ ] AMD GPU
     - [ ] CPU only
   - [ ] 测试网络环境
     - [ ] 国内网络
     - [ ] 国际网络
     - [ ] 离线模式

3. **用户测试** (2天)
   - [ ] 招募 Beta 测试者
   - [ ] 收集反馈
   - [ ] 修复 Bug

4. **文档编写** (2天)
   - [ ] 用户手册
   - [ ] 开发者文档
   - [ ] 故障排除指南

### 6.2 里程碑

| 里程碑 | 预计完成时间 | 交付物 |
|-------|------------|--------|
| M1: 核心重构完成 | 第3周 | 可运行的新启动器 |
| M2: 模块化内容完成 | 第5周 | 模型和 WebUI 分离管理 |
| M3: 更新机制完成 | 第6周 | 支持增量更新 |
| M4: Beta 版本 | 第8周 | 可对外测试的版本 |
| M5: 正式版本 | 第10周 | v2.0 正式发布 |

### 6.3 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|-----|------|------|---------|
| 网络下载不稳定 | 🟡 中 | 🔴 高 | 多镜像 + 断点续传 |
| Python 环境兼容性 | 🟢 低 | 🔴 高 | 动态检测 + 多版本支持 |
| 模型下载慢 | 🔴 高 | 🟡 中 | 国内镜像 + P2P 下载 |
| 用户不接受首次等待 | 🟡 中 | 🟡 中 | 优化 UI + 后台下载 |
| 开发时间超期 | 🟡 中 | 🟡 中 | 分阶段交付 + MVP 优先 |

---

## 附录

### A. 关键代码示例

#### A.1 系统检测

```python
# system_detector.py

import subprocess
import shutil
import platform
from pathlib import Path
from typing import Optional, Dict

class SystemDetector:
    """系统信息检测器"""
    
    @staticmethod
    def detect_all() -> Dict:
        """检测所有系统信息"""
        return {
            "os": SystemDetector.detect_os(),
            "gpu": SystemDetector.detect_gpu(),
            "disk": SystemDetector.detect_disk_space(),
            "runtime": SystemDetector.detect_runtime(),
        }
    
    @staticmethod
    def detect_os() -> Dict:
        """检测操作系统"""
        return {
            "system": platform.system(),  # Windows
            "release": platform.release(),  # 10
            "version": platform.version(),  # 10.0.19041
            "machine": platform.machine(),  # AMD64
            "processor": platform.processor(),
        }
    
    @staticmethod
    def detect_gpu() -> Dict:
        """检测 GPU 信息"""
        gpu_info = {
            "vendor": None,  # NVIDIA, AMD, Intel
            "name": None,
            "vram": None,  # MB
            "cuda_available": False,
            "cuda_version": None,
        }
        
        # 尝试检测 NVIDIA GPU
        if shutil.which("nvidia-smi"):
            try:
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if lines:
                        parts = lines[0].split(', ')
                        gpu_info["vendor"] = "NVIDIA"
                        gpu_info["name"] = parts[0]
                        gpu_info["vram"] = int(parts[1].split()[0])  # "12288 MiB" -> 12288
                        gpu_info["cuda_available"] = True
                        
                        # 检测 CUDA 版本
                        cuda_result = subprocess.run(
                            ["nvidia-smi"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        # 解析 "CUDA Version: 12.1"
                        import re
                        match = re.search(r'CUDA Version: ([\d.]+)', cuda_result.stdout)
                        if match:
                            gpu_info["cuda_version"] = match.group(1)
            except Exception:
                pass
        
        # TODO: 检测 AMD GPU (rocm-smi)
        # TODO: 检测 Intel GPU
        
        return gpu_info
    
    @staticmethod
    def detect_disk_space(path: Optional[Path] = None) -> Dict:
        """检测磁盘空间"""
        if path is None:
            path = Path.cwd()
        
        import shutil
        usage = shutil.disk_usage(path)
        
        return {
            "total": usage.total,  # bytes
            "used": usage.used,
            "free": usage.free,
            "total_gb": usage.total / (1024**3),
            "free_gb": usage.free / (1024**3),
        }
    
    @staticmethod
    def detect_runtime() -> Dict:
        """检测运行时依赖"""
        runtime_info = {
            "vcredist_installed": False,
            "dotnet_installed": False,
        }
        
        # 检测 VC++ Redistributable（检查注册表）
        try:
            import winreg
            key_paths = [
                r"SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64",
                r"SOFTWARE\\WOW6432Node\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64",
            ]
            for key_path in key_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    runtime_info["vcredist_installed"] = True
                    winreg.CloseKey(key)
                    break
                except FileNotFoundError:
                    continue
        except Exception:
            pass
        
        return runtime_info
```

#### A.2 首次运行向导

```python
# first_run_wizard.py

from PyQt6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QLabel,
    QCheckBox, QProgressBar, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread

class FirstRunWizard(QWizard):
    """首次运行向导"""
    
    def __init__(self, system_info: Dict, parent=None):
        super().__init__(parent)
        self.system_info = system_info
        self.setWindowTitle("首次运行设置")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(600, 500)
        
        # 添加页面
        self.addPage(WelcomePage(system_info))
        self.addPage(ComponentSelectionPage(system_info))
        self.addPage(DownloadPage())
        self.addPage(CompletePage())
    
    def get_selected_components(self) -> Dict:
        """获取用户选择的组件"""
        page = self.page(1)  # ComponentSelectionPage
        return page.get_selections()


class WelcomePage(QWizardPage):
    """欢迎页面"""
    
    def __init__(self, system_info: Dict, parent=None):
        super().__init__(parent)
        self.setTitle("欢迎使用 Stable Diffusion Desktop")
        self.setSubTitle("首次运行需要下载必要的组件")
        
        layout = QVBoxLayout(self)
        
        # 系统信息
        info_text = f"""
检测到您的系统信息：

操作系统: {system_info['os']['system']} {system_info['os']['release']}
显卡: {system_info['gpu']['name'] or '未检测到独立显卡'}
显存: {system_info['gpu']['vram'] or 0} MB
可用空间: {system_info['disk']['free_gb']:.1f} GB

根据您的配置，我们将推荐合适的组件。
"""
        
        info_label = QLabel(info_text)
        layout.addWidget(info_label)


class ComponentSelectionPage(QWizardPage):
    """组件选择页面"""
    
    def __init__(self, system_info: Dict, parent=None):
        super().__init__(parent)
        self.setTitle("选择要安装的组件")
        
        layout = QVBoxLayout(self)
        
        # Python 环境选择
        self.env_group = QGroupBox("Python 环境")
        env_layout = QVBoxLayout()
        
        if system_info['gpu']['cuda_available']:
            cuda_ver = system_info['gpu']['cuda_version'] or "12.1"
            if cuda_ver.startswith("11"):
                recommended_env = "cuda118"
            else:
                recommended_env = "cuda121"
            
            self.env_cuda = QRadioButton(f"CUDA {cuda_ver} 版本 (推荐，~4GB)")
            self.env_cuda.setChecked(True)
        else:
            recommended_env = "cpu"
            self.env_cpu = QRadioButton("CPU 版本 (~2GB)")
            self.env_cpu.setChecked(True)
        
        env_layout.addWidget(self.env_cuda if system_info['gpu']['cuda_available'] else self.env_cpu)
        self.env_group.setLayout(env_layout)
        layout.addWidget(self.env_group)
        
        # WebUI 核心（必选）
        self.webui_checkbox = QCheckBox("WebUI 核心文件 (必需，~50MB)")
        self.webui_checkbox.setChecked(True)
        self.webui_checkbox.setEnabled(False)
        layout.addWidget(self.webui_checkbox)
        
        # 模型选择
        self.model_group = QGroupBox("模型文件")
        model_layout = QVBoxLayout()
        
        self.model_sd15 = QCheckBox("Stable Diffusion 1.5 (推荐，4.27GB)")
        self.model_sd15.setChecked(True)
        model_layout.addWidget(self.model_sd15)
        
        # 根据显存决定是否启用 SDXL
        vram = system_info['gpu']['vram'] or 0
        self.model_sdxl = QCheckBox("Stable Diffusion XL (6.94GB)")
        if vram < 10 * 1024:  # 小于 10GB
            self.model_sdxl.setEnabled(False)
            self.model_sdxl.setToolTip("需要至少 10GB 显存")
        model_layout.addWidget(self.model_sdxl)
        
        self.model_group.setLayout(model_layout)
        layout.addWidget(self.model_group)
        
        # 总计大小
        self.size_label = QLabel()
        self.update_total_size()
        layout.addWidget(self.size_label)
        
        # 连接信号
        self.model_sd15.stateChanged.connect(self.update_total_size)
        self.model_sdxl.stateChanged.connect(self.update_total_size)
    
    def update_total_size(self):
        """更新总下载大小"""
        total_size = 0.05  # WebUI 核心 50MB
        total_size += 4.0 if self.env_cuda.isChecked() else 2.0  # Python 环境
        
        if self.model_sd15.isChecked():
            total_size += 4.27
        if self.model_sdxl.isChecked() and self.model_sdxl.isEnabled():
            total_size += 6.94
        
        self.size_label.setText(f"总下载大小: {total_size:.2f} GB")
    
    def get_selections(self) -> Dict:
        """获取选择结果"""
        return {
            "python_env": "cuda118" if self.env_cuda.isChecked() else "cpu",
            "webui_core": True,
            "models": {
                "sd-v1-5": self.model_sd15.isChecked(),
                "sdxl-base": self.model_sdxl.isChecked() and self.model_sdxl.isEnabled(),
            }
        }


class DownloadPage(QWizardPage):
    """下载进度页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("正在下载和安装")
        self.setSubTitle("请耐心等待...")
        
        layout = QVBoxLayout(self)
        
        # 当前任务
        self.current_label = QLabel("准备中...")
        layout.addWidget(self.current_label)
        
        # 当前进度条
        self.current_progress = QProgressBar()
        layout.addWidget(self.current_progress)
        
        # 速度和剩余时间
        self.speed_label = QLabel("")
        layout.addWidget(self.speed_label)
        
        # 日志
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # 整体进度
        self.overall_progress = QProgressBar()
        layout.addWidget(QLabel("整体进度:"))
        layout.addWidget(self.overall_progress)
    
    def initializePage(self):
        """页面初始化时开始下载"""
        selections = self.wizard().get_selected_components()
        
        # 创建下载线程
        self.download_thread = DownloadThread(selections)
        self.download_thread.progress_updated.connect(self.on_progress_updated)
        self.download_thread.log_message.connect(self.on_log_message)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()
    
    def on_progress_updated(self, current: int, total: int, task: str):
        """更新进度"""
        self.current_label.setText(f"当前: {task}")
        self.current_progress.setMaximum(total)
        self.current_progress.setValue(current)
        # TODO: 计算速度和剩余时间
    
    def on_log_message(self, message: str):
        """添加日志"""
        self.log_text.append(message)
    
    def on_download_finished(self, success: bool):
        """下载完成"""
        if success:
            self.wizard().next()
        else:
            # 显示错误
            pass


class DownloadThread(QThread):
    """下载线程"""
    
    progress_updated = pyqtSignal(int, int, str)  # current, total, task_name
    log_message = pyqtSignal(str)
    finished = pyqtSignal(bool)  # success
    
    def __init__(self, selections: Dict):
        super().__init__()
        self.selections = selections
    
    def run(self):
        """执行下载"""
        try:
            from download_manager import DownloadManager
            from environment_manager import PythonEnvManager
            from model_manager import ModelManager
            
            dm = DownloadManager()
            
            # 1. 下载 Python 环境
            self.log_message.emit("开始下载 Python 环境...")
            env_type = self.selections["python_env"]
            dm.download_and_install_env(
                env_type,
                progress_callback=lambda c, t: self.progress_updated.emit(c, t, f"Python 环境 ({env_type})")
            )
            
            # 2. 下载 WebUI 核心
            self.log_message.emit("开始下载 WebUI 核心...")
            dm.download_and_install_webui(
                progress_callback=lambda c, t: self.progress_updated.emit(c, t, "WebUI 核心")
            )
            
            # 3. 下载模型
            for model_id, selected in self.selections["models"].items():
                if selected:
                    self.log_message.emit(f"开始下载模型: {model_id}...")
                    mm = ModelManager()
                    mm.download_model(
                        model_id,
                        progress_callback=lambda c, t: self.progress_updated.emit(c, t, f"模型 ({model_id})")
                    )
            
            self.log_message.emit("✓ 所有组件下载完成！")
            self.finished.emit(True)
        except Exception as e:
            self.log_message.emit(f"✗ 错误: {e}")
            self.finished.emit(False)


class CompletePage(QWizardPage):
    """完成页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("安装完成")
        self.setSubTitle("您现在可以开始使用 Stable Diffusion Desktop 了！")
        
        layout = QVBoxLayout(self)
        
        complete_text = """
✓ 所有组件已成功安装

您可以：
1. 点击"完成"按钮启动应用
2. 在主界面开始生成图像
3. 在设置中调整参数

提示：
- 首次生成图像可能需要较长时间（加载模型）
- 您可以随时在设置中下载更多模型
"""
        
        label = QLabel(complete_text)
        layout.addWidget(label)
```

### B. 配置文件示例

#### B.1 组件配置 (components.json)

```json
{
  "version": "1.0",
  "components": {
    "python-env": {
      "cpu": {
        "version": "1.0.0",
        "size": 2147483648,
        "url": "https://cdn.example.com/python-env-3.10-cpu-v1.0.0.zip",
        "mirrors": [
          "https://mirror1.com/python-env-3.10-cpu-v1.0.0.zip",
          "https://mirror2.com/python-env-3.10-cpu-v1.0.0.zip"
        ],
        "md5": "abc123def456...",
        "requirements": {
          "disk_space": 5368709120
        }
      },
      "cuda118": {
        "version": "1.0.0",
        "size": 4294967296,
        "url": "https://cdn.example.com/python-env-3.10-cuda118-v1.0.0.zip",
        "md5": "def789ghi012...",
        "requirements": {
          "disk_space": 10737418240,
          "cuda_version": "11.x"
        }
      },
      "cuda121": {
        "version": "1.0.0",
        "size": 4294967296,
        "url": "https://cdn.example.com/python-env-3.10-cuda121-v1.0.0.zip",
        "md5": "ghi345jkl678...",
        "requirements": {
          "disk_space": 10737418240,
          "cuda_version": "12.x"
        }
      }
    },
    "webui-core": {
      "version": "1.7.0",
      "size": 52428800,
      "url": "https://cdn.example.com/webui-core-v1.7.0.zip",
      "mirrors": [
        "https://mirror1.com/webui-core-v1.7.0.zip"
      ],
      "md5": "jkl901mno234...",
      "changelog": "- 新增 ControlNet 支持\n- 优化启动速度\n- 修复已知 Bug"
    }
  },
  "models": {
    "sd-v1-5": {
      "name": "Stable Diffusion 1.5",
      "version": "1.5",
      "size": 4294967296,
      "url": "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors",
      "mirrors": [
        "https://hf-mirror.com/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
      ],
      "md5": "cc6cb27103417325ff94f52b7a5d2dde",
      "recommended": true,
      "requirements": {
        "vram": 4294967296
      }
    },
    "sdxl-base": {
      "name": "Stable Diffusion XL Base",
      "version": "1.0",
      "size": 6979321856,
      "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
      "mirrors": [
        "https://hf-mirror.com/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
      ],
      "md5": "...",
      "recommended": false,
      "requirements": {
        "vram": 10737418240
      }
    }
  }
}
```

---

## 总结

本文档全面分析了当前 Stable Diffusion WebUI 桌面版的架构、数据链路和核心痛点，并提供了详细的重构方案。

### 核心要点

1. **当前架构**：PyQt6 + PyInstaller + 分离式环境打包
2. **主要痛点**：无法真正开箱即用，首次运行体验差
3. **推荐方案**：混合打包 + 智能引导 + 模块化内容管理
4. **预期改进**：
   - 首次启动时间：5-10分钟 → 30秒
   - 安装包大小：4-5GB → 200MB (核心)
   - 更新方式：重新下载 5GB → 增量更新 10-50MB
   - 用户体验：技术门槛高 → 引导式简化

### 下一步行动

1. ✅ 评审此文档并达成共识
2. 🚀 启动阶段1开发（核心重构）
3. 📊 跟踪进度和里程碑
4. 🧪 持续测试和优化

---

**文档维护**：
- 作者：AI Assistant
- 最后更新：2024-12-10
- 状态：初稿待审核

