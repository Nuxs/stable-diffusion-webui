# PyQt6 完整版桌面应用构建和分发指南

## 概述

`build.py` 用于构建完整的 PyQt6 桌面应用，界面功能最完善。构建后的应用可以在其他 Windows 电脑上直接运行。

## 构建步骤

### 1. 安装依赖

确保已安装必要的依赖：

```bash
pip install pyinstaller PyQt6 PyQt6-WebEngine
```

### 2. 运行构建脚本

```bash
cd desktop-app
python build.py
```

### 3. 构建输出

构建完成后，可执行文件位于：
```
dist/StableDiffusionWebUI/StableDiffusionWebUI.exe
```

## 分发到其他电脑

### 方法 1: 直接复制文件夹（推荐）

1. 将整个 `dist/StableDiffusionWebUI` 文件夹复制到目标电脑
2. 在目标电脑上运行 `StableDiffusionWebUI.exe`

### 方法 2: 创建安装包

可以使用 Inno Setup 或其他安装包制作工具创建安装程序。

## 系统要求

### 目标电脑必须安装：

1. **Visual C++ Redistributable 2015-2022**
   - 下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - 这是 PyQt6 运行所必需的

2. **Windows 10/11 (64位)**

### 不需要安装：
- Python
- PyQt6
- 其他 Python 依赖

## 目录结构

构建后的目录结构：
```
StableDiffusionWebUI/
├── StableDiffusionWebUI.exe  # 主程序
├── _internal/                 # 内部依赖文件
├── PyQt6/                     # PyQt6 库文件
│   ├── Qt6/
│   │   ├── bin/              # Qt DLL 文件
│   │   ├── plugins/          # Qt 插件
│   │   └── qml/              # QML 文件
│   └── ...
├── resources/                 # 资源文件
└── ...                       # 其他依赖文件
```

## 与 Tkinter 版本的区别

- **build.py (PyQt6 版本)**: 
  - 界面更现代、功能更完善
  - 使用 Qt WebEngine 显示 WebUI
  - 支持更多界面功能（缩放、工具栏等）
  - 文件体积较大（~200-300MB）

- **build_tkinter.py (Tkinter 版本)**:
  - 界面简单
  - 使用系统浏览器打开 WebUI
  - 文件体积较小（~50MB）

## 故障排除

### 问题：应用无法启动

1. 检查是否安装了 Visual C++ Redistributable
2. 检查 Windows 版本是否为 64 位
3. 查看是否有错误提示

### 问题：DLL 加载失败

1. 确保整个 `StableDiffusionWebUI` 文件夹完整复制
2. 不要只复制 `StableDiffusionWebUI.exe` 文件
3. 检查 `PyQt6/Qt6/bin` 目录是否存在

### 问题：WebEngine 无法加载页面

1. 确保 `PyQt6/Qt6/plugins` 目录存在
2. 确保 `PyQt6/Qt6/qml` 目录存在

## 构建选项

### 目录模式（当前使用）

- **优点**: DLL 加载更可靠，启动更快，更容易调试
- **缺点**: 文件分散在多个目录中

### 单文件模式（可选）

如果需要单文件模式，可以修改 `app.spec` 中的 `exclude_binaries=False`，但可能遇到 DLL 加载问题。

## 注意事项

1. 首次构建可能需要较长时间（5-10分钟）
2. 构建过程中会下载一些依赖，确保网络连接正常
3. 构建后的文件夹较大（200-300MB），分发时注意文件大小
4. 建议在干净的 Windows 系统上测试构建结果



