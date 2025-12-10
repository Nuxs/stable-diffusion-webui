#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""运行时状态读写工具"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


RUNTIME_STATE_FILENAME = "runtime_state.json"


def _state_file(data_dir: Path) -> Path:
    return Path(data_dir) / RUNTIME_STATE_FILENAME


def load_runtime_state(data_dir: Path) -> Optional[Dict[str, Any]]:
    """从 data 目录读取运行时状态"""
    path = _state_file(data_dir)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:
        logger.warning("加载 runtime_state 失败: %s", exc)
        return None


def save_runtime_state(data_dir: Path, state: Dict[str, Any]) -> None:
    """写入运行时状态"""
    path = _state_file(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.error("保存 runtime_state 失败: %s", exc)


def update_runtime_state(data_dir: Path, **kwargs: Any) -> Dict[str, Any]:
    """合并并返回最新状态"""
    state = load_runtime_state(data_dir) or {}
    state.update(kwargs)
    save_runtime_state(data_dir, state)
    return state
