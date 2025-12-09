# PyInstaller runtime hook to fix PyQt6 DLL loading
import os
import sys

# 获取应用目录
if getattr(sys, 'frozen', False):
    # 打包后的应用
    app_dir = sys._MEIPASS
else:
    # 开发模式
    app_dir = os.path.dirname(os.path.abspath(__file__))

# 添加 PyQt6 Qt6/bin 到 DLL 搜索路径
pyqt6_bin_path = os.path.join(app_dir, 'PyQt6', 'Qt6', 'bin')
if os.path.exists(pyqt6_bin_path):
    # Windows 下使用 AddDllDirectory
    try:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        AddDllDirectory = kernel32.AddDllDirectory
        AddDllDirectory.argtypes = [wintypes.LPCWSTR]
        AddDllDirectory.restype = wintypes.HANDLE
        
        # 添加 DLL 目录
        dll_dir = os.path.abspath(pyqt6_bin_path)
        AddDllDirectory(dll_dir)
    except Exception:
        # 如果 AddDllDirectory 失败，使用 PATH
        os.environ['PATH'] = pyqt6_bin_path + os.pathsep + os.environ.get('PATH', '')

# 也尝试从 _internal 目录加载
_internal_path = os.path.join(os.path.dirname(app_dir), '_internal')
if os.path.exists(_internal_path):
    os.environ['PATH'] = _internal_path + os.pathsep + os.environ.get('PATH', '')

