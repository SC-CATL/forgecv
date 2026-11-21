"""崩溃落盘：未捕获异常写本地 JSON，保留原钩子。"""

from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import TracebackType


def crash_dir() -> Path:
    """崩溃目录固定在 LOCALAPPDATA 下。"""
    base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    path = base / "ForgeCV" / "crashes"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_dump(
    exc_type: type[BaseException],
    exc: BaseException,
    traceback_obj: TracebackType | None,
    directory: Path,
) -> Path:
    """把异常与调用栈写成 JSON。"""
    moment = datetime.now(timezone.utc)
    path = directory / f"crash-{moment:%Y%m%dT%H%M%S%fZ}.json"
    payload = {
        "type": exc_type.__name__,
        "message": str(exc),
        "traceback": "".join(traceback.format_exception(exc_type, exc, traceback_obj)),
        "created_at": moment.isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def install_excepthook(directory: Path | None = None) -> Path:
    """安装全局钩子，返回崩溃目录。"""
    target = directory or crash_dir()
    previous = sys.excepthook

    def _hook(
        exc_type: type[BaseException],
        exc: BaseException,
        traceback_obj: TracebackType | None,
    ) -> None:
        try:
            path = write_dump(exc_type, exc, traceback_obj, target)
            print(f"崩溃信息已写入：{path}", file=sys.stderr)
        finally:
            previous(exc_type, exc, traceback_obj)

    sys.excepthook = _hook
    return target
