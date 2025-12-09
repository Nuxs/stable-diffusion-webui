# 📦 打包指南

## ✅ 打包完成！

Tkinter 版本的桌面应用已成功打包。

## 📁 打包结果

打包后的文件位于：
```
desktop-app/dist/StableDiffusionWebUI/
```

### 主要文件
- `StableDiffusionWebUI.exe` - 主程序可执行文件
- `_internal/` - 内部依赖文件
- `resources/` - 资源文件（如果存在）

## 🚀 使用方法

### 方式 1: 直接运行
1. 进入打包目录：
   ```bash
   cd desktop-app/dist/StableDiffusionWebUI
   ```
2. 双击运行 `StableDiffusionWebUI.exe`

### 方式 2: 命令行运行
```bash
cd desktop-app/dist/StableDiffusionWebUI
.\StableDiffusionWebUI.exe
```

## 📋 打包说明

### 打包配置
- **配置文件**: `app_tkinter.spec`
- **打包脚本**: `build_tkinter.py`
- **模式**: 目录模式（onedir）
- **控制台**: 无控制台窗口（console=False）

### 包含的内容
- ✅ Tkinter GUI 框架
- ✅ 服务器管理器
- ✅ 所有 Python 依赖
- ✅ 资源文件（图标等）

### 不包含的内容
- ❌ WebUI 项目文件（需要单独安装）
- ❌ Python 解释器（已打包在 exe 中）

## ⚠️ 重要提示

### 1. WebUI 项目位置
应用需要访问原始的 `stable-diffusion-webui` 项目目录。确保：
- WebUI 项目已正确安装
- 虚拟环境已配置（如果使用）
- 模型文件已下载

### 2. 首次运行
首次运行时，应用会：
- 自动检测 WebUI 项目位置
- 启动服务器
- 打开浏览器窗口

### 3. 分发应用
如果要分发应用给其他用户：
1. 打包整个 `dist/StableDiffusionWebUI` 目录
2. 确保用户已安装 WebUI 项目
3. 提供使用说明

## 🔧 重新打包

如果需要重新打包：
```bash
cd desktop-app
python build_tkinter.py
```

## 📝 打包选项

### 修改打包模式
编辑 `app_tkinter.spec` 文件：
- `console=False` - 无控制台窗口（GUI 模式）
- `console=True` - 显示控制台窗口（调试模式）

### 添加资源文件
在 `app_tkinter.spec` 的 `datas` 列表中添加：
```python
datas = [
    ('path/to/file', 'destination/path'),
]
```

## 🎉 完成！

应用已成功打包，可以独立运行！

