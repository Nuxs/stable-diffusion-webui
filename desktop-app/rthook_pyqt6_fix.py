# PyInstaller runtime hook to fix PyQt6 DLL loading
# 这个 hook 在 PyQt6 模块被导入之前执行，用于设置 DLL 搜索路径
import os
import sys

def add_dll_directory(dll_path):
    """添加 DLL 目录到搜索路径"""
    if not os.path.exists(dll_path):
        return False
    
    dll_dir = os.path.abspath(dll_path)
    
    # 方法1: 使用 AddDllDirectory (Windows 8+, 最可靠)
    try:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        AddDllDirectory = kernel32.AddDllDirectory
        AddDllDirectory.argtypes = [wintypes.LPCWSTR]
        AddDllDirectory.restype = wintypes.HANDLE
        handle = AddDllDirectory(dll_dir)
        if handle:
            return True
    except Exception:
        pass
    
    # 方法2: 使用 os.add_dll_directory (Python 3.8+)
    try:
        os.add_dll_directory(dll_dir)
        return True
    except Exception:
        pass
    
    # 方法3: 添加到 PATH 环境变量（最兼容的方法）
    current_path = os.environ.get('PATH', '')
    if dll_dir not in current_path:
        os.environ['PATH'] = dll_dir + os.pathsep + current_path
        return True
    
    return False

# 确定 DLL 路径
if getattr(sys, 'frozen', False):
    # 打包后的应用
    exe_dir = os.path.dirname(sys.executable)
    
    # 目录模式：检查 _internal 目录
    _internal_dir = os.path.join(exe_dir, '_internal')
    if os.path.exists(_internal_dir):
        # 优先使用 _internal 目录
        dll_paths = [
            os.path.join(_internal_dir, 'PyQt6', 'Qt6', 'bin'),
            _internal_dir,
        ]
    else:
        # 单文件模式：使用 _MEIPASS（如果存在）
        if hasattr(sys, '_MEIPASS'):
            dll_paths = [
                os.path.join(sys._MEIPASS, 'PyQt6', 'Qt6', 'bin'),
                sys._MEIPASS,
            ]
        else:
            # 回退到 exe 目录
            dll_paths = [
                os.path.join(exe_dir, 'PyQt6', 'Qt6', 'bin'),
                exe_dir,
            ]
else:
    # 开发模式：运行时 hook 通常不会在开发模式下执行
    # 但为了安全，我们仍然设置
    app_dir = os.path.dirname(os.path.abspath(__file__))
    dll_paths = [
        os.path.join(app_dir, 'PyQt6', 'Qt6', 'bin'),
        app_dir,
    ]

# 添加所有找到的 DLL 路径
for dll_path in dll_paths:
    if add_dll_directory(dll_path):
        # 成功添加了一个路径，继续尝试其他路径
        pass

# 关键：设置 Qt 插件路径环境变量（Qt 会读取这个）
if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    _internal_dir = os.path.join(exe_dir, '_internal')
    if os.path.exists(_internal_dir):
        qt6_bin = os.path.join(_internal_dir, 'PyQt6', 'Qt6', 'bin')
        qt_plugin_path = os.path.join(_internal_dir, 'PyQt6', 'Qt6', 'plugins')
        
        # 设置 Qt 插件路径（Qt 会读取这个环境变量）
        if os.path.exists(qt_plugin_path):
            os.environ['QT_PLUGIN_PATH'] = qt_plugin_path
            # 也添加到 PATH
            os.environ['PATH'] = qt_plugin_path + os.pathsep + os.environ.get('PATH', '')
        
        # 创建 qt.conf 文件（如果不存在）
        qt_conf_path = os.path.join(qt6_bin, 'qt.conf')
        if not os.path.exists(qt_conf_path) and os.path.exists(qt6_bin):
            try:
                qt_conf_content = """[Paths]
Prefix = PyQt6/Qt6
Plugins = plugins
Translations = translations
"""
                with open(qt_conf_path, 'w', encoding='utf-8') as f:
                    f.write(qt_conf_content)
            except Exception:
                pass  # 如果无法创建，依赖环境变量


