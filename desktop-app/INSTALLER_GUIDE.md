# 📦 安装程序制作指南

## ✅ 打包完成

应用已成功打包到：
```
desktop-app/dist/StableDiffusionWebUI/
```

## 🎯 创建安装程序

### 方式 1: 使用 Inno Setup（推荐）

1. **下载 Inno Setup**
   - 访问: https://jrsoftware.org/isinfo.php
   - 下载并安装 Inno Setup Compiler

2. **创建安装脚本**
   已创建 `installer.iss` 文件，包含完整的安装程序配置。

3. **编译安装程序**
   - 打开 Inno Setup Compiler
   - 打开 `desktop-app/installer.iss`
   - 点击 "Build" -> "Compile"
   - 安装程序将生成在 `desktop-app/dist/` 目录

### 方式 2: 使用 NSIS

1. **下载 NSIS**
   - 访问: https://nsis.sourceforge.io/
   - 下载并安装 NSIS

2. **创建安装脚本**
   创建 `.nsi` 文件配置安装程序

### 方式 3: 直接分发文件夹

最简单的方式是直接分发打包后的文件夹：
1. 压缩 `dist/StableDiffusionWebUI` 文件夹
2. 用户解压后直接运行 `StableDiffusionWebUI.exe`

## 📋 安装程序功能

### 基本功能
- ✅ 安装到用户选择的目录
- ✅ 创建桌面快捷方式
- ✅ 创建开始菜单项
- ✅ 卸载程序

### 高级功能（可选）
- 自动检测 WebUI 项目位置
- 配置虚拟环境
- 下载必要依赖

## 🚀 快速开始

### 使用 Inno Setup

1. **安装 Inno Setup**
   ```powershell
   # 下载并安装 Inno Setup
   # https://jrsoftware.org/isinfo.php
   ```

2. **编译安装程序**
   ```powershell
   cd desktop-app
   # 使用 Inno Setup Compiler 打开 installer.iss
   # 或使用命令行：
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
   ```

3. **分发安装程序**
   - 安装程序位于 `dist/StableDiffusionWebUI_Setup.exe`
   - 分发给用户安装使用

## 📝 注意事项

### 1. WebUI 项目依赖
应用需要访问原始的 `stable-diffusion-webui` 项目：
- 确保用户已安装 WebUI 项目
- 或在安装程序中包含 WebUI 项目

### 2. 虚拟环境
- 应用会自动检测并使用虚拟环境
- 如果不存在，会使用系统 Python

### 3. 首次运行
- 应用会自动启动服务器
- 可能需要几分钟加载模型

## 🎉 完成！

打包和安装程序配置已完成！


