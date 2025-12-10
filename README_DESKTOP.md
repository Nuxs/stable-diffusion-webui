# Stable Diffusion WebUI 桌面应用

## 📍 重要提示

桌面应用代码位于 `desktop-app/` 目录中，**不在项目根目录**。

## 🚀 快速运行

### 方式 1: 使用批处理文件（推荐）

从项目根目录运行：
```bash
desktop-app\run_desktop.bat
```

### 方式 2: 进入目录运行

```bash
cd desktop-app
python src/main.py
```

### 方式 3: 使用完整路径

```bash
python desktop-app/src/main.py
```

## ⚠️ 系统要求

在运行之前，**必须安装**：

1. **Visual C++ Redistributable**
   - 下载: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - 安装后**重启计算机**

2. **Python 依赖**
   ```bash
   cd desktop-app
   pip install -r requirements.txt
   ```

## 📖 详细文档

进入 `desktop-app/` 目录查看：
- `QUICK_START.md` - 快速开始指南
- `SOLUTION.md` - 完整解决方案
- `STATUS.md` - 项目状态

## 🔧 故障排除

如果遇到 DLL 加载错误：
1. 确认已安装 Visual C++ Redistributable
2. 确认已重启计算机
3. 运行 `desktop-app/check_dependencies.py` 检查



