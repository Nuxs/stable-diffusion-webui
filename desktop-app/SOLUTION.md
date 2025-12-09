# PyQt6 DLL 加载问题完整解决方案

## 问题根源

开发环境中 PyQt6 也无法导入，说明问题不在打包，而是**系统环境缺少必要的依赖**。

## 已实施的修复

### 1. 代码层面修复

已在 `src/main.py` 中添加了 DLL 路径修复代码：
- 自动检测并添加 PyQt6 DLL 目录到系统搜索路径
- 支持打包模式和开发模式
- 使用 Windows API `AddDllDirectory` 优先，失败时回退到 PATH

### 2. 打包配置优化

创建了 `app_onedir_fixed.spec`，包含：
- 完整的 PyQt6 DLL 收集
- PyQt6 插件目录包含
- 运行时 hook 支持

## 必须的系统依赖

### Visual C++ Redistributable

**这是最关键的一步！**

1. 下载并安装：
   - 64位: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - 或搜索 "Microsoft Visual C++ Redistributable 2015-2022"

2. **安装后必须重启计算机**

3. 验证安装：
   ```powershell
   Test-Path "C:\Windows\System32\vcruntime140.dll"
   ```

## 使用修复后的应用

### 方式 1: 使用新打包的版本

```bash
# 使用修复后的 spec 文件打包
python -m PyInstaller app_onedir_fixed.spec --clean

# 运行
.\dist\StableDiffusionWebUI\StableDiffusionWebUI.exe
```

### 方式 2: 开发模式运行

如果打包版本仍有问题，可以直接运行源代码：

```bash
python src/main.py
```

代码中已包含 DLL 路径修复，应该能正常工作。

## 验证修复

运行以下命令验证：

```bash
# 检查依赖
python check_dependencies.py

# 测试 PyQt6
python -c "from PyQt6.QtWidgets import QApplication; print('Success!')"
```

## 如果仍然失败

### 步骤 1: 重新安装 PyQt6

```bash
pip uninstall PyQt6 PyQt6-WebEngine
pip install --no-cache-dir PyQt6 PyQt6-WebEngine
```

### 步骤 2: 检查系统架构

确保：
- Python 是 64 位版本
- Visual C++ Redistributable 是 64 位版本
- 系统是 64 位

### 步骤 3: 使用官方 Python

如果使用 Anaconda，尝试切换到官方 Python：
- 下载: https://www.python.org/downloads/
- 安装时选择 "Add Python to PATH"
- 重新安装 PyQt6

### 步骤 4: 检查安全软件

某些杀毒软件可能阻止 DLL 加载，尝试：
- 临时禁用杀毒软件
- 将应用目录添加到白名单

## 文件说明

- `app_onedir_fixed.spec` - 修复后的打包配置
- `src/main.py` - 已添加 DLL 路径修复代码
- `check_dependencies.py` - 依赖检查工具
- `fix_pyqt6.py` - 自动修复脚本
- `README_FIX.md` - 详细修复指南

## 当前状态

✅ 代码已修复（DLL 路径自动设置）
✅ 打包配置已优化
⚠️ 需要安装 Visual C++ Redistributable（系统依赖）

## 下一步

1. **安装 Visual C++ Redistributable**（最重要！）
2. **重启计算机**
3. 运行 `python check_dependencies.py` 验证
4. 测试应用

如果安装 VC++ Redistributable 后仍然无法运行，请提供 `check_dependencies.py` 的完整输出。


