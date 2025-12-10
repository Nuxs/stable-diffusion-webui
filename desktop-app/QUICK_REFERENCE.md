# 快速参考指南

<div align="center">

**Desktop App 开发和使用速查表**

[代码结构](#代码结构) • [常用命令](#常用命令) • [配置说明](#配置说明) • [API参考](#api参考) • [故障排除](#故障排除)

</div>

---

## 代码结构

### 核心模块

```python
# 启动入口
src/launcher.py          # 智能启动器，集成首次运行检测

# UI组件
src/main_window.py       # 主窗口（PyQt6）
src/first_run_wizard.py  # 首次运行向导

# 管理器
src/download_manager.py  # 下载管理（断点续传、重试）
src/model_manager.py     # 模型管理（下载、验证）
src/server_manager.py    # WebUI服务器管理
src/update_manager.py    # 更新管理（版本检查）

# 工具
src/system_detector.py   # 系统信息检测
src/utils/portable_python.py  # Python环境管理
src/utils/environment_manager.py  # 运行时环境解析
src/utils/config.py      # 配置管理
src/utils/logger.py      # 日志系统
```

---

## 常用命令

### 开发模式

```bash
# 运行应用（开发模式）
python src/launcher.py

# 运行系统检测
python src/system_detector.py

# 测试下载管理器
python src/download_manager.py

# 测试模型管理器
python src/model_manager.py
```

### 构建和打包

```bash
# 安装依赖
pip install -r requirements.txt

# 构建应用
python build.py

# 构建输出路径
dist/StableDiffusionWebUI/StableDiffusionWebUI.exe
```

### 测试

```bash
# 运行所有测试
python run_all_tests.py

# 检查依赖
python check_dependencies.py

# PyQt6诊断
python diagnose_pyqt6.py
```

---

## 配置说明

### components.json

组件下载配置文件：

```json
{
  "python_environments": {
    "cpu": {
      "name": "Python 3.10 (CPU)",
      "url": "...",
      "size_bytes": 2147483648,
      "md5": "..."
    },
    "cuda118": {...},
    "cuda121": {...}
  },
  "models": {
    "sd-v1-5": {
      "name": "Stable Diffusion 1.5",
      "url": "...",
      "size_bytes": 4265146195,
      "recommended": true
    }
  }
}
```

### 环境变量

```bash
# 日志级别
export LOG_LEVEL=DEBUG

# 数据目录
export DATA_DIR=/path/to/data

# 代理设置
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
```

---

## API参考

### SystemDetector

```python
from src.system_detector import SystemDetector

# 检测所有信息
info = SystemDetector.detect_all()

# 推荐Python环境
env = SystemDetector.recommend_python_env(info)
# 返回: 'cpu' | 'cuda118' | 'cuda121'

# 检查最低要求
meets, errors = SystemDetector.check_minimum_requirements(info)
```

### DownloadManager

```python
from src.download_manager import DownloadManager

dm = DownloadManager(cache_dir=Path("cache"))

# 下载文件
file_path = dm.download_file(
    url="https://example.com/file.zip",
    expected_md5="abc123...",
    progress_callback=lambda curr, total: print(f"{curr}/{total}"),
    mirrors=["https://mirror1.com/file.zip"]
)

# 解压文件
success = dm.extract_archive(
    archive_path=file_path,
    target_dir=Path("output")
)
```

### ModelManager

```python
from src.model_manager import ModelManager

mm = ModelManager(data_dir=Path("data"), download_manager=dm)

# 列出可用模型
models = mm.list_available_models(filter_by_vram=4*1024*1024*1024)

# 下载模型
model_path = mm.download_model(
    model_id="sd-v1-5",
    progress_callback=lambda curr, total: ...
)

# 检查模型是否已安装
installed = mm.is_model_installed("sd-v1-5")
```

### PortablePythonManager

```python
from src.utils.portable_python import PortablePythonManager

ppm = PortablePythonManager(data_dir=Path("data"), download_manager=dm)

# 设置环境
success = ppm.setup_environment(
    env_type='cuda118',
    progress_callback=lambda step, curr, total: ...
)

# 获取Python路径
python_exe = ppm.get_python_exe()

# 运行命令
result = ppm.run_command(["-m", "pip", "list"])
```

### EnvironmentManager

```python
from pathlib import Path
from src.utils.environment_manager import EnvironmentManager

env_manager = EnvironmentManager(
    project_root=Path("stable-diffusion-webui"),
    data_dir=Path("desktop-app/data")
)

env_manager.refresh()
python_exe = env_manager.get_python_executable()
print("using", python_exe, "from", env_manager.describe_source())
```

- 优先读取 `runtime_state.json` 中的 `python_env` 描述，其次检查 `data/python-env/`、项目 `venv/`，最后回退到系统 `python3.10`。
- `ServerManager` 会在启动前调用该类，以确保始终使用符合要求的 Python 3.10 解释器。

### UpdateManager

```python
from src.update_manager import UpdateManager

um = UpdateManager(app_dir=Path("."), current_version="2.0.0")

# 检查更新
update = um.check_for_updates("webui")

if update:
    print(f"新版本: {update['latest_version']}")
    
    # 应用更新
    success = um.apply_update(update, download_callback=...)
```

---

## 故障排除

### 常见问题

#### 1. PyQt6 DLL 加载失败

```python
# 错误: DLL load failed while importing QtCore

# 解决方案:
# 1. 检查 PyQt6 版本
pip list | grep PyQt6

# 2. 重新安装
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y
pip install PyQt6==6.6.1 PyQt6-WebEngine==6.6.0

# 3. 运行诊断
python diagnose_pyqt6.py
```

#### 2. 下载失败

```python
# 错误: DownloadError: 下载失败，已尝试 3 个URL

# 可能原因:
# - 网络连接问题
# - 镜像服务器不可用
# - 防火墙阻止

# 解决方案:
# 1. 检查网络连接
ping google.com

# 2. 使用代理
export HTTP_PROXY=http://proxy:port

# 3. 查看日志
tail -f logs/app.log
```

#### 3. 系统检测失败

```python
# 错误: 未检测到 GPU

# 解决方案:
# 1. 检查 nvidia-smi
nvidia-smi

# 2. 更新驱动
# 访问 NVIDIA 官网下载最新驱动

# 3. 手动设置环境类型
# 在首次运行向导中选择 CPU 版本
```

#### 4. Python环境设置失败

```python
# 错误: Python 环境设置失败

# 可能原因:
# - 磁盘空间不足
# - 权限不足
# - 网络超时

# 解决方案:
# 1. 检查磁盘空间
df -h

# 2. 以管理员运行
# 右键 -> 以管理员身份运行

# 3. 增加超时时间
# 编辑 portable_python.py
# 修改 timeout=1800 为更大值
```

---

## 调试技巧

### 启用详细日志

```python
# 方法1: 环境变量
export LOG_LEVEL=DEBUG

# 方法2: 修改 logger.py
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG
    ...
)
```

### 查看日志文件

```bash
# 实时查看
tail -f logs/app.log

# 搜索错误
grep -i error logs/app.log

# 查看最后100行
tail -n 100 logs/app.log
```

### 性能分析

```python
import cProfile
import pstats

# 分析启动性能
cProfile.run('main()', 'profile_stats')

# 查看结果
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(20)
```

---

## 开发技巧

### 代码风格

```python
# 使用类型提示
def download_file(url: str, output_path: Optional[Path] = None) -> Path:
    ...

# 添加文档字符串
def process_data(data: Dict) -> bool:
    """
    处理数据
    
    Args:
        data: 输入数据字典
    
    Returns:
        bool: 是否成功
    """
    ...

# 使用日志而非print
logger.info("开始处理...")  # ✓
print("开始处理...")         # ✗
```

### 测试编写

```python
import unittest
from pathlib import Path
from src.download_manager import DownloadManager

class TestDownloadManager(unittest.TestCase):
    def setUp(self):
        self.dm = DownloadManager(Path("test_cache"))
    
    def test_download_file(self):
        file_path = self.dm.download_file(
            url="https://example.com/test.txt"
        )
        self.assertTrue(file_path.exists())
    
    def tearDown(self):
        # 清理测试文件
        ...
```

---

## 资源链接

### 文档
- [README](README.md) - 项目介绍
- [BUILD_GUIDE](BUILD_GUIDE.md) - 构建指南
- [USER_GUIDE](USER_GUIDE.md) - 用户手册
- [ARCHITECTURE_ANALYSIS](ARCHITECTURE_ANALYSIS.md) - 架构文档

### 外部资源
- [PyQt6 文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [PyInstaller 文档](https://pyinstaller.org/en/stable/)
- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

---

## 快捷键速查

### 应用内
- `Ctrl+R` - 重新加载 WebUI
- `Ctrl+O` - 在浏览器中打开
- `Ctrl+Q` - 退出应用
- `F11` - 全屏模式
- `F12` - 开发者工具

### 开发
- `Ctrl+C` - 停止开发服务器
- `Ctrl+Z` - 暂停进程
- `Ctrl+\` - 强制退出

---

<div align="center">

**💡 提示**: 使用 `Ctrl+F` 快速搜索本文档

[返回顶部](#快速参考指南)

</div>
