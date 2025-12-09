# 快速开始指南

## 第一步：安装依赖

运行安装脚本：

```bash
setup.bat
```

或者手动安装：

```bash
pip install -r requirements.txt
```

## 第二步：运行应用

### 开发模式

```bash
run.bat
```

或者：

```bash
python src/main.py
```

### 打包模式

1. 打包应用：

```bash
python build.py
```

2. 运行打包后的可执行文件：

```bash
dist\StableDiffusionWebUI.exe
```

## 功能说明

### 主界面

- **菜单栏**: 提供文件、视图、服务器和帮助菜单
- **工具栏**: 快速访问常用功能
- **WebView**: 显示 Stable Diffusion WebUI 界面
- **状态栏**: 显示服务器状态和加载进度

### 快捷键

- `F5`: 重新加载页面
- `Ctrl+B`: 在浏览器中打开
- `Ctrl++`: 放大
- `Ctrl+-`: 缩小
- `Ctrl+0`: 重置缩放
- `Ctrl+Q`: 退出应用

### 服务器管理

应用会自动启动和管理 WebUI 服务器：

- 启动时自动启动服务器
- 关闭时自动停止服务器
- 可以通过菜单手动重启或停止服务器

## 常见问题

### Q: 应用无法启动？

A: 检查以下几点：
1. Python 是否正确安装
2. 依赖是否已安装（运行 `setup.bat`）
3. Stable Diffusion WebUI 项目是否在正确的位置

### Q: 服务器启动失败？

A: 检查以下几点：
1. 端口是否被占用（应用会自动尝试其他端口）
2. WebUI 的依赖是否已安装
3. 查看 `logs/app.log` 获取详细错误信息

### Q: 页面无法加载？

A: 尝试以下方法：
1. 点击"重新加载"按钮
2. 在浏览器中打开查看错误信息
3. 检查服务器是否正常运行（查看状态栏）

### Q: 如何更改端口？

A: 编辑 `config/app_config.json`，修改 `port` 字段。

## 下一步

- 查看 [INSTALL.md](INSTALL.md) 了解详细安装说明
- 查看 [README.md](README.md) 了解项目详情
- 查看日志文件 `logs/app.log` 获取运行信息


