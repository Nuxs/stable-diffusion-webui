# PyQt6 DLL 加载问题修复指南

## 问题描述

如果遇到 `DLL load failed while importing QtWidgets: 找不到指定的程序` 错误，这通常是因为：

1. **缺少 Visual C++ Redistributable** - PyQt6 需要这个运行时库
2. **PyQt6 安装不完整** - 某些 DLL 文件缺失或损坏
3. **系统环境问题** - PATH 环境变量或系统配置问题

## 快速修复步骤

### 步骤 1: 安装 Visual C++ Redistributable

**这是最可能的原因！**

1. 下载 Visual C++ Redistributable:
   - 直接下载: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - 或者搜索 "Visual C++ Redistributable 2015-2022"

2. 运行安装程序并完成安装

3. **重启计算机**（重要！）

4. 重新测试应用

### 步骤 2: 重新安装 PyQt6

如果步骤 1 无效，尝试重新安装 PyQt6:

```bash
pip uninstall PyQt6 PyQt6-WebEngine
pip install PyQt6 PyQt6-WebEngine
```

### 步骤 3: 使用修复脚本

运行修复脚本:

```bash
python fix_pyqt6.py
```

### 步骤 4: 检查系统依赖

运行依赖检查:

```bash
python check_dependencies.py
```

## 验证修复

运行以下命令验证 PyQt6 是否可以正常导入:

```bash
python -c "from PyQt6.QtWidgets import QApplication; print('Success!')"
```

如果显示 "Success!"，说明问题已解决。

## 如果仍然无法解决

1. **检查系统架构**: 确保安装的是 64 位版本的 Visual C++ Redistributable
2. **检查 Python 版本**: 确保使用 Python 3.10 或更高版本
3. **检查防火墙/杀毒软件**: 某些安全软件可能阻止 DLL 加载
4. **查看详细错误**: 运行 `python check_dependencies.py` 获取详细信息

## 临时解决方案

如果无法修复系统环境，可以：

1. **使用开发模式运行**（不打包）:
   ```bash
   python src/main.py
   ```

2. **使用虚拟环境**: 创建一个新的虚拟环境并重新安装所有依赖

3. **使用其他 Python 发行版**: 尝试使用官方 Python 而不是 Anaconda

## 联系支持

如果以上方法都无法解决问题，请提供：
- `python check_dependencies.py` 的完整输出
- Python 版本和系统信息
- 错误消息的完整内容


