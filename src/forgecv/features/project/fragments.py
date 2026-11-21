"""项目页的复合控件：指标表格与标签勾选。"""

from __future__ import annotations

from typing import Any, cast

from forgecv.features.project.schemas import MetricInput
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.qt import QtCore, QtWidgets


class MetricsEditor(QtWidgets.QFrame):
    """指标表格卡片：每行一个键值对。"""

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        """构建标题、表格与增删按钮。"""
        super().__init__(parent)
        self.setObjectName("Card")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(forms.title("项目指标", self))
        self.table = QtWidgets.QTableWidget(0, 3, self)
        self.table.setHorizontalHeaderLabels(["指标", "值", "单位"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMinimumHeight(120)
        layout.addWidget(self.table)
        row = QtWidgets.QHBoxLayout()
        add = forms.button("加一行", self, secondary=True)
        add.clicked.connect(lambda: self.table.insertRow(self.table.rowCount()))
        remove = forms.button("删选中行", self, secondary=True)
        remove.clicked.connect(self._remove_row)
        row.addWidget(add)
        row.addWidget(remove)
        row.addStretch(1)
        layout.addLayout(row)

    def set_metrics(self, metrics: object) -> None:
        """用记录刷新表格。"""
        records = cast(list[Any], metrics)
        self.table.setRowCount(0)
        for metric in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(metric.key))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(metric.value))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(metric.unit))

    def collect(self) -> list[MetricInput]:
        """读取表格为输入模型。"""
        return [
            MetricInput(
                key=self._cell(row, 0),
                value=self._cell(row, 1),
                unit=self._cell(row, 2),
            )
            for row in range(self.table.rowCount())
        ]

    def clear(self) -> None:
        """清空全部行。"""
        self.table.setRowCount(0)

    def _remove_row(self) -> None:
        """删除当前选中行。"""
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def _cell(self, row: int, column: int) -> str:
        """安全读取单元格。"""
        item = self.table.item(row, column)
        return "" if item is None else item.text()


class TagPicker(QtWidgets.QFrame):
    """四维标签勾选卡片。"""

    def __init__(self, parent: QtWidgets.QWidget, labels: dict[str, str]) -> None:
        """构建列表并记录维度中文名。"""
        super().__init__(parent)
        self.setObjectName("Card")
        self._labels = labels
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(forms.title("技术标签", self))
        layout.addWidget(forms.muted("勾选后随项目一起保存，用于筛选与统计。", self))
        self.list = QtWidgets.QListWidget(self)
        self.list.setObjectName("ItemList")
        self.list.setMinimumHeight(150)
        layout.addWidget(self.list)

    def set_tags(self, tags: object) -> None:
        """重建可勾选列表。"""
        records = cast(list[Any], tags)
        self.list.clear()
        for tag in records:
            dimension = self._labels.get(tag.dimension, tag.dimension)
            item = QtWidgets.QListWidgetItem(f"[{dimension}] {tag.name}")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, tag.id)
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            self.list.addItem(item)

    def set_selected(self, tags: object) -> None:
        """按项目已有标签打勾。"""
        records = cast(list[Any], tags)
        selected = {tag.id for tag in records}
        for index in range(self.list.count()):
            item = self.list.item(index)
            checked = item.data(QtCore.Qt.ItemDataRole.UserRole) in selected
            state = QtCore.Qt.CheckState.Checked if checked else QtCore.Qt.CheckState.Unchecked
            item.setCheckState(state)

    def selected_ids(self) -> list[int]:
        """已勾选的标签 id。"""
        checked: list[int] = []
        for index in range(self.list.count()):
            item = self.list.item(index)
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                checked.append(int(item.data(QtCore.Qt.ItemDataRole.UserRole)))
        return checked

    def clear(self) -> None:
        """全部取消勾选。"""
        for index in range(self.list.count()):
            self.list.item(index).setCheckState(QtCore.Qt.CheckState.Unchecked)
