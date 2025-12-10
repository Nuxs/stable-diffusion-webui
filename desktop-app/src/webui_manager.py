#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WebUI 核心管理器"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable, Dict, Optional

from src.utils.config import Config
from src.download_manager import DownloadManager


class WebUIManager:
    """负责下载、更新和校验 WebUI 核心文件"""

    def __init__(self, data_dir: Path, download_manager: DownloadManager):
        self.data_dir = Path(data_dir)
        self.webui_dir = self.data_dir / "webui"
        self.temp_dir = self.data_dir / "_tmp_webui"
        self.config = Config()
        self.dm = download_manager

    def is_installed(self) -> bool:
        return (self.webui_dir / "launch.py").exists()

    def get_installed_version(self) -> Optional[str]:
        version_file = self.webui_dir / "VERSION"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8").strip()
        return None

    def get_required_version(self) -> Dict:
        info = self.config.get_webui_core()
        if not info:
            raise RuntimeError("components.json 中缺少 webui_core 配置")
        return info

    def ensure_latest(self, progress_callback: Optional[Callable[[int, int], None]] = None) -> Path:
        info = self.get_required_version()
        installed = self.get_installed_version()
        if installed == info.get("version") and self.is_installed():
            return self.webui_dir
        return self.install(info, progress_callback)

    def install(self, info: Dict, progress_callback: Optional[Callable[[int, int], None]] = None) -> Path:
        self._cleanup_temp()
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        filename = info["url"].split("/")[-1].split("?")[0]
        archive_path = self.dm.download_file(
            url=info["url"],
            filename=filename,
            expected_size=info.get("size_bytes"),
            expected_md5=info.get("md5"),
            progress_callback=progress_callback,
            mirrors=info.get("mirrors")
        )

        self.dm.extract_archive(archive_path, self.temp_dir)

        extracted_root = self._detect_extracted_root()
        if self.webui_dir.exists():
            shutil.rmtree(self.webui_dir)
        shutil.move(str(extracted_root), self.webui_dir)
        self._cleanup_temp()

        version_file = self.webui_dir / "VERSION"
        version_file.write_text(info.get("version", "unknown"), encoding="utf-8")
        return self.webui_dir

    def _detect_extracted_root(self) -> Path:
        candidates = [p for p in self.temp_dir.iterdir() if p.is_dir()]
        if len(candidates) == 1:
            return candidates[0]
        return self.temp_dir

    def _cleanup_temp(self) -> None:
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
