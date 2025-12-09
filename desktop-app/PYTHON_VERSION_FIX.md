# Python 版本兼容性问题

## 问题

Stable Diffusion WebUI 推荐使用 **Python 3.10.6**，但当前环境是 **Python 3.12.7**。

这可能导致：
- torch 版本不兼容
- 其他依赖包版本问题
- 服务器启动失败

## 解决方案

### 方案 1: 使用 --skip-python-version-check（已添加）

代码中已自动添加此参数，但可能仍有依赖问题。

### 方案 2: 安装 Python 3.10.6（推荐）

1. 下载 Python 3.10.6:
   - https://www.python.org/downloads/release/python-3106/

2. 安装时选择 "Add Python to PATH"

3. 创建虚拟环境:
   ```bash
   python3.10 -m venv venv
   venv\Scripts\activate
   ```

4. 在虚拟环境中安装依赖

### 方案 3: 使用 WebUI 的虚拟环境

如果 WebUI 项目中有 `venv` 文件夹：

```bash
# 激活 WebUI 的虚拟环境
venv\Scripts\activate

# 然后运行桌面应用
python desktop-app/src/main_tkinter.py
```

### 方案 4: 修改服务器启动使用特定 Python

在 `server_manager_tkinter.py` 中，可以指定 Python 路径：

```python
# 如果存在 venv，使用 venv 中的 Python
venv_python = self.project_root / "venv" / "Scripts" / "python.exe"
if venv_python.exists():
    python_exe = str(venv_python)
```

## 当前状态

- ✅ 已添加 `--skip-python-version-check` 参数
- ⚠️ 可能仍有依赖版本问题
- 💡 建议使用 Python 3.10.6 或 WebUI 的虚拟环境

