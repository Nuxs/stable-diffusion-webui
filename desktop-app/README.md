# Stable Diffusion WebUI 桌面版

<div align="center">

**一键安装、开箱即用的 AI 图像生成桌面应用**

[![版本](https://img.shields.io/badge/version-2.0.0-blue.svg)](CHANGELOG.md)
[![许可证](https://img.shields.io/badge/license-AGPL--3.0-green.svg)](LICENSE.txt)
[![平台](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](#系统要求)

[功能特点](#功能特点) • [快速开始](#快速开始) • [系统要求](#系统要求) • [文档](#文档) • [常见问题](#常见问题)

</div>

---

## 功能特点

✨ **智能引导** - 首次运行自动检测系统配置，引导安装必要组件  
🚀 **快速启动** - 优化的启动流程，30秒内完成启动  
📦 **轻量打包** - 核心应用仅 200MB，按需下载所需组件  
🔄 **增量更新** - 支持组件独立更新，无需重新下载完整包  
🎨 **完整功能** - 基于 AUTOMATIC1111 的 Stable Diffusion WebUI，支持所有核心功能  
💻 **跨硬件** - 自动适配 CPU/NVIDIA GPU，智能推荐最佳配置

---

## 快速开始

### 用户版（推荐）

1. **下载安装包**
   - 从 [Releases](../../releases) 页面下载最新版 `StableDiffusionDesktop.exe`

2. **运行应用**
   - 双击 `StableDiffusionDesktop.exe`
   - 首次运行会启动设置向导

3. **跟随向导**
   - ✅ 查看系统信息
   - 🔧 选择 Python 环境（自动推荐）
   - 📥 选择要下载的 AI 模型
   - ⏱️ 等待下载完成（2-6 GB，取决于选择）

4. **开始创作**
   - 向导完成后自动打开 WebUI
   - 在提示词框输入描述，点击"生成"

### 开发者版

详见 [BUILD_GUIDE.md](BUILD_GUIDE.md)

---

## 系统要求

### 最低配置

| 项目 | 要求 |
|------|------|
| **操作系统** | Windows 10/11 (64位) |
| **内存** | 8 GB RAM |
| **存储空间** | 10 GB 可用空间 |
| **网络** | 稳定的互联网连接（首次安装） |
| **其他** | Visual C++ Redistributable 2015-2022 |

### 推荐配置

| 项目 | 配置 |
|------|------|
| **显卡** | NVIDIA GPU with 4GB+ VRAM |
| **处理器** | Intel i5 或同等级别 |
| **存储空间** | 20 GB 可用空间（包含模型） |
| **CUDA** | 11.8 或 12.1 |

> **💡 提示**: 
> - 没有独立显卡也可以使用，但生成速度会较慢（使用 CPU 模式）
> - 推荐使用 SSD 以获得更好的性能

---

## 使用指南

### 基础操作

1. **生成图像**
   ```
   在 Prompt（提示词）框输入描述 → 点击"Generate"（生成）
   ```

2. **调整参数**
   - **采样步数** (Sampling steps): 20-30 适合大多数情况
   - **宽度/高度** (Width/Height): 512x512 或 768x768
   - **CFG Scale**: 7-12，控制提示词的影响程度

3. **查看输出**
   - 生成的图像保存在 `data/outputs/txt2img-images/` 目录

### 高级功能

- **图生图** (img2img): 基于参考图像生成新图像
- **局部重绘** (Inpaint): 修改图像的特定区域
- **ControlNet**: 精确控制图像生成（需安装扩展）
- **Lora**: 使用微调模型改变风格

详细教程请参阅 [USER_GUIDE.md](USER_GUIDE.md)

---

## 项目结构

```
desktop-app/
├── 📄 README.md                    # 本文档
├── 📄 BUILD_GUIDE.md               # 开发者构建指南
├── 📄 USER_GUIDE.md                # 用户使用指南
├── 📄 CHANGELOG.md                 # 变更日志
├── 📄 ARCHITECTURE_ANALYSIS.md     # 架构分析文档
│
├── 🔧 build.py                     # 构建脚本
├── 🔧 app.spec                     # PyInstaller 配置
├── 📋 requirements.txt             # Python 依赖
│
├── 📁 src/                         # 源代码
│   ├── launcher.py                 # 智能启动器（主入口）
│   ├── main_window.py              # 主窗口
│   ├── server_manager.py           # 服务器管理
│   ├── system_detector.py          # 系统检测
│   ├── download_manager.py         # 下载管理
│   ├── model_manager.py            # 模型管理
│   ├── first_run_wizard.py         # 首次运行向导
│   ├── update_manager.py           # 更新管理
│   └── utils/                      # 工具模块
│       ├── config.py               # 配置管理
│       ├── logger.py               # 日志系统
│       └── portable_python.py      # Python 环境管理
│
├── 📁 config/                      # 配置文件
│   └── components.json             # 组件下载配置
│
└── 📁 resources/                   # 资源文件
    └── icon.ico                    # 应用图标
```

---

## 运行时数据布局与环境解析

- `desktop-app/data/python-env/`：由首次运行向导通过 `PortablePythonManager` 下载并配置的 Python 3.10 环境，包含 pip 与所有 WebUI 依赖。
- `desktop-app/data/webui/`：`WebUIManager` 解包后的核心代码目录，始终保持与组件配置一致的版本。
- `desktop-app/data/runtime_state.json`：`FirstRunWizard` 写入的运行时描述（Python 环境类型、路径、已装模型等），后续由 `ServerManager` 读取。

流程概览：
1. `launcher.py`/`SmartLauncher` 创建 `data/` 目录并在首次运行时触发向导。
2. 向导完成后会在 `runtime_state.json` 中写入 `python_env` 与 `webui` 信息，并更新 `Config.webui_project_path`。
3. `ServerManager` 启动前实例化 `EnvironmentManager`，按 `runtime_state → data/python-env → 项目 venv → 系统 Python` 的顺序解析 Python 3.10 解释器。
4. 校验成功后，`ServerManager` 使用解析出的解释器与下载好的 WebUI 目录启动 `launch.py`/`webui.py`。

> 📌 这样即可保持瘦客户端，仅在用户侧下载所需组件，同时保证启动器与运行时环境的一致性。

---

## 文档索引

- **用户文档**
  - [用户使用指南](USER_GUIDE.md) - 详细的使用教程
  - [常见问题](USER_GUIDE.md#常见问题) - FAQ 和故障排除
  - [更新日志](CHANGELOG.md) - 版本历史和变更记录

- **开发者文档**
  - [构建指南](BUILD_GUIDE.md) - 如何构建和打包应用
  - [架构文档](ARCHITECTURE_ANALYSIS.md) - 系统架构和设计决策
  - [重构总结](REFACTORING_SUMMARY.md) - 重构过程和进度

---

## 常见问题

### Q: 首次下载需要多长时间？
**A**: 取决于您的网络速度和选择的组件：
- 仅 CPU 环境：约 2 GB，10-20 分钟
- CUDA 环境 + SD 1.5 模型：约 8 GB，30-60 分钟
- 包含 SDXL 模型：约 15 GB，60-120 分钟

### Q: 可以更换模型吗？
**A**: 可以！将 `.safetensors` 或 `.ckpt` 模型文件放入 `data/models/Stable-diffusion/` 目录，重启应用即可。

### Q: 生成图像很慢怎么办？
**A**: 
- 确保使用了 CUDA 版本（如果有 NVIDIA 显卡）
- 降低分辨率（如 512x512）
- 减少采样步数（20-30）
- 关闭不必要的扩展

### Q: 如何更新应用？
**A**: 应用会自动检查更新并提示。也可以手动下载最新版本覆盖安装。

### Q: 在哪里可以找到生成的图像？
**A**: 默认保存在 `data/outputs/txt2img-images/` 目录。

更多问题请查阅 [USER_GUIDE.md](USER_GUIDE.md) 或提交 Issue。

---

## 技术栈

- **UI 框架**: PyQt6 + WebEngine
- **后端**: Gradio (Stable Diffusion WebUI)
- **打包**: PyInstaller
- **AI 模型**: Stable Diffusion 1.5 / SDXL
- **语言**: Python 3.10

---

## 许可证

本项目基于 [AGPL-3.0 许可证](../LICENSE.txt)。

使用的第三方项目：
- [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) - AGPL-3.0
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GPL v3

---

## 贡献

欢迎贡献代码、报告问题或提出建议！

- 🐛 [报告 Bug](../../issues/new?template=bug_report.md)
- 💡 [功能建议](../../issues/new?template=feature_request.md)
- 📖 [改进文档](../../issues/new?labels=documentation)

---

## 致谢

- [AUTOMATIC1111](https://github.com/AUTOMATIC1111) - Stable Diffusion WebUI 的原作者
- [Stability AI](https://stability.ai/) - Stable Diffusion 模型
- 所有为开源社区做出贡献的开发者

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给个 Star！**

[返回顶部](#stable-diffusion-webui-桌面版)

</div>
