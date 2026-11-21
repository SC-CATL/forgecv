"""开发服务器：迁移一次、启动应用、源码变化自动重启。"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POLL_SECONDS = 0.8


def snapshot() -> dict[str, float]:
    """记录 src 下所有 Python 文件的修改时间。"""
    return {
        str(path): path.stat().st_mtime
        for path in (ROOT / "src").rglob("*.py")
        if path.is_file()
    }


def migrate() -> None:
    """启动前把数据库升到 head。"""
    subprocess.run([sys.executable, str(ROOT / "main.py"), "--migrate"], cwd=ROOT, check=False)


def launch() -> subprocess.Popen[bytes]:
    """拉起应用进程。"""
    return subprocess.Popen([sys.executable, str(ROOT / "main.py"), "--dev"], cwd=ROOT)


def watch(process: subprocess.Popen[bytes]) -> int:
    """轮询源码变化并重启，窗口关闭即退出。"""
    state = snapshot()
    while True:
        code = process.poll()
        if code is not None:
            return code
        time.sleep(POLL_SECONDS)
        current = snapshot()
        if current == state:
            continue
        print("检测到源码变化，重启中 ...")
        process.terminate()
        process.wait(timeout=5)
        state = current
        process = launch()


def main(argv: list[str] | None = None) -> int:
    """解析参数并进入监听循环。"""
    parser = argparse.ArgumentParser(description="开发服务器")
    parser.add_argument("--no-watch", action="store_true", help="关闭自动重启")
    args = parser.parse_args(argv)
    migrate()
    process = launch()
    if args.no_watch:
        return process.wait()
    try:
        return watch(process)
    except KeyboardInterrupt:
        process.terminate()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
