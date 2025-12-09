# Stable Diffusion WebUI 桌面应用程序

这是一个将 Stable Diffusion WebUI 打包为 Windows 桌面应用程序的项目。

## 功能特性

- 🖥️ 现代化的桌面应用界面
- 🌐 内置 WebView，无需打开浏览器
- 🔄 自动管理服务器启动和停止
- ⚙️ 可配置的服务器参数
- 📦 可打包为独立的可执行文件
- 🎨 美观的用户界面

## 系统要求

- Windows 10/11
- Python 3.10 或更高版本
- 已安装 Stable Diffusion WebUI 及其依赖

## 安装依赖

```bash
cd desktop-app
pip install -r requirements.txt
```

## 运行应用

```bash
python src/main.py
```

## 打包应用

使用 PyInstaller 打包为可执行文件：

```bash
python build.py
```

打包后的可执行文件将位于 `dist` 目录中。

## 项目结构

```
desktop-app/
├── src/                    # 源代码
│   ├── main.py            # 主入口
│   ├── main_window.py     # 主窗口
│   ├── server_manager.py  # 服务器管理
│   └── utils/             # 工具类
├── resources/             # 资源文件
├── config/                # 配置文件
├── logs/                  # 日志文件
├── build/                 # 构建临时文件
├── dist/                  # 打包输出
├── requirements.txt       # Python 依赖
└── README.md             # 说明文档
```

## 配置

应用配置文件位于 `config/app_config.json`，可以配置：

- `port`: 服务器端口（默认: 7860）
- `api`: 是否启用 API（默认: false）
- `listen`: 监听地址（默认: 127.0.0.1）
- `theme`: 主题（默认: default）
- `window_width`: 窗口宽度（默认: 1200）
- `window_height`: 窗口高度（默认: 800）

## 许可证

与 Stable Diffusion WebUI 项目相同。


