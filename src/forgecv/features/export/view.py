"""导出页：选版本、预检、写 Word。"""

from __future__ import annotations

from typing import Any, cast

from forgecv.features.export.viewmodel import ExportViewModel
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.qt import QtCore, QtWidgets


class ExportPage(QtWidgets.QWidget):
    """整页只有三步：选版本、看预检、导出。"""

    def __init__(self, view_model: ExportViewModel) -> None:
        """构建界面并加载。"""
        super().__init__()
        self._vm = view_model
        area, layout = forms.scroll_form(self)
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(area)
        layout.addWidget(forms.title("导出 Word", area))
        layout.addWidget(forms.muted("使用当前版本的编排与条目，生成可直接投递的 docx。", area))

        card, card_layout = forms.card(area)
        body = forms.form()
        self._version = QtWidgets.QComboBox(card)
        self._version.currentIndexChanged.connect(self._on_version)
        self._folder = QtWidgets.QLineEdit(card)
        self._folder.setText(self._vm.folder_hint())
        body.addRow("简历版本", self._version)
        body.addRow("输出目录", self._folder)
        card_layout.addLayout(body)
        self._checks = forms.muted("", card)
        self._checks.setWordWrap(True)
        card_layout.addWidget(self._checks)
        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        export = forms.button("导出 Word", card)
        export.clicked.connect(self._export)
        row.addWidget(export)
        card_layout.addLayout(row)
        layout.addWidget(card)

        self._path = forms.muted("", area)
        self._path.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._path)
        self._status = forms.muted("", area)
        layout.addWidget(self._status)
        layout.addStretch(1)

        self._vm.versions_changed.connect(self._fill_versions)
        self._vm.checks_changed.connect(self._fill_checks)
        self._vm.path_changed.connect(self._path.setText)
        self._vm.status_changed.connect(self._status.setText)
        self._vm.load()

    def _fill_versions(self, rows: object) -> None:
        """刷新版本下拉框。"""
        records = cast(list[Any], rows)
        self._version.blockSignals(True)
        self._version.clear()
        for row in records:
            self._version.addItem(row.name, row.id)
        self._version.blockSignals(False)
        if records:
            self._version.setCurrentIndex(0)
            self._vm.select(int(records[0].id))

    def _fill_checks(self, lines: object) -> None:
        """展示预检结果。"""
        records = cast(list[Any], lines)
        self._checks.setText("\n".join(f"· {line}" for line in records))

    def _on_version(self, index: int) -> None:
        """切换版本重新预检。"""
        if index >= 0:
            self._vm.select(int(self._version.itemData(index)))

    def _export(self) -> None:
        """点击导出。"""
        if self._version.currentIndex() < 0:
            return
        self._vm.export(int(self._version.currentData()), self._folder.text())
