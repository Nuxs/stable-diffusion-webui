# -*- mode: python ; coding: utf-8 -*-
# 完善的目录模式打包配置 - 适用于在其他电脑上直接运行
# 目录模式比单文件模式更可靠，DLL 加载更容易，启动更快

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_dynamic_libs

block_cipher = None

# 收集 PyQt6 的所有数据、二进制文件和隐藏导入
# 注意：collect_all 可能会在构建时产生警告（DLL 加载失败），这是正常的，不影响最终打包
# 这是因为 PyInstaller 在隔离的子进程中尝试导入 PyQt6.QtCore 来获取库信息
# 如果失败，我们会手动收集所有必要的文件，确保最终打包结果完整
datas = []
binaries = []
hiddenimports = []

try:
    # 尝试使用 collect_all，但捕获所有异常（包括 DLL 加载失败）
    datas, binaries, hiddenimports = collect_all('PyQt6')
    print(f"✓ collect_all('PyQt6') 成功")
except ImportError as e:
    # DLL 加载失败是预期的，继续手动收集
    print(f"⚠ collect_all('PyQt6') 在分析阶段无法加载 DLL（这是正常的）: {e}")
    print("   将继续手动收集所有必要的 PyQt6 文件...")
except Exception as e:
    print(f"⚠ collect_all('PyQt6') 失败: {e}")
    print("   将继续手动收集所有必要的 PyQt6 文件...")

# 添加 PyQt6 插件目录（非常重要！）
try:
    import PyQt6
    pyqt6_path = os.path.dirname(PyQt6.__file__)
    
    # 添加 Qt6/bin 目录下的所有 DLL
    qt6_bin_path = os.path.join(pyqt6_path, 'Qt6', 'bin')
    if os.path.exists(qt6_bin_path):
        for dll_file in os.listdir(qt6_bin_path):
            if dll_file.endswith('.dll'):
                dll_full_path = os.path.join(qt6_bin_path, dll_file)
                # 避免重复添加
                if (dll_full_path, '.') not in binaries:
                    binaries.append((dll_full_path, '.'))
    
    # 添加 Qt6/plugins 目录（关键！）
    qt6_plugins_path = os.path.join(pyqt6_path, 'Qt6', 'plugins')
    if os.path.exists(qt6_plugins_path):
        for root, dirs, files in os.walk(qt6_plugins_path):
            for file in files:
                if file.endswith(('.dll', '.so')):
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(root, qt6_plugins_path)
                    dest_path = os.path.join('PyQt6', 'Qt6', 'plugins', rel_path) if rel_path != '.' else os.path.join('PyQt6', 'Qt6', 'plugins')
                    # 避免重复添加
                    if (src_path, dest_path) not in datas:
                        datas.append((src_path, dest_path))
    
    # 添加 Qt6/qml 目录（WebEngine 需要）
    qt6_qml_path = os.path.join(pyqt6_path, 'Qt6', 'qml')
    if os.path.exists(qt6_qml_path):
        qml_tuple = (qt6_qml_path, 'PyQt6/Qt6/qml')
        if qml_tuple not in datas:
            datas.append(qml_tuple)
        
except Exception as e:
    print(f"警告: 无法添加 PyQt6 资源: {e}")

# 确保包含所有必要的 DLL
try:
    pyqt6_binaries = collect_dynamic_libs('PyQt6')
    for binary in pyqt6_binaries:
        if binary not in binaries:
            binaries.append(binary)
except Exception as e:
    print(f"警告: collect_dynamic_libs('PyQt6') 失败: {e}")

# 注意：Qt6Core.dll 可能需要 ICU DLL，但通常系统已包含
# 如果运行时仍然出现 ucnv_open 错误，可能需要：
# 1. 禁用 UPX 压缩（已在 EXE 和 COLLECT 中设置 upx=False）
# 2. 确保 Visual C++ Redistributable 已安装
# 3. 检查系统 ICU DLL 是否可用（通常在 C:\Windows\System32）

# 添加资源文件
spec_dir = os.path.dirname(os.path.abspath(SPEC))
resources_path = os.path.join(spec_dir, 'resources')
if os.path.exists(resources_path):
    for root, dirs, files in os.walk(resources_path):
        for file in files:
            if file != 'README.md':
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, resources_path)
                datas.append((src_path, os.path.join('resources', os.path.dirname(rel_path)) if os.path.dirname(rel_path) else 'resources'))

# 添加 stable-diffusion-webui 项目核心文件
# 项目根目录是 desktop-app 的父目录
project_root = os.path.dirname(spec_dir)
print(f"项目根目录: {project_root}")

# 需要排除的目录和文件
exclude_dirs = {
    '__pycache__', '.git', 'node_modules',
    'models', 'outputs', 'cache', 'tmp', 'logs',
    'desktop-app', 'build', 'dist', '.idea', '.vscode',
    'repositories'  # repositories 目录通常很大，可以排除
    # 注意：venv 不在排除列表中，因为我们希望打包它
}

exclude_files = {
    '.gitignore', '.gitattributes', '.gitmodules'
}

# 需要打包的核心目录和文件
core_dirs = [
    'modules', 'scripts', 'javascript', 'html', 'configs',
    'extensions-builtin', 'textual_inversion_templates',
    'localizations', 'test'
]

core_files = [
    'launch.py', 'webui.py', 'webui.bat', 'webui.sh', 'webui-user.bat',
    'webui-user.sh', 'webui-macos-env.sh', 'requirements.txt',
    'requirements_versions.txt', 'requirements_npu.txt', 'requirements-test.txt',
    'package.json', 'pyproject.toml', 'LICENSE.txt', 'README.md',
    'CHANGELOG.md', 'CITATION.cff', 'CODEOWNERS', 'params.txt',
    'config.json', 'ui-config.json', 'style.css', 'script.js',
    'screenshot.png', '_typos.toml'
]

# 打包核心目录
for core_dir in core_dirs:
    core_dir_path = os.path.join(project_root, core_dir)
    if os.path.exists(core_dir_path):
        for root, dirs, files in os.walk(core_dir_path):
            # 过滤掉排除的目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            
            for file in files:
                if file not in exclude_files and not file.startswith('.'):
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, project_root)
                    datas.append((src_path, os.path.dirname(rel_path) if os.path.dirname(rel_path) != '.' else '.'))
        print(f"已添加目录: {core_dir}")

# 打包核心文件
for core_file in core_files:
    core_file_path = os.path.join(project_root, core_file)
    if os.path.exists(core_file_path):
        datas.append((core_file_path, '.'))
        print(f"已添加文件: {core_file}")

# 打包其他重要目录（如果存在）
other_dirs = ['embeddings', 'extensions', 'config_states']
for other_dir in other_dirs:
    other_dir_path = os.path.join(project_root, other_dir)
    if os.path.exists(other_dir_path):
        for root, dirs, files in os.walk(other_dir_path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            for file in files:
                if file not in exclude_files and not file.startswith('.'):
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, project_root)
                    datas.append((src_path, os.path.dirname(rel_path) if os.path.dirname(rel_path) != '.' else '.'))
        print(f"已添加目录: {other_dir}")

# 注意：venv环境不直接打包，使用分离式打包方案
# venv将被压缩为7z格式，放在environment/venv.7z
# 应用首次运行时会自动解压
print("=" * 60)
print("分离式打包方案")
print("=" * 60)
print("venv环境不直接打包到exe中（体积过大）")
print("请使用以下步骤创建完整分发包：")
print("1. 运行: python create_environment_package.py 创建环境包")
print("2. 将 environment/venv.7z 复制到打包输出目录")
print("3. 应用首次运行时会自动解压环境")
print("=" * 60)

print(f"已添加 {len([d for d in datas if isinstance(d, tuple) and len(d) == 2])} 个文件/目录到打包列表")

# 添加额外的隐藏导入
hiddenimports += [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtWebEngineCore',
    'requests',
    # 标准库模块
    'pkgutil',
    'importlib',
    'importlib.util',
    'importlib.metadata',
]

# 注意：PyInstaller 在构建时可能会显示关于 PyQt6 DLL 加载的警告
# 这是因为 PyInstaller 尝试在隔离的子进程中导入 PyQt6.QtCore 来获取库信息
# 这个警告是正常的，不会影响最终打包结果，因为我们已经手动收集了所有必要的 DLL 和资源
# 构建会继续正常进行，可以安全地忽略这个警告

# 尝试抑制 Qt 库信息收集警告（如果 PyInstaller 支持）
# 注意：这不会完全消除警告，但可以减少输出
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='PyInstaller')

# 添加配置文件
config_dir = os.path.join(spec_dir, 'config')
if os.path.exists(config_dir):
    for config_file in os.listdir(config_dir):
        if config_file.endswith('.json'):
            datas.append((os.path.join(config_dir, config_file), 'config'))
    print(f"✓ 已添加配置文件")

# 添加新的隐藏导入（重构后的模块）
hiddenimports += [
    'src.launcher',
    'src.system_detector',
    'src.download_manager',
    'src.model_manager',
    'src.first_run_wizard',
    'src.utils.portable_python',
]

a = Analysis(
    ['src/launcher.py'],  # 🔄 更新入口点：main.py -> launcher.py
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={
        # 尝试配置 PyQt6 hook 跳过库信息收集（如果支持）
        # 注意：这取决于 PyInstaller 版本，可能不生效
    },
    runtime_hooks=['rthook_pyqt6_fix.py'],  # 使用运行时 hook 修复 DLL 加载
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 目录模式：exe 和依赖文件分开，更可靠
# 重要：exclude_binaries=True 必须设置，且第三个参数必须是空列表 []
exe = EXE(
    pyz,
    a.scripts,
    [],  # 空列表表示不包含二进制文件，强制目录模式
    exclude_binaries=True,  # 不打包二进制文件到 exe，使用目录模式
    name='StableDiffusionWebUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用 UPX 压缩，避免 DLL 加载问题（特别是 Qt6Core.dll 的 ucnv_open 错误）
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' if os.path.exists('resources/icon.ico') else None,
)

# 收集所有文件到目录
# 注意：只有当 EXE 的 exclude_binaries=True 时，COLLECT 才会被执行
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # 禁用 UPX 压缩，避免 DLL 加载问题
    upx_exclude=[],
    name='StableDiffusionWebUI',
)
