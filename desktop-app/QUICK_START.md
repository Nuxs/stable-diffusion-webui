# 快速开始指南

## 🎯 当前状态

✅ **代码已完善** - DLL 路径自动修复已添加到代码中
✅ **打包配置已优化** - 使用 `app_onedir_fixed.spec`
⚠️ **需要系统依赖** - Visual C++ Redistributable

## 🚀 立即开始

### 第一步：安装系统依赖（必需！）

**这是最关键的一步！**

1. 下载 Visual C++ Redistributable:
   ```
   https://aka.ms/vs/17/release/vc_redist.x64.exe
   ```

2. 运行安装程序

3. **重启计算机**（必须！）

### 第二步：验证环境

```bash
# 检查依赖
python check_dependencies.py

# 应该看到：
# PyQt6.QtCore: ✓ 可以导入
# PyQt6.QtWidgets: ✓ 可以导入
```

### 第三步：运行应用

#### 方式 A: 开发模式（推荐先测试）

```bash
python src/main.py
```

#### 方式 B: 打包版本

```bash
# 如果还没打包，先打包
python -m PyInstaller app_onedir_fixed.spec --clean

# 运行
.\dist\StableDiffusionWebUI\StableDiffusionWebUI.exe
```

## 📋 文件说明

| 文件 | 说明 |
|------|------|
| `src/main.py` | 主程序（已包含 DLL 修复） |
| `app_onedir_fixed.spec` | 修复后的打包配置 |
| `check_dependencies.py` | 依赖检查工具 |
| `SOLUTION.md` | 完整解决方案文档 |
| `STATUS.md` | 项目状态总结 |

## ❓ 常见问题

### Q: 仍然报 DLL 错误？
A: 
1. 确认已安装 Visual C++ Redistributable
2. **确认已重启计算机**
3. 运行 `python check_dependencies.py` 查看详细信息

### Q: 开发模式可以运行，打包版本不行？
A: 使用 `app_onedir_fixed.spec` 重新打包：
```bash
python -m PyInstaller app_onedir_fixed.spec --clean
```

### Q: 如何确认问题已解决？
A: 运行以下命令，应该显示 "Success!"：
```bash
python -c "from PyQt6.QtWidgets import QApplication; print('Success!')"
```

## 📞 需要帮助？

1. 查看 `SOLUTION.md` 获取详细解决方案
2. 运行 `python check_dependencies.py` 获取诊断信息
3. 查看 `STATUS.md` 了解项目当前状态

