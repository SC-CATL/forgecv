"""主题服务：令牌 -> QSS，支持浅色、深色、高对比与跟随系统。"""

from __future__ import annotations

import sys
from importlib import import_module, resources
from pathlib import Path
from types import ModuleType
from typing import Any, cast

from forgecv.platform.ui.kit import qss
from forgecv.platform.ui.qt import QtCore, QtGui, QtWidgets, Signal

# 3.11+ 用标准库 tomllib，3.10 回退 tomli；统一按模块对象使用，避免版本分支触发静态检查。
_toml: ModuleType = import_module("tomllib" if sys.version_info >= (3, 11) else "tomli")

MODES = ("light", "dark", "high_contrast")
_CACHE: dict[Path, dict[str, Any]] = {}


def tokens_path() -> Path:
    """返回随包分发的令牌文件路径。"""
    return Path(str(resources.files("forgecv.resources").joinpath("tokens.toml")))


def load_tokens(path: Path | None = None) -> dict[str, Any]:
    """读取并缓存令牌文件。"""
    target = path or tokens_path()
    cached = _CACHE.get(target)
    if cached is None:
        with target.open("rb") as handle:
            cached = cast(dict[str, Any], _toml.load(handle))
        _CACHE[target] = cached
    return cached


def flatten(tokens: dict[str, Any]) -> dict[str, str]:
    """把分组令牌展平成 QSS 占位符。"""
    flat: dict[str, str] = {}
    for section in ("space", "radius", "font"):
        for key, value in tokens[section].items():
            flat[f"{section}_{key}"] = str(value)
    flat["font_family"] = str(tokens["font"]["family"])
    return flat


def build_stylesheet(tokens: dict[str, Any], mode: str) -> str:
    """按模式拼装完整 QSS。"""
    values = flatten(tokens)
    values.update({key: str(value) for key, value in tokens[mode].items()})
    return qss.render(values)


class ThemeService(QtCore.QObject):
    """管理当前主题并广播切换事件。"""

    changed = Signal(str)

    def __init__(self, tokens: dict[str, Any] | None = None) -> None:
        """加载令牌，初始模式为 light。"""
        super().__init__()
        self._tokens = tokens or load_tokens()
        self._mode = "light"

    @property
    def current(self) -> str:
        """当前生效的具体模式。"""
        return self._mode

    def available(self) -> tuple[str, ...]:
        """可选模式，含跟随系统。"""
        return (*MODES, "system")

    def resolve(self, name: str) -> str:
        """把 system 解析为具体模式。"""
        if name in MODES:
            return name
        return self._system_mode()

    def apply(self, name: str) -> str:
        """应用主题，返回实际模式。"""
        mode = self.resolve(name)
        app = QtWidgets.QApplication.instance()
        if app is not None:
            cast(QtWidgets.QApplication, app).setStyleSheet(build_stylesheet(self._tokens, mode))
        if mode != self._mode:
            self._mode = mode
            self.changed.emit(mode)
        return mode

    def color(self, key: str) -> str:
        """读取当前模式的颜色令牌。"""
        return str(self._tokens[self._mode][key])

    @staticmethod
    def _system_mode() -> str:
        """读取系统配色，失败时回退浅色。"""
        hints = QtGui.QGuiApplication.styleHints()
        scheme = getattr(hints, "colorScheme", None)
        if scheme is None:
            return "light"
        try:
            return "dark" if scheme() == QtCore.Qt.ColorScheme.Dark else "light"
        except AttributeError:  # pragma: no cover - Qt5 无 colorScheme
            return "light"
