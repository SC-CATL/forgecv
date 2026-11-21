"""标签管理页：四维标签的维护入口。"""

from __future__ import annotations

from typing import Any, cast

from forgecv.features.tag.schemas import TagInput
from forgecv.features.tag.viewmodel import TagViewModel
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.qt import QtCore, QtWidgets


class TagPage(QtWidgets.QWidget):
    """左侧标签列表，右侧编辑表单。"""

    def __init__(self, view_model: TagViewModel) -> None:
        """构建界面并加载。"""
        super().__init__()
        self._vm = view_model
        self._current_id: int | None = None
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addWidget(forms.title("标签管理", self))
        outer.addWidget(forms.muted("四个维度：语言、领域、工程实践、工具链。名称全局唯一。", self))

        split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        split.addWidget(self._build_list(split))
        split.addWidget(self._build_form(split))
        split.setSizes([340, 620])
        outer.addWidget(split, 1)

        self._vm.rows_changed.connect(self._fill_list)
        self._vm.status_changed.connect(self._status.setText)
        self._vm.load()

    def _build_list(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """左侧标签列表。"""
        panel = QtWidgets.QWidget(parent)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 12, 0)
        self._list = QtWidgets.QListWidget(panel)
        self._list.setObjectName("ItemList")
        self._list.currentRowChanged.connect(self._on_row)
        layout.addWidget(self._list, 1)
        add = forms.button("新增标签", panel)
        add.clicked.connect(self._new)
        layout.addWidget(add)
        return panel

    def _build_form(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """右侧编辑区。"""
        area, layout = forms.scroll_form(parent)
        frame, card_layout = forms.card(area)
        card_layout.addWidget(forms.title("标签详情", frame))
        body = forms.form()
        self._name = QtWidgets.QLineEdit(frame)
        self._dimension = QtWidgets.QComboBox(frame)
        for code, label in self._vm.dimensions.items():
            self._dimension.addItem(label, code)
        self._color = QtWidgets.QLineEdit(frame)
        self._color.setPlaceholderText("#RRGGBB，可留空")
        self._order = QtWidgets.QSpinBox(frame)
        self._order.setRange(0, 9999)
        self._description = QtWidgets.QTextEdit(frame)
        self._description.setFixedHeight(80)
        body.addRow("名称", self._name)
        body.addRow("维度", self._dimension)
        body.addRow("颜色", self._color)
        body.addRow("排序号", self._order)
        body.addRow("说明", self._description)
        card_layout.addLayout(body)
        actions = QtWidgets.QHBoxLayout()
        self._delete = forms.button("删除", frame, danger=True)
        self._delete.clicked.connect(self._delete_current)
        save = forms.button("保存", frame)
        save.clicked.connect(self._save)
        actions.addWidget(self._delete)
        actions.addStretch(1)
        actions.addWidget(save)
        card_layout.addLayout(actions)
        self._status = forms.muted("", frame)
        card_layout.addWidget(self._status)
        layout.addWidget(frame)
        layout.addStretch(1)
        return area

    def _fill_list(self, rows: object) -> None:
        """刷新标签列表。"""
        records = cast(list[Any], rows)
        keep = self._current_id
        labels = self._vm.dimensions
        self._list.blockSignals(True)
        self._list.clear()
        for row in records:
            text = f"[{labels.get(row.dimension, row.dimension)}] {row.name}"
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, row.id)
            self._list.addItem(item)
        self._list.blockSignals(False)
        if self._list.count() == 0:
            self._new()
            return
        index = 0
        if keep is not None:
            for candidate in range(self._list.count()):
                if self._list.item(candidate).data(QtCore.Qt.ItemDataRole.UserRole) == keep:
                    index = candidate
                    break
        self._list.setCurrentRow(index)

    def _on_row(self, row: int) -> None:
        """回填选中标签。"""
        if row < 0:
            return
        target = int(self._list.item(row).data(QtCore.Qt.ItemDataRole.UserRole))
        for record in self._vm.rows:
            if record.id == target:
                self._load(record)
                return

    def _load(self, record: object) -> None:
        """写入控件。"""
        self._current_id = record.id  # type: ignore[attr-defined]
        self._name.setText(record.name)  # type: ignore[attr-defined]
        index = self._dimension.findData(record.dimension)  # type: ignore[attr-defined]
        self._dimension.setCurrentIndex(max(index, 0))
        self._color.setText(record.color)  # type: ignore[attr-defined]
        self._order.setValue(record.sort_order)  # type: ignore[attr-defined]
        self._description.setPlainText(record.description)  # type: ignore[attr-defined]
        self._delete.setEnabled(True)

    def _new(self) -> None:
        """清空为新建。"""
        self._current_id = None
        self._name.clear()
        self._dimension.setCurrentIndex(0)
        self._color.clear()
        self._order.setValue(0)
        self._description.clear()
        self._delete.setEnabled(False)

    def _save(self) -> None:
        """新增或更新。"""
        data = TagInput(
            name=self._name.text(),
            dimension=str(self._dimension.currentData()),
            color=self._color.text(),
            description=self._description.toPlainText(),
            sort_order=self._order.value(),
        )
        if self._current_id is None:
            new_id = self._vm.create(data)
            if new_id is not None:
                self._select_id(new_id)
            return
        self._vm.update(self._current_id, data)

    def _select_id(self, target: int) -> None:
        """选中指定标签并回填。"""
        for index in range(self._list.count()):
            if self._list.item(index).data(QtCore.Qt.ItemDataRole.UserRole) == target:
                self._list.blockSignals(True)
                self._list.setCurrentRow(index)
                self._list.blockSignals(False)
        for record in self._vm.rows:
            if record.id == target:
                self._load(record)
                return

    def _delete_current(self) -> None:
        """删除当前标签。"""
        if self._current_id is not None:
            self._vm.delete(self._current_id)
            self._current_id = None
