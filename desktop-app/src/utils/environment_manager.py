#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行环境管理器
负责在不同来源之间解析符合要求的 Python 3.10 解释器
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

try:
    from src.utils.runtime_state import load_runtime_state
except ImportError:  # pragma: no cover - 打包场景
    from utils.runtime_state import load_runtime_state

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """统一管理 Python 环境解析"""

    REQUIRED_MAJOR = "3.10"
    DEFAULT_RUNTIME_SUBDIR = "python-env"

    def __init__(self, project_root: Path, data_dir: Path):
        self.project_root = Path(project_root)
        self.data_dir = Path(data_dir)
        self.runtime_state = load_runtime_state(self.data_dir) or {}
        self._python_exe: Optional[Path] = None
        self._python_source: Optional[str] = None
        self._checked_candidates: List[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """重新读取运行时状态，清空缓存"""
        self.runtime_state = load_runtime_state(self.data_dir) or {}
        self._python_exe = None
        self._python_source = None
        self._checked_candidates.clear()

    def get_python_executable(self) -> Path:
        """返回满足要求的 Python 3.10 解释器路径"""
        if self._python_exe and self._python_exe.exists():
            return self._python_exe

        python_path = self._resolve_python_executable()
        if python_path:
            self._python_exe = python_path
            return python_path

        raise RuntimeError(self._build_resolution_error())

    def describe_source(self) -> Optional[str]:
        """返回当前解析到的 Python 来源描述"""
        return self._python_source

    # ------------------------------------------------------------------
    # Resolution helpers
    # ------------------------------------------------------------------
    def _resolve_python_executable(self) -> Optional[Path]:
        resolvers = [
            self._python_from_runtime_state,
            self._python_from_data_dir,
            self._python_from_project_venv,
            self._python_from_sys_executable,
            self._python_from_system_install,
        ]

        for resolver in resolvers:
            resolved = resolver()
            if resolved:
                path, source = resolved
                logger.info("✓ 使用 Python 解释器 (%s): %s", source, path)
                self._python_source = source
                return path

        return None

    def _python_from_runtime_state(self) -> Optional[Tuple[Path, str]]:
        env_info = self.runtime_state.get("python_env") if isinstance(self.runtime_state, dict) else None
        if not env_info:
            return None

        candidates: List[Path] = []
        python_exe = env_info.get("python_exe")
        env_path = env_info.get("path")

        if python_exe:
            candidates.append(Path(python_exe))
        if env_path:
            env_root = Path(env_path)
            candidates.extend(self._expand_python_candidates(env_root))

        return self._validate_candidates(candidates, source="runtime_state")

    def _python_from_data_dir(self) -> Optional[Tuple[Path, str]]:
        env_root = self.data_dir / self.DEFAULT_RUNTIME_SUBDIR
        candidates = self._expand_python_candidates(env_root)
        return self._validate_candidates(candidates, source="data_dir")

    def _python_from_project_venv(self) -> Optional[Tuple[Path, str]]:
        venv_root = self.project_root / "venv"
        candidates = self._expand_python_candidates(venv_root)

        # 兼容嵌套 _internal 目录
        internal_root = self.project_root / "_internal" / "venv"
        candidates.extend(self._expand_python_candidates(internal_root))

        return self._validate_candidates(candidates, source="project_venv")

    def _python_from_sys_executable(self) -> Optional[Tuple[Path, str]]:
        current = Path(sys.executable)
        return self._validate_candidates([current], source="current_process")

    def _python_from_system_install(self) -> Optional[Tuple[Path, str]]:
        candidates: List[Path] = []
        # 常见的 Windows 安装目录
        windows_paths = [
            r"C:\\Python310\\python.exe",
            r"C:\\Program Files\\Python310\\python.exe",
            r"C:\\Program Files (x86)\\Python310\\python.exe",
        ]
        for path in windows_paths:
            candidates.append(Path(path))

        # POSIX 平台
        posix_paths = [
            Path("/usr/bin/python3.10"),
            Path("/usr/local/bin/python3.10"),
        ]
        candidates.extend(posix_paths)

        which_python = shutil.which("python3.10")
        if which_python:
            candidates.append(Path(which_python))

        return self._validate_candidates(candidates, source="system")

    # ------------------------------------------------------------------
    # Candidate utilities
    # ------------------------------------------------------------------
    def _expand_python_candidates(self, env_root: Path) -> List[Path]:
        candidates: List[Path] = []
        if not env_root:
            return candidates

        if sys.platform == "win32":
            candidates.append(env_root / "Scripts" / "python.exe")
            candidates.append(env_root / "python.exe")
        else:
            candidates.append(env_root / "bin" / "python3.10")
            candidates.append(env_root / "bin" / "python")
            candidates.append(env_root / "python3.10")

        return candidates

    def _validate_candidates(self, candidates: Sequence[Path], source: str) -> Optional[Tuple[Path, str]]:
        for candidate in candidates:
            if not candidate:
                continue
            candidate = candidate.resolve()
            if str(candidate) in self._checked_candidates:
                continue
            self._checked_candidates.append(str(candidate))

            if not candidate.exists():
                continue

            version = self._read_python_version(candidate)
            if not version:
                continue

            if self.REQUIRED_MAJOR in version:
                return candidate, source

            logger.warning("忽略 Python %s (来源 %s)，未匹配 %s", version.strip(), source, self.REQUIRED_MAJOR)

        return None

    def _read_python_version(self, python_path: Path) -> Optional[str]:
        try:
            result = subprocess.run(
                [str(python_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            output = (result.stdout or result.stderr or "").strip()
            if not output:
                return None
            return output
        except (OSError, subprocess.SubprocessError) as exc:
            logger.debug("读取 Python 版本失败 %s: %s", python_path, exc)
            return None

    # ------------------------------------------------------------------
    # Error helpers
    # ------------------------------------------------------------------
    def _build_resolution_error(self) -> str:
        checked = "\n".join(f"  - {path}" for path in self._checked_candidates)
        message = [
            "未找到可用的 Python 3.10 解释器。",
            "请确认以下任一条件已满足:",
            "1. 首次运行向导已经完成，并在 data/python-env 中准备好 Python", 
            "2. stable-diffusion-webui 根目录下存在 venv (Python 3.10)",
            "3. 系统已安装 Python 3.10 并可通过 python3.10 访问",
        ]
        if checked:
            message.append("\n已检查的候选路径:\n" + checked)
        return "\n".join(message)
