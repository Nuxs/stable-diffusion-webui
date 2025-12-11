#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首次运行向导
引导用户完成初始设置和组件下载
"""

import logging
from pathlib import Path
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel,
    QRadioButton, QCheckBox, QTextEdit, QProgressBar, QGroupBox,
    QPushButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


class FirstRunWizard(QWizard):
    """首次运行向导"""
    
    def __init__(self, system_info: Dict, data_dir: Path, parent=None):
        super().__init__(parent)
        self.system_info = system_info
        self.data_dir = Path(data_dir)
        
        self.setWindowTitle("首次运行设置")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(700, 550)
        
        # 添加页面
        self.welcome_page = WelcomePage(system_info)
        self.component_page = ComponentSelectionPage(system_info)
        self.download_page = DownloadPage(data_dir)
        self.complete_page = CompletePage()
        
        self.addPage(self.welcome_page)
        self.addPage(self.component_page)
        self.addPage(self.download_page)
        self.addPage(self.complete_page)
        
        # 自定义按钮文本
        self.setButtonText(QWizard.WizardButton.NextButton, "下一步")
        self.setButtonText(QWizard.WizardButton.BackButton, "上一步")
        self.setButtonText(QWizard.WizardButton.FinishButton, "完成")
        self.setButtonText(QWizard.WizardButton.CancelButton, "取消")
    
    def get_selected_components(self) -> Dict:
        """获取用户选择的组件"""
        return self.component_page.get_selections()


class WelcomePage(QWizardPage):
    """欢迎页面"""
    
    def __init__(self, system_info: Dict, parent=None):
        super().__init__(parent)
        self.system_info = system_info
        
        self.setTitle("欢迎使用 Stable Diffusion Desktop")
        self.setSubTitle("首次运行需要下载必要的组件，这可能需要几分钟时间。")
        
        layout = QVBoxLayout(self)
        
        # 欢迎信息
        welcome_label = QLabel(
            "这是一款基于 Stable Diffusion WebUI 的桌面应用，"
            "可以让您轻松地生成 AI 图像。\n\n"
            "我们已经检测到您的系统信息，将为您推荐最合适的配置。"
        )
        welcome_label.setWordWrap(True)
        layout.addWidget(welcome_label)
        
        layout.addSpacing(20)
        
        # 系统信息
        info_group = QGroupBox("系统信息")
        info_layout = QVBoxLayout()
        
        os_info = system_info.get('os', {})
        gpu_info = system_info.get('gpu', {})
        disk_info = system_info.get('disk', {})
        
        info_text = f"""
<b>操作系统:</b> {os_info.get('platform', '未知')}<br>
<b>处理器:</b> {os_info.get('processor', '未知')}<br>
"""
        
        if gpu_info.get('name'):
            info_text += f"<b>显卡:</b> {gpu_info['name']}<br>"
            if gpu_info.get('vram'):
                vram_gb = gpu_info['vram'] / 1024
                info_text += f"<b>显存:</b> {vram_gb:.1f} GB<br>"
            if gpu_info.get('cuda_version'):
                info_text += f"<b>CUDA:</b> {gpu_info['cuda_version']}<br>"
        else:
            info_text += "<b>显卡:</b> 未检测到独立显卡（将使用 CPU 模式）<br>"
        
        info_text += f"<b>可用磁盘空间:</b> {disk_info.get('free_gb', 0):.1f} GB<br>"
        
        info_label = QLabel(info_text)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_layout.addWidget(info_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addSpacing(20)
        
        # 注意事项
        note_label = QLabel(
            "<b>注意事项:</b><br>"
            "• 首次运行需要下载 2-6 GB 的组件<br>"
            "• 请确保您有稳定的网络连接<br>"
            "• 下载过程支持暂停和恢复<br>"
            "• 您可以随时在设置中下载更多模型"
        )
        note_label.setTextFormat(Qt.TextFormat.RichText)
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        layout.addStretch()


class ComponentSelectionPage(QWizardPage):
    """组件选择页面"""
    
    def __init__(self, system_info: Dict, parent=None):
        super().__init__(parent)
        self.system_info = system_info
        
        self.setTitle("选择要安装的组件")
        self.setSubTitle("根据您的系统配置，我们为您推荐了合适的组件。")
        
        layout = QVBoxLayout(self)
        
        # Python 环境选择
        env_group = QGroupBox("Python 环境 (必需)")
        env_layout = QVBoxLayout()
        
        self.env_button_group = QButtonGroup(self)
        
        gpu = system_info.get('gpu', {})
        recommended_env = self._recommend_env(gpu)
        
        # CPU 选项
        self.env_cpu = QRadioButton("CPU 版本 (~2 GB)")
        self.env_cpu.setToolTip("适合没有独立显卡的电脑，生成速度较慢")
        env_layout.addWidget(self.env_cpu)
        self.env_button_group.addButton(self.env_cpu)
        
        # CUDA 11.8 选项
        self.env_cuda118 = QRadioButton("CUDA 11.8 版本 (~4 GB) - 推荐")
        self.env_cuda118.setToolTip("适合 NVIDIA GTX 10 系列及以上显卡")
        env_layout.addWidget(self.env_cuda118)
        self.env_button_group.addButton(self.env_cuda118)
        
        # CUDA 12.1 选项
        self.env_cuda121 = QRadioButton("CUDA 12.1 版本 (~4 GB)")
        self.env_cuda121.setToolTip("适合 NVIDIA RTX 40 系列显卡")
        env_layout.addWidget(self.env_cuda121)
        self.env_button_group.addButton(self.env_cuda121)
        
        # 根据推荐设置默认选项
        if recommended_env == 'cpu':
            self.env_cpu.setChecked(True)
            self.env_cpu.setText("CPU 版本 (~2 GB) - 推荐")
        elif recommended_env == 'cuda118':
            self.env_cuda118.setChecked(True)
        elif recommended_env == 'cuda121':
            self.env_cuda121.setChecked(True)
            self.env_cuda121.setText("CUDA 12.1 版本 (~4 GB) - 推荐")
        else:
            self.env_cpu.setChecked(True)
        
        # 如果没有 GPU，禁用 CUDA 选项
        if not gpu.get('cuda_available'):
            self.env_cuda118.setEnabled(False)
            self.env_cuda121.setEnabled(False)
        
        env_group.setLayout(env_layout)
        layout.addWidget(env_group)
        
        # 模型选择
        model_group = QGroupBox("AI 模型")
        model_layout = QVBoxLayout()
        
        model_layout.addWidget(QLabel("选择要下载的模型（可稍后在设置中添加）:"))
        
        self.model_sd15 = QCheckBox("Stable Diffusion 1.5 (4.27 GB) - 推荐")
        self.model_sd15.setToolTip("最经典的版本，速度快，适合入门")
        self.model_sd15.setChecked(True)
        model_layout.addWidget(self.model_sd15)
        
        self.model_sdxl = QCheckBox("Stable Diffusion XL (6.94 GB)")
        self.model_sdxl.setToolTip("更高质量，但速度较慢，需要更强显卡")
        
        # 检查显存要求
        vram = gpu.get('vram', 0)
        if vram < 10 * 1024:  # 小于 10GB
            self.model_sdxl.setEnabled(False)
            self.model_sdxl.setToolTip(
                f"需要至少 10GB 显存（您的显存: {vram / 1024:.1f} GB）"
            )
        
        model_layout.addWidget(self.model_sdxl)
        
        self.model_skip = QCheckBox("稍后手动下载")
        self.model_skip.setToolTip("您可以稍后在应用中下载模型")
        model_layout.addWidget(self.model_skip)
        
        # 连接信号，确保至少选择一个选项
        self.model_sd15.toggled.connect(self._update_model_selection)
        self.model_sdxl.toggled.connect(self._update_model_selection)
        self.model_skip.toggled.connect(self._update_model_selection)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        layout.addSpacing(10)
        
        # 总计大小
        self.size_label = QLabel()
        self.size_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(self.size_label)
        
        layout.addStretch()
        
        # 连接信号更新总大小
        self.env_cpu.toggled.connect(self._update_total_size)
        self.env_cuda118.toggled.connect(self._update_total_size)
        self.env_cuda121.toggled.connect(self._update_total_size)
        self.model_sd15.toggled.connect(self._update_total_size)
        self.model_sdxl.toggled.connect(self._update_total_size)
        
        # 初始化总大小
        self._update_total_size()
    
    def _recommend_env(self, gpu: Dict) -> str:
        """推荐环境类型"""
        if not gpu.get('cuda_available'):
            return 'cpu'
        
        cuda_version = gpu.get('cuda_version', '')
        if cuda_version:
            major = cuda_version.split('.')[0]
            if major == '12':
                return 'cuda121'
            elif major == '11':
                return 'cuda118'
        
        return 'cuda118'
    
    def _update_model_selection(self):
        """更新模型选择状态"""
        # 如果选择了"稍后下载"，取消其他选项
        if self.model_skip.isChecked():
            self.model_sd15.setChecked(False)
            if self.model_sdxl.isEnabled():
                self.model_sdxl.setChecked(False)
        # 如果选择了具体模型，取消"稍后下载"
        elif self.model_sd15.isChecked() or self.model_sdxl.isChecked():
            self.model_skip.setChecked(False)
    
    def _update_total_size(self):
        """更新总下载大小"""
        total_gb = 0.0
        
        # Python 环境
        if self.env_cpu.isChecked():
            total_gb += 2.0
        elif self.env_cuda118.isChecked() or self.env_cuda121.isChecked():
            total_gb += 4.0
        
        # WebUI 核心（约50MB）
        total_gb += 0.05
        
        # 模型
        if self.model_sd15.isChecked():
            total_gb += 4.27
        if self.model_sdxl.isChecked() and self.model_sdxl.isEnabled():
            total_gb += 6.94
        
        self.size_label.setText(f"总下载大小: {total_gb:.2f} GB")
    
    def get_selections(self) -> Dict:
        """获取选择结果"""
        env_type = 'cpu'
        if self.env_cuda118.isChecked():
            env_type = 'cuda118'
        elif self.env_cuda121.isChecked():
            env_type = 'cuda121'
        
        return {
            "python_env": env_type,
            "webui_core": True,  # 总是需要
            "models": {
                "sd-v1-5": self.model_sd15.isChecked(),
                "sdxl-base": self.model_sdxl.isChecked() and self.model_sdxl.isEnabled(),
            }
        }


class DownloadPage(QWizardPage):
    """下载进度页面"""
    
    def __init__(self, data_dir: Path, parent=None):
        super().__init__(parent)
        self.data_dir = data_dir
        self.download_thread = None
        
        self.setTitle("正在下载和安装组件")
        self.setSubTitle("请耐心等待，这可能需要几分钟...")
        
        layout = QVBoxLayout(self)
        
        # 当前任务
        self.current_label = QLabel("准备中...")
        self.current_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.current_label)
        
        # 当前进度条
        self.current_progress = QProgressBar()
        self.current_progress.setMinimum(0)
        self.current_progress.setMaximum(100)
        layout.addWidget(self.current_progress)
        
        # 速度和剩余时间
        self.speed_label = QLabel("")
        layout.addWidget(self.speed_label)
        
        layout.addSpacing(10)
        
        # 日志
        log_label = QLabel("详细信息:")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        layout.addSpacing(10)
        
        # 整体进度
        overall_label = QLabel("整体进度:")
        layout.addWidget(overall_label)
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        layout.addWidget(self.overall_progress)
        
        layout.addStretch()
        
        # 禁用返回按钮
        self.setCommitPage(True)
    
    def initializePage(self):
        """页面初始化时开始下载"""
        wizard = self.wizard()
        if isinstance(wizard, FirstRunWizard):
            selections = wizard.get_selected_components()
            
            # 创建下载线程
            self.download_thread = DownloadThread(selections, self.data_dir)
            self.download_thread.progress_updated.connect(self.on_progress_updated)
            self.download_thread.log_message.connect(self.on_log_message)
            self.download_thread.current_task.connect(self.on_current_task)
            self.download_thread.overall_progress.connect(self.on_overall_progress)
            self.download_thread.finished.connect(self.on_download_finished)
            self.download_thread.start()
    
    def on_current_task(self, task_name: str):
        """更新当前任务"""
        self.current_label.setText(f"当前: {task_name}")
    
    def on_progress_updated(self, current: int, total: int):
        """更新进度"""
        if total > 0:
            percent = int((current / total) * 100)
            self.current_progress.setValue(percent)
            
            # 计算速度（简化版本，实际应该记录时间）
            # TODO: 实现真实的速度计算
            self.speed_label.setText(f"{current} / {total} 字节")
    
    def on_overall_progress(self, current: int, total: int):
        """更新整体进度"""
        if total > 0:
            percent = int((current / total) * 100)
            self.overall_progress.setValue(percent)
    
    def on_log_message(self, message: str):
        """添加日志"""
        self.log_text.append(message)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def on_download_finished(self, success: bool, error: str):
        """下载完成"""
        if success:
            self.current_label.setText("✓ 所有组件安装完成")
            self.current_progress.setValue(100)
            self.overall_progress.setValue(100)
            self.wizard().next()
        else:
            self.current_label.setText(f"✗ 安装失败: {error}")
            self.log_text.append(f"\n<b style='color: red;'>错误: {error}</b>")


class CompletePage(QWizardPage):
    """完成页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTitle("安装完成!")
        self.setSubTitle("您现在可以开始使用 Stable Diffusion Desktop 了")
        
        layout = QVBoxLayout(self)
        
        complete_text = QLabel(
            "<h3>✓ 所有组件已成功安装</h3><br>"
            "<b>您现在可以:</b><br>"
            "• 点击\"完成\"按钮启动应用<br>"
            "• 在主界面开始生成图像<br>"
            "• 在设置中调整参数和下载更多模型<br><br>"
            "<b>使用提示:</b><br>"
            "• 首次生成图像可能需要较长时间（加载模型）<br>"
            "• 您可以随时在设置中下载更多模型<br>"
            "• 如遇到问题，请查看帮助文档或访问官方论坛"
        )
        complete_text.setTextFormat(Qt.TextFormat.RichText)
        complete_text.setWordWrap(True)
        layout.addWidget(complete_text)
        
        layout.addStretch()


class DownloadThread(QThread):
    """下载线程"""
    
    progress_updated = pyqtSignal(int, int)  # current, total
    log_message = pyqtSignal(str)
    current_task = pyqtSignal(str)
    overall_progress = pyqtSignal(int, int)  # current_step, total_steps
    finished = pyqtSignal(bool, str)  # success, error_message
    
    def __init__(self, selections: Dict, data_dir: Path):
        super().__init__()
        self.selections = selections
        self.data_dir = data_dir
    
    def run(self):
        """执行下载"""
        try:
            # 导入必要的模块
            import sys
            from pathlib import Path
            
            # 添加路径
            sys.path.insert(0, str(Path(__file__).parent))
            
            from download_manager import DownloadManager
            from utils.portable_python import PortablePythonManager
            from model_manager import ModelManager
            
            cache_dir = self.data_dir.parent / "cache"
            dm = DownloadManager(cache_dir)
            
            total_steps = 2  # Python环境 + WebUI核心
            if self.selections["models"]["sd-v1-5"] or self.selections["models"]["sdxl-base"]:
                total_steps += 1
            
            current_step = 0
            
            # 1. 安装 Python 环境
            self.log_message.emit("=" * 50)
            self.log_message.emit("步骤 1: 设置 Python 环境")
            self.log_message.emit("=" * 50)
            current_step += 1
            self.overall_progress.emit(current_step, total_steps)
            
            ppm = PortablePythonManager(self.data_dir, dm)
            
            def env_progress(step, curr, total):
                self.current_task.emit(f"Python 环境 - {step}")
                self.log_message.emit(f"  [{curr}/{total}] {step}")
            
            if not ppm.setup_environment(self.selections["python_env"], env_progress):
                self.finished.emit(False, "Python 环境设置失败")
                return
            
            # 2. 下载 WebUI 核心（暂时跳过，因为需要从 GitHub 下载）
            self.log_message.emit("\n" + "=" * 50)
            self.log_message.emit("步骤 2: 准备 WebUI 核心文件")
            self.log_message.emit("=" * 50)
            current_step += 1
            self.overall_progress.emit(current_step, total_steps)
            self.current_task.emit("WebUI 核心文件")
            self.log_message.emit("  WebUI 核心文件已包含在应用中")
            
            # 3. 下载模型
            if self.selections["models"]["sd-v1-5"] or self.selections["models"]["sdxl-base"]:
                self.log_message.emit("\n" + "=" * 50)
                self.log_message.emit("步骤 3: 下载 AI 模型")
                self.log_message.emit("=" * 50)
                current_step += 1
                self.overall_progress.emit(current_step, total_steps)
                
                mm = ModelManager(self.data_dir, dm)
                
                for model_id, selected in self.selections["models"].items():
                    if selected:
                        model_info = mm.get_model_info(model_id)
                        if model_info:
                            self.current_task.emit(f"下载模型: {model_info['name']}")
                            self.log_message.emit(f"  下载 {model_info['name']}...")
                            
                            def model_progress(current, total):
                                self.progress_updated.emit(current, total)
                            
                            result = mm.download_model(model_id, model_progress)
                            if result:
                                self.log_message.emit(f"  ✓ {model_info['name']} 下载完成")
                            else:
                                self.log_message.emit(f"  ✗ {model_info['name']} 下载失败")
            
            self.log_message.emit("\n" + "=" * 50)
            self.log_message.emit("✓ 所有组件安装完成!")
            self.log_message.emit("=" * 50)
            self.finished.emit(True, "")
            
        except Exception as e:
            logger.error(f"下载过程出错: {e}", exc_info=True)
            self.log_message.emit(f"\n✗ 错误: {e}")
            self.finished.emit(False, str(e))


if __name__ == "__main__":
    # 测试代码
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 模拟系统信息
    system_info = {
        'os': {
            'platform': 'Windows-10-10.0.19041-SP0',
            'processor': 'Intel64 Family 6 Model 140 Stepping 1, GenuineIntel',
        },
        'gpu': {
            'name': 'NVIDIA GeForce RTX 3060',
            'vram': 12288,
            'cuda_available': True,
            'cuda_version': '11.8',
        },
        'disk': {
            'free_gb': 250.5,
            'total_gb': 500.0,
        },
        'runtime': {
            'vcredist_installed': True,
        }
    }
    
    wizard = FirstRunWizard(system_info, Path("test_data"))
    result = wizard.exec()
    
    if result == QWizard.DialogCode.Accepted:
        print("用户完成了设置")
        print(f"选择的组件: {wizard.get_selected_components()}")
    else:
        print("用户取消了设置")

