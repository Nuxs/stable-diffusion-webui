# 🔧 路径修复说明

## ✅ 已修复的问题

打包后的应用无法找到 WebUI 项目的 `launch.py` 和 `webui.py` 文件。

## 🎯 解决方案

应用现在会自动检测 WebUI 项目位置，支持以下方式：

### 1. 自动检测（推荐）

应用会自动从以下位置查找 WebUI 项目：

1. **从 exe 目录向上查找**
   - `dist/StableDiffusionWebUI/` → `dist/` → `stable-diffusion-webui/`
   - 最多向上查找 5 级目录

2. **从当前工作目录查找**
   - 如果当前目录包含 `launch.py` 或 `webui.py`

3. **从配置文件中读取**
   - 如果配置文件中指定了路径

### 2. 手动配置（如果自动检测失败）

如果自动检测失败，可以手动配置：

1. **创建配置文件**
   - 位置：`dist/StableDiffusionWebUI/config/app_config.json`

2. **添加项目路径**
   ```json
   {
     "port": 7860,
     "webui_project_path": "C:\\Users\\YourName\\Documents\\GitHub\\stable-diffusion-webui"
   }
   ```

## 📁 推荐的目录结构

```
stable-diffusion-webui/
├── launch.py
├── webui.py
├── models/
├── venv/
└── desktop-app/
    └── dist/
        └── StableDiffusionWebUI/
            ├── StableDiffusionWebUI.exe
            ├── _internal/
            └── config/
                └── app_config.json  (可选)
```

## 🚀 使用方法

### 方式 1: 标准结构（推荐）

将打包后的应用放在 `desktop-app/dist/StableDiffusionWebUI/` 中，应用会自动找到上级目录的 WebUI 项目。

### 方式 2: 自定义位置

1. 将 `StableDiffusionWebUI` 文件夹复制到任意位置
2. 创建 `config/app_config.json` 文件
3. 设置 `webui_project_path` 为 WebUI 项目的完整路径

### 方式 3: 从 WebUI 项目目录运行

在 WebUI 项目根目录运行应用，应用会自动检测当前目录。

## ⚠️ 注意事项

1. **路径格式**
   - Windows 路径使用反斜杠 `\` 或正斜杠 `/`
   - 在 JSON 中需要使用转义：`\\` 或 `/`

2. **路径验证**
   - 应用会验证路径是否存在
   - 会检查 `launch.py` 或 `webui.py` 是否存在

3. **错误提示**
   - 如果找不到项目，应用会显示详细的错误信息
   - 建议查看日志文件：`logs/app.log`

## 🔍 调试

如果应用无法找到项目：

1. **查看日志**
   ```bash
   # 日志位置
   dist/StableDiffusionWebUI/logs/app.log
   ```

2. **手动测试**
   ```bash
   # 在 WebUI 项目目录中
   python launch.py --port 7860
   ```

3. **检查路径**
   - 确保 `launch.py` 或 `webui.py` 存在
   - 确保路径中没有特殊字符
   - 确保有读取权限

## ✅ 修复完成

现在打包后的应用应该能够正确找到 WebUI 项目了！


