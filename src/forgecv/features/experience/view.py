"""工作经历页：左侧列表，右侧表单。"""

from __future__ import annotations

from typing import Any, cast

from forgecv.features.experience.schemas import ExperienceInput
from forgecv.features.experience.viewmodel import ExperienceViewModel
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.kit.format import period
from forgecv.platform.ui.qt import QtCore, QtWidgets


class ExperiencePage(QtWidgets.QWidget):
    """工作与实习经历的增删改。"""

    def __init__(self, view_model: ExperienceViewModel) -> None:
        """构建界面并加载。"""
        super().__init__()
        self._vm = view_model
        self._current_id: int | None = None
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addWidget(forms.title("工作经历", self))
        outer.addWidget(forms.muted("成果条目建议包含动作、方法与可验证的数字。", self))

        split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        split.addWidget(self._build_list(split))
        split.addWidget(self._build_form(split))
        split.setSizes([340, 720])
        outer.addWidget(split, 1)

        self._vm.rows_changed.connect(self._fill_list)
        self._vm.status_changed.connect(self._status.setText)
        self._vm.load()

    def _build_list(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """左侧经历列表。"""
        panel = QtWidgets.QWidget(parent)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 12, 0)
        self._list = QtWidgets.QListWidget(panel)
        self._list.setObjectName("ItemList")
        self._list.currentRowChanged.connect(self._on_row)
        layout.addWidget(self._list, 1)
        add = forms.button("新增", panel)
        add.clicked.connect(self._new)
        layout.addWidget(add)
        return panel

    def _build_form(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """右侧编辑区。"""
        area, layout = forms.scroll_form(parent)
        frame, card_layout = forms.card(area)
        card_layout.addWidget(forms.title("经历详情", frame))
        body = forms.form()
        self._company = QtWidgets.QLineEdit(frame)
        self._role = QtWidgets.QLineEdit(frame)
        self._location = QtWidgets.QLineEdit(frame)
        self._start = forms.date_edit(frame)
        self._end = forms.date_edit(frame)
        self._current = QtWidgets.QCheckBox("至今（在职）", frame)
        self._current.toggled.connect(lambda checked: self._end.setEnabled(not checked))
        end_row = QtWidgets.QHBoxLayout()
        end_row.addWidget(self._end, 1)
        end_row.addWidget(self._current)
        self._summary = QtWidgets.QTextEdit(frame)
        self._summary.setFixedHeight(80)
        self._highlights = QtWidgets.QTextEdit(frame)
        self._highlights.setFixedHeight(110)
        self._highlights.setPlaceholderText("每行一条，建议量化")
        body.addRow("公司", self._company)
        body.addRow("职位", self._role)
        body.addRow("城市", self._location)
        body.addRow("开始", self._start)
        body.addRow("结束", end_row)
        body.addRow("职责概述", self._summary)
        body.addRow("成果条目", self._highlights)
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
        """刷新列表并恢复选择。"""
        records = cast(list[Any], rows)
        keep = self._current_id
        self._list.blockSignals(True)
        self._list.clear()
        for row in records:
            text = (
                f"{period(row.start_date, row.end_date, is_current=row.is_current)} · "
                f"{row.company}\n{row.role} · {row.location or '未填城市'}"
            )
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
        """回填选中经历。"""
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
        self._company.setText(record.company)  # type: ignore[attr-defined]
        self._role.setText(record.role)  # type: ignore[attr-defined]
        self._location.setText(record.location)  # type: ignore[attr-defined]
        forms.set_date(self._start, record.start_date)  # type: ignore[attr-defined]
        forms.set_date(self._end, record.end_date)  # type: ignore[attr-defined]
        self._current.setChecked(record.is_current)  # type: ignore[attr-defined]
        self._summary.setPlainText(record.summary)  # type: ignore[attr-defined]
        self._highlights.setPlainText("\n".join(record.highlights))  # type: ignore[attr-defined]
        self._delete.setEnabled(True)

    def _new(self) -> None:
        """清空为新建。"""
        self._current_id = None
        self._company.clear()
        self._role.clear()
        self._location.clear()
        self._current.setChecked(False)
        self._summary.clear()
        self._highlights.clear()
        self._delete.setEnabled(False)

    def _save(self) -> None:
        """新增或更新。"""
        data = ExperienceInput(
            company=self._company.text(),
            role=self._role.text(),
            location=self._location.text(),
            start_date=forms.to_date(self._start),
            end_date=None if self._current.isChecked() else forms.to_date(self._end),
            is_current=self._current.isChecked(),
            summary=self._summary.toPlainText(),
            highlights=self._lines(self._highlights.toPlainText()),
        )
        if self._current_id is None:
            new_id = self._vm.add(data)
            if new_id is not None:
                self._select_id(new_id)
            return
        self._vm.update(self._current_id, data)

    def _select_id(self, target: int) -> None:
        """选中指定经历并回填。"""
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
        """删除当前经历。"""
        if self._current_id is not None:
            self._vm.delete(self._current_id)
            self._current_id = None

    @staticmethod
    def _lines(value: str) -> list[str]:
        """按行拆分成果条目。"""
        return [line.strip() for line in value.splitlines() if line.strip()]
