"""自绘弹窗：统一视觉、统一按钮语义，不依赖系统原生对话框。"""

from __future__ import annotations

from typing import Any

from forgecv.platform.ui.qt import QtCore, QtWidgets, exec_dialog

_BUTTONS = {"confirm": "确定", "cancel": "取消", "close": "关闭"}


class _CardDialog(QtWidgets.QDialog):
    """自绘卡片式弹窗，样式全部来自全局 QSS。"""

    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        title: str,
        body: str,
        buttons: list[tuple[str, str, str]],
    ) -> None:
        super().__init__(parent)
        self._result = "close"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        card = QtWidgets.QFrame(self)
        card.setObjectName("Card")
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setSpacing(12)
        heading = QtWidgets.QLabel(title, card)
        heading.setObjectName("PageTitle")
        text = QtWidgets.QLabel(body, card)
        text.setWordWrap(True)
        card_layout.addWidget(heading)
        card_layout.addWidget(text)
        layout.addWidget(card)

        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        for label, role, result in buttons:
            button = QtWidgets.QPushButton(label, self)
            if role:
                button.setObjectName(role)
            button.clicked.connect(lambda _checked=False, value=result: self._finish(value))
            row.addWidget(button)
        layout.addLayout(row)

    def _finish(self, result: str) -> None:
        """记录语义结果并关闭。"""
        self._result = result
        self.accept()

    def outcome(self) -> str:
        """返回语义结果，默认关闭。"""
        return self._result


class DialogService(QtCore.QObject):
    """封装确认、提示、错误三类弹窗。"""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """记录父窗口，便于居中与模态。"""
        super().__init__(parent)
        self._parent = parent

    def set_parent(self, parent: QtWidgets.QWidget) -> None:
        """主窗口创建后回填父窗口。"""
        self._parent = parent

    def confirm(self, title: str, body: str, **labels: Any) -> bool:
        """确认框，仅在用户点确认时返回 True。"""
        buttons = [
            (labels.get("cancel", _BUTTONS["cancel"]), "Secondary", "cancel"),
            (labels.get("confirm", _BUTTONS["confirm"]), "", "confirm"),
        ]
        dialog = _CardDialog(self._parent, title, body, buttons)
        exec_dialog(dialog)
        return dialog.outcome() == "confirm"

    def notify(self, title: str, body: str) -> None:
        """单按钮提示。"""
        self._open(title, body, [(_BUTTONS["close"], "", "close")])

    def error(self, title: str, body: str) -> None:
        """错误提示，危险色按钮。"""
        self._open(title, body, [(_BUTTONS["close"], "Danger", "close")])

    def _open(self, title: str, body: str, buttons: list[tuple[str, str, str]]) -> str:
        """打开弹窗并返回语义结果。"""
        dialog = _CardDialog(self._parent, title, body, buttons)
        exec_dialog(dialog)
        return dialog.outcome()
