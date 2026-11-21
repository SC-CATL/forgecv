"""Qt 绑定唯一入口：业务代码只从这里导入 Qt 符号。"""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QObject, Qt, Signal, Slot

BINDING = "PySide6"
QAction = QtGui.QAction

__all__ = [
    "BINDING",
    "QAction",
    "QObject",
    "Qt",
    "QtCore",
    "QtGui",
    "QtWidgets",
    "Signal",
    "Slot",
    "enable_high_dpi",
    "exec_app",
    "exec_dialog",
]


def exec_app(app: QtWidgets.QApplication) -> int:
    """跨 Qt5/Qt6 进入事件循环。"""
    if BINDING == "PySide6":
        return int(app.exec())
    return int(app.exec_())


def exec_dialog(dialog: QtWidgets.QDialog) -> int:
    """跨 Qt5/Qt6 执行模态对话框。"""
    if BINDING == "PySide6":
        return int(dialog.exec())
    return int(dialog.exec_())


def enable_high_dpi() -> None:
    """在创建 QApplication 之前启用高 DPI 支持。"""
    if BINDING == "PySide6":
        policy = Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        QtGui.QGuiApplication.setHighDpiScaleFactorRoundingPolicy(policy)
        return
    QtWidgets.QApplication.setAttribute(getattr(Qt, "AA_EnableHighDpiScaling"), True)  # noqa: B009
    QtWidgets.QApplication.setAttribute(getattr(Qt, "AA_UseHighDpiPixmaps"), True)  # noqa: B009
