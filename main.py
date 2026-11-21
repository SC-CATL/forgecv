"""根目录启动器：转发到 forgecv.__main__:main。"""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    """未安装包时把 src/ 加入导入路径。"""
    src = Path(__file__).resolve().parent / "src"
    if src.is_dir() and str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main() -> int:
    """启动应用并返回退出码。"""
    _ensure_src_on_path()
    try:
        from forgecv.__main__ import main as app_main
    except ImportError as exc:  # 路径兜底需要延迟导入
        print(f"无法导入 forgecv，请先执行 uv sync：{exc}", file=sys.stderr)
        return 2
    return app_main()


if __name__ == "__main__":
    raise SystemExit(main())
