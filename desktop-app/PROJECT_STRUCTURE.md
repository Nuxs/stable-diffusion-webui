# 项目结构说明

## 目录结构

```
desktop-app/
├── src/                          # 源代码目录
│   ├── main.py                  # 应用程序主入口
│   ├── main_window.py           # 主窗口类
│   ├── server_manager.py        # 服务器管理器
│   └── utils/                   # 工具类
│       ├── __init__.py
│       ├── config.py            # 配置管理
│       └── logger.py            # 日志配置
│
├── resources/                    # 资源文件目录
│   ├── icon.ico                 # 应用图标（需要添加）
│   └── README.md                # 资源说明
│
├── config/                      # 配置文件目录
│   └── app_config.json          # 应用配置（自动生成）
│
├── logs/                        # 日志文件目录（自动生成）
│   └── app.log                  # 应用日志
│
├── build/                       # 构建临时文件（自动生成）
├── dist/                        # 打包输出目录（自动生成）
│
├── requirements.txt             # Python 依赖列表
├── app.spec                     # PyInstaller 规格文件
├── build.py                     # 构建脚本
├── create_installer.py          # 安装程序创建脚本
├── setup.bat                    # Windows 安装脚本
├── run.bat                      # Windows 运行脚本
├── README.md                    # 项目说明
├── INSTALL.md                   # 安装指南
├── QUICKSTART.md                # 快速开始指南
└── PROJECT_STRUCTURE.md         # 本文件
```

## 核心文件说明

### 源代码

- **main.py**: 应用程序入口点，初始化 Qt 应用和主窗口
- **main_window.py**: 主窗口类，包含 UI 组件和用户交互逻辑
- **server_manager.py**: 管理 WebUI 服务器的启动、停止和状态检查
- **utils/config.py**: 管理应用配置（端口、窗口大小等）
- **utils/logger.py**: 配置日志系统

### 构建和打包

- **build.py**: 使用 PyInstaller 打包应用的脚本
- **app.spec**: PyInstaller 规格文件，定义打包参数
- **create_installer.py**: 生成 Inno Setup 安装脚本

### 配置文件

- **requirements.txt**: Python 依赖包列表
- **config/app_config.json**: 应用运行时配置（自动生成）

### 脚本文件

- **setup.bat**: 安装依赖的批处理脚本
- **run.bat**: 运行应用的批处理脚本

## 工作流程

### 开发流程

1. 修改源代码 (`src/`)
2. 运行 `run.bat` 测试
3. 查看日志 (`logs/app.log`) 调试

### 打包流程

1. 运行 `python build.py` 打包
2. 在 `dist/` 目录找到可执行文件
3. （可选）运行 `python create_installer.py` 创建安装程序

### 运行流程

1. 应用启动 (`main.py`)
2. 初始化主窗口 (`main_window.py`)
3. 启动服务器管理器 (`server_manager.py`)
4. 服务器管理器启动 WebUI 服务器
5. 主窗口加载 WebView 显示 WebUI 界面

## 技术栈

- **PyQt6**: GUI 框架
- **PyQt6-WebEngine**: WebView 组件
- **requests**: HTTP 请求库
- **PyInstaller**: 打包工具
- **Inno Setup**: 安装程序创建工具（可选）

## 扩展说明

### 添加新功能

1. 在 `src/` 目录创建新模块
2. 在 `main_window.py` 中集成新功能
3. 更新 `requirements.txt` 添加新依赖

### 自定义配置

编辑 `src/utils/config.py` 添加新的配置项。

### 修改界面

编辑 `main_window.py` 中的 `get_stylesheet()` 方法修改样式。

## 注意事项

1. **图标文件**: 需要手动添加 `resources/icon.ico` 文件
2. **WebUI 依赖**: 确保 Stable Diffusion WebUI 及其依赖已正确安装
3. **端口冲突**: 应用会自动检测并选择可用端口
4. **日志文件**: 日志文件会不断增长，定期清理 `logs/` 目录

