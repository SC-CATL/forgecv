"""崩溃落盘：JSON 结构与钩子安装。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from forgecv.platform.observability.crash import install_excepthook, write_dump


def test_write_dump_contains_traceback(tmp_path: Path) -> None:
    """异常类型、消息与调用栈都写入文件。"""
    try:
        raise ValueError("坏值")
    except ValueError as exc:
        path = write_dump(ValueError, exc, exc.__traceback__, tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["type"] == "ValueError"
    assert "坏值" in payload["message"]
    assert "ValueError" in payload["traceback"]


def test_install_excepthook_writes_dump(tmp_path: Path) -> None:
    """安装后未捕获异常会落盘，并保留原钩子。"""
    original = sys.excepthook
    sys.excepthook = lambda *_args: None
    try:
        install_excepthook(tmp_path)
        try:
            raise RuntimeError("崩溃")
        except RuntimeError as exc:
            sys.excepthook(type(exc), exc, exc.__traceback__)
    finally:
        sys.excepthook = original
    assert list(tmp_path.glob("crash-*.json"))
