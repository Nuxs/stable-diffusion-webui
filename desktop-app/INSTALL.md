# 安装指南

## 方式一：直接运行（开发模式）

### 1. 安装依赖

```bash
cd desktop-app
pip install -r requirements.txt
```

或者使用提供的批处理文件：

```bash
setup.bat
```

### 2. 运行应用

```bash
python src/main.py
```

或者：

```bash
run.bat
```

## 方式二：打包为可执行文件

### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

### 2. 打包应用

```bash
python build.py
```

打包完成后，可执行文件将位于 `dist/StableDiffusionWebUI.exe`

### 3. 运行可执行文件

直接双击 `dist/StableDiffusionWebUI.exe` 即可运行。

## 方式三：创建安装程序

### 1. 安装 Inno Setup

下载并安装 Inno Setup: https://jrsoftware.org/isdl.php

### 2. 生成安装脚本

```bash
python create_installer.py
```

这将创建 `installer.iss` 文件。

### 3. 编译安装程序

1. 打开 Inno Setup Compiler
2. 打开 `installer.iss` 文件
3. 点击 "Build" -> "Compile" 或按 F9

安装程序将位于 `installer/` 目录中。

## 注意事项

1. **Python 环境**: 确保已安装 Python 3.10 或更高版本
2. **WebUI 依赖**: 桌面应用需要 Stable Diffusion WebUI 项目及其所有依赖已正确安装
3. **端口冲突**: 如果默认端口 7860 被占用，应用会自动尝试其他端口
4. **首次运行**: 首次运行可能需要一些时间来启动服务器

## 故障排除

### 问题：无法启动服务器

- 检查 Python 环境是否正确
- 检查 Stable Diffusion WebUI 的依赖是否已安装
- 查看 `logs/app.log` 获取详细错误信息

### 问题：页面无法加载

- 检查服务器是否正常启动
- 查看状态栏的服务器状态
- 尝试在浏览器中打开查看错误信息

### 问题：打包失败

- 确保已安装 PyInstaller
- 检查所有依赖是否已安装
- 查看构建日志获取详细错误信息

## 配置

应用配置文件位于 `config/app_config.json`，可以修改以下设置：

- `port`: 服务器端口（默认: 7860）
- `api`: 是否启用 API（默认: false）
- `listen`: 监听地址（默认: 127.0.0.1）
- `window_width`: 窗口宽度（默认: 1200）
- `window_height`: 窗口高度（默认: 800）


