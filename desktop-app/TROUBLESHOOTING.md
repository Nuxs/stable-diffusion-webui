# 故障排除指南

## DLL 加载失败问题

如果遇到 "DLL load failed" 错误，可以尝试以下解决方案：

### 方案 1: 使用目录模式打包

目录模式会将 DLL 文件单独存放，更容易解决依赖问题：

```bash
pyinstaller app_onedir.spec --clean
```

打包后，所有文件会在 `dist/StableDiffusionWebUI/` 目录中，直接运行其中的 `StableDiffusionWebUI.exe`。

### 方案 2: 检查 Visual C++ 运行库

确保已安装 Microsoft Visual C++ Redistributable：
- 下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe

### 方案 3: 使用开发模式运行

如果打包版本有问题，可以直接运行源代码：

```bash
python src/main.py
```

这样可以确认问题是否出在打包过程。

### 方案 4: 检查 PyQt6 安装

确保 PyQt6 正确安装：

```bash
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

### 方案 5: 重新安装 PyQt6

如果 PyQt6 有问题，尝试重新安装：

```bash
pip uninstall PyQt6 PyQt6-WebEngine
pip install PyQt6 PyQt6-WebEngine
```

## 其他常见问题

### 服务器启动失败

1. 检查端口是否被占用
2. 查看 `logs/app.log` 获取详细错误信息
3. 确保 Stable Diffusion WebUI 的依赖已正确安装

### 页面无法加载

1. 检查服务器是否正常启动（查看状态栏）
2. 尝试在浏览器中打开查看错误信息
3. 检查防火墙设置

### 打包文件过大

单文件模式会包含所有依赖，文件较大（200+ MB）是正常的。如果觉得太大，可以使用目录模式。

## 获取帮助

如果以上方案都无法解决问题，请：
1. 查看 `logs/app.log` 获取详细错误信息
2. 在开发模式下运行并查看控制台输出
3. 提供完整的错误信息和系统环境信息

