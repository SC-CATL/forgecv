"""快照页：保存版本、选择两份对比。"""

from __future__ import annotations

from typing import Any, cast

from forgecv.features.snapshot.viewmodel import SnapshotViewModel
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.qt import QtCore, QtWidgets


class SnapshotPage(QtWidgets.QWidget):
    """左侧快照列表，右侧 Diff。"""

    def __init__(self, view_model: SnapshotViewModel) -> None:
        """构建界面并加载。"""
        super().__init__()
        self._vm = view_model
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addWidget(forms.title("版本快照", self))
        outer.addWidget(forms.muted("快照保存当时的渲染文本；用两份快照做行级差异对比。", self))
        split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        split.addWidget(self._build_controls(split))
        split.addWidget(self._build_diff(split))
        split.setSizes([380, 720])
        outer.addWidget(split, 1)

        self._vm.versions_changed.connect(self._fill_versions)
        self._vm.snapshots_changed.connect(self._fill_snapshots)
        self._vm.diff_changed.connect(self._diff.setPlainText)
        self._vm.status_changed.connect(self._status.setText)
        self._vm.load()

    def _build_controls(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """版本、快照列表与对比选择。"""
        panel = QtWidgets.QWidget(parent)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 12, 0)
        self._version = QtWidgets.QComboBox(panel)
        self._version.currentIndexChanged.connect(self._on_version)
        layout.addWidget(self._version)
        row = QtWidgets.QHBoxLayout()
        self._label = QtWidgets.QLineEdit(panel)
        self._label.setPlaceholderText("快照备注，可空")
        create = forms.button("保存快照", panel)
        create.clicked.connect(self._create)
        row.addWidget(self._label, 1)
        row.addWidget(create)
        layout.addLayout(row)
        self._list = QtWidgets.QListWidget(panel)
        self._list.setObjectName("ItemList")
        layout.addWidget(self._list, 1)
        compare_row = QtWidgets.QHBoxLayout()
        self._before = QtWidgets.QComboBox(panel)
        self._after = QtWidgets.QComboBox(panel)
        compare = forms.button("对比", panel, secondary=True)
        compare.clicked.connect(self._compare)
        compare_row.addWidget(self._before, 1)
        compare_row.addWidget(self._after, 1)
        compare_row.addWidget(compare)
        layout.addLayout(compare_row)
        self._status = forms.muted("", panel)
        layout.addWidget(self._status)
        return panel

    def _build_diff(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """右侧差异预览。"""
        self._diff = QtWidgets.QPlainTextEdit(parent)
        self._diff.setReadOnly(True)
        return self._diff

    def _fill_versions(self, rows: object) -> None:
        """版本下拉框。"""
        records = cast(list[Any], rows)
        self._version.blockSignals(True)
        self._version.clear()
        for row in records:
            self._version.addItem(row.name, row.id)
        self._version.blockSignals(False)
        if records:
            self._vm.select(int(records[0].id))

    def _fill_snapshots(self, rows: object) -> None:
        """快照列表与对比下拉框。"""
        records = cast(list[Any], rows)
        self._list.clear()
        self._before.clear()
        self._after.clear()
        for row in records:
            self._list.addItem(f"{row.label or '未命名'} · {row.created_at:%Y-%m-%d %H:%M}")
            self._before.addItem(f"{row.id} · {row.label or '未命名'}", row.id)
            self._after.addItem(f"{row.id} · {row.label or '未命名'}", row.id)
        if self._after.count() >= 1:
            self._after.setCurrentIndex(self._after.count() - 1)

    def _on_version(self, index: int) -> None:
        """切换版本。"""
        if index >= 0:
            self._vm.select(int(self._version.itemData(index)))

    def _create(self) -> None:
        """保存快照。"""
        self._vm.create(self._label.text())
        self._label.clear()

    def _compare(self) -> None:
        """对比选中的两份快照。"""
        if self._before.currentIndex() < 0 or self._after.currentIndex() < 0:
            return
        self._vm.compare(
            int(self._before.currentData()), int(self._after.currentData())
        )
