"""设置页：只拼控件与绑定信号，颜色尺寸全部来自令牌。"""

from __future__ import annotations

from forgecv.features.settings.viewmodel import SettingsViewModel
from forgecv.platform.ui.qt import QtWidgets


class SettingsPage(QtWidgets.QWidget):
    """主题设置页。"""

    def __init__(self, view_model: SettingsViewModel) -> None:
        """构建表单并接线。"""
        super().__init__()
        self._vm = view_model
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QtWidgets.QLabel("设置", self)
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        card = QtWidgets.QFrame(self)
        card.setObjectName("Card")
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setSpacing(12)

        label = QtWidgets.QLabel("外观主题", card)
        self._combo = QtWidgets.QComboBox(card)
        self._combo.addItems(self._vm.themes)
        self._combo.setCurrentText(self._vm.selected)
        hint = QtWidgets.QLabel("选择后立即预览，保存后下次启动生效。", card)
        hint.setObjectName("Muted")

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        save = QtWidgets.QPushButton("保存", card)
        save.clicked.connect(self._on_save)
        buttons.addWidget(save)

        card_layout.addWidget(label)
        card_layout.addWidget(self._combo)
        card_layout.addWidget(hint)
        card_layout.addLayout(buttons)
        layout.addWidget(card)

        self._status = QtWidgets.QLabel("", self)
        self._status.setObjectName("Muted")
        layout.addWidget(self._status)
        layout.addStretch(1)

        self._combo.currentTextChanged.connect(self._vm.select)
        self._vm.status_changed.connect(self._status.setText)
        self._vm.themes_changed.connect(self._on_themes)
        self._vm.load()

    def _on_save(self) -> None:
        """保存当前选择。"""
        self._vm.save()

    def _on_themes(self, themes: list[str]) -> None:
        """主题列表变化时重建选项。"""
        self._combo.blockSignals(True)
        self._combo.clear()
        self._combo.addItems(themes)
        self._combo.setCurrentText(self._vm.selected)
        self._combo.blockSignals(False)
