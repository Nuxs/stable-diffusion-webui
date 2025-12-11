# Stable Diffusion WebUI Desktop

一键安装、开箱即用的 Stable Diffusion WebUI 桌面应用

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
[![License](https://img.shields.io/badge/license-AGPL--3.0-green.svg)](LICENSE.txt)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey.svg)](https://www.microsoft.com/windows)

---

## 📋 简介

将强大的 [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) 打包为独立的 Windows 桌面应用，采用**智能引导**设计，真正实现**开箱即用**。

### ✨ 核心特性

- 🚀 **智能引导**：首次运行自动检测系统配置并推荐最佳设置
- 💻 **轻量安装**：核心应用仅 200MB，组件按需下载
- 🎯 **开箱即用**：自动管理 Python 环境和依赖，无需手动配置
- 🖥️ **现代界面**：内置 PyQt6 WebView，无需打开浏览器
- 📦 **模型管理**：内置模型库，一键下载主流 SD 模型
- 🔄 **增量更新**：支持组件独立更新，无需重新下载完整安装包
- ⚙️ **自动适配**：根据 GPU 自动选择 CUDA 版本（11.8 / 12.1 / CPU）

---

## 🎯 快速开始

### 用户版（推荐）

1. **下载应用**
   ```
   下载 StableDiffusionDesktop.exe（约 200MB）
   ```

2. **首次运行**
   - 双击 `StableDiffusionDesktop.exe`
   - 应用会自动检测您的系统配置
   - 跟随向导选择要下载的组件：
     - Python 环境（CPU 2GB / CUDA 11.8 4GB / CUDA 12.1 4GB）
     - AI 模型（Stable Diffusion 1.5 / SDXL 等）
   - 后台自动下载和安装（约 5-15 分钟）

3. **开始使用**
   - 安装完成后自动启动
   - 在主界面开始生成 AI 图像
   - 享受创作！

### 开发者版

详见 [BUILD_GUIDE.md](BUILD_GUIDE.md)

---

## 💡 系统要求

### 最低要求

| 项目 | 要求 |
|-----|------|
| **操作系统** | Windows 10 (64位) 或更高 |
| **磁盘空间** | 至少 10 GB 可用空间 |
| **内存** | 8 GB RAM（推荐 16 GB） |
| **运行时** | Visual C++ Redistributable 2015-2022 [下载](https://aka.ms/vs/17/release/vc_redist.x64.exe) |

### 推荐配置

| 组件 | 推荐配置 | 说明 |
|-----|---------|------|
| **显卡** | NVIDIA GPU with 4GB+ VRAM | 用于GPU加速，显著提升生成速度 |
| **CPU模式** | Intel i5 / AMD Ryzen 5 或更高 | 无GPU时使用CPU生成（速度较慢） |

### 支持的显卡

- ✅ **NVIDIA**：GTX 10 系列及以上（推荐 RTX 系列）
- ⚠️ **AMD**：暂不支持（未来可能支持 ROCm）
- ⚠️ **Intel**：仅 CPU 模式

---

## 📖 使用指南

### 首次运行流程

```
启动应用
   ↓
系统检测（GPU/CUDA/磁盘）
   ↓
选择组件
   ├─ Python 环境（自动推荐）
   ├─ AI 模型（可选）
   └─ 后台下载
   ↓
自动安装和配置
   ↓
启动主界面
```

### 主要功能

#### 1. 生成图像
- 输入文本提示词（Prompt）
- 调整参数（尺寸、步数、引导系数等）
- 点击生成按钮
- 等待 AI 创作（首次加载模型需要时间）

#### 2. 模型管理
- 菜单 → 设置 → 模型管理
- 浏览内置模型库
- 一键下载新模型
- 切换不同风格的模型

#### 3. 高级设置
- ControlNet（精确控制）
- Lora（微调模型）
- 图生图（Image-to-Image）
- 局部重绘（Inpainting）

### 常见操作

| 操作 | 快捷键 / 方法 |
|-----|--------------|
| 重新加载页面 | `F5` 或菜单 → 视图 → 重新加载 |
| 在浏览器中打开 | `Ctrl+B` 或工具栏按钮 |
| 放大界面 | `Ctrl++` |
| 缩小界面 | `Ctrl+-` |
| 重置缩放 | `Ctrl+0` |
| 退出应用 | `Ctrl+Q` 或菜单 → 文件 → 退出 |

---

## 📂 文件结构

```
StableDiffusionDesktop/          # 应用根目录
├── StableDiffusionDesktop.exe   # 主程序（200MB）
├── _internal/                    # 内部文件（PyQt6 等）
│   ├── PyQt6/                    # Qt 框架
│   ├── config/                   # 配置文件
│   └── ...
├── data/                         # 运行时数据（首次运行后创建）
│   ├── python-env/               # Python 环境（2-4 GB）
│   ├── webui/                    # WebUI 核心文件（~50MB）
│   ├── models/                   # AI 模型文件（4-10+ GB）
│   │   └── Stable-diffusion/
│   │       ├── v1-5-pruned-emaonly.safetensors
│   │       └── ...
│   ├── outputs/                  # 生成的图像
│   └── config/                   # 用户配置
├── cache/                        # 下载缓存
└── logs/                         # 日志文件
```

---

## ❓ 常见问题

### Q: 首次运行需要多长时间？
**A:** 取决于您选择的组件和网络速度：
- 核心应用启动：约 30 秒
- 下载 Python 环境：约 5-10 分钟（2-4 GB）
- 下载 AI 模型：约 5-15 分钟（4-10 GB）
- 总计：约 10-25 分钟

### Q: 可以离线使用吗？
**A:** 首次安装需要联网下载组件。安装完成后，可以离线使用。

### Q: 显存不足怎么办？
**A:** 
- 降低生成图像的尺寸（512x512）
- 减少批次数量
- 启用低显存优化（设置中）
- 使用 CPU 模式（速度较慢）

### Q: 如何更新应用？
**A:** 
- 应用会自动检测更新
- 菜单 → 帮助 → 检查更新
- 只下载变化的部分（10-50MB），无需重新下载完整安装包

### Q: 支持哪些模型？
**A:** 
- Stable Diffusion 1.5（推荐，速度快）
- Stable Diffusion XL（更高质量，需要 10GB+ 显存）
- 社区微调模型（可从 [Civitai](https://civitai.com/) 下载）

### Q: 遇到错误怎么办？
**A:** 
1. 查看 [USER_GUIDE.md](USER_GUIDE.md) 中的故障排除章节
2. 检查 `logs/` 目录中的日志文件
3. 访问[官方论坛](https://github.com/AUTOMATIC1111/stable-diffusion-webui/discussions)寻求帮助

---

## 📚 文档索引

| 文档 | 说明 |
|-----|------|
| [README.md](README.md) | 本文档（入口文档） |
| [BUILD_GUIDE.md](BUILD_GUIDE.md) | 开发者构建指南 |
| [USER_GUIDE.md](USER_GUIDE.md) | 用户使用指南（详细） |
| [ARCHITECTURE_ANALYSIS.md](ARCHITECTURE_ANALYSIS.md) | 架构分析文档 |
| [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) | 重构总结 |
| [CHANGELOG.md](CHANGELOG.md) | 变更日志 |

---

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📜 许可证

本项目遵循 **AGPL-3.0** 许可证。详见 [LICENSE.txt](../LICENSE.txt)

---

## 🙏 致谢

- [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) - 核心 WebUI
- [Stability AI](https://stability.ai/) - Stable Diffusion 模型
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
- [PyInstaller](https://pyinstaller.org/) - 打包工具

---

## 📧 联系方式

- 问题反馈：[GitHub Issues](https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues)
- 讨论区：[GitHub Discussions](https://github.com/AUTOMATIC1111/stable-diffusion-webui/discussions)

---

<div align="center">
Made with ❤️ by SD-WebUI Desktop Team
</div>
