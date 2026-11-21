"""学历路径页：左侧时间轴列表，右侧编辑表单。"""

from __future__ import annotations

from typing import Any, cast

from forgecv.features.education.schemas import DEGREE_LEVELS, EducationInput
from forgecv.features.education.viewmodel import EducationViewModel
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.kit.format import period
from forgecv.platform.ui.qt import QtCore, QtWidgets


class EducationPage(QtWidgets.QWidget):
    """学历节点的增删改与排序。"""

    def __init__(self, view_model: EducationViewModel) -> None:
        """构建左右分栏并加载数据。"""
        super().__init__()
        self._vm = view_model
        self._current_id: int | None = None
        self._status: QtWidgets.QLabel

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addWidget(forms.title("学历路径", self))
        outer.addWidget(forms.muted("按时间顺序记录学历变迁；列表顺序决定时间轴顺序。", self))

        split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        split.addWidget(self._build_list(split))
        split.addWidget(self._build_form(split))
        split.setSizes([340, 720])
        outer.addWidget(split, 1)

        self._vm.rows_changed.connect(self._fill_list)
        self._vm.status_changed.connect(self._status.setText)
        self._vm.load()

    def _build_list(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """左侧时间轴列表。"""
        panel = QtWidgets.QWidget(parent)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 12, 0)
        self._list = QtWidgets.QListWidget(panel)
        self._list.setObjectName("ItemList")
        self._list.currentRowChanged.connect(self._on_row)
        layout.addWidget(self._list, 1)
        row = QtWidgets.QHBoxLayout()
        add = forms.button("新增", panel)
        add.clicked.connect(self._new)
        up = forms.button("上移", panel, secondary=True)
        up.clicked.connect(lambda: self._move(-1))
        down = forms.button("下移", panel, secondary=True)
        down.clicked.connect(lambda: self._move(1))
        row.addWidget(add)
        row.addWidget(up)
        row.addWidget(down)
        layout.addLayout(row)
        return panel

    def _build_form(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """右侧编辑区。"""
        area, layout = forms.scroll_form(parent)
        frame, card_layout = forms.card(area)
        card_layout.addWidget(forms.title("学历详情", frame))
        body = forms.form()
        self._school = QtWidgets.QLineEdit(frame)
        self._degree = QtWidgets.QComboBox(frame)
        self._degree.addItems(DEGREE_LEVELS)
        self._major = QtWidgets.QLineEdit(frame)
        self._start = forms.date_edit(frame)
        self._end = forms.date_edit(frame)
        self._current = QtWidgets.QCheckBox("至今（在读）", frame)
        self._current.toggled.connect(lambda checked: self._end.setEnabled(not checked))
        end_row = QtWidgets.QHBoxLayout()
        end_row.addWidget(self._end, 1)
        end_row.addWidget(self._current)
        self._gpa = QtWidgets.QLineEdit(frame)
        self._gpa.setPlaceholderText("如 3.8/4.0")
        self._courses = QtWidgets.QLineEdit(frame)
        self._courses.setPlaceholderText("用顿号或逗号分隔")
        self._thesis = QtWidgets.QLineEdit(frame)
        self._notes = QtWidgets.QTextEdit(frame)
        self._notes.setFixedHeight(80)
        body.addRow("院校", self._school)
        body.addRow("层次", self._degree)
        body.addRow("专业", self._major)
        body.addRow("入学", self._start)
        body.addRow("毕业", end_row)
        body.addRow("GPA", self._gpa)
        body.addRow("主修课程", self._courses)
        body.addRow("论文 / 毕设", self._thesis)
        body.addRow("备注", self._notes)
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
        """刷新列表，尽量保留当前选中。"""
        records = cast(list[Any], rows)
        keep = self._current_id
        self._list.blockSignals(True)
        self._list.clear()
        for row in records:
            text = (
                f"{period(row.start_date, row.end_date, is_current=row.is_current)}\n"
                f"{row.school} · {row.degree_level} · {row.major or '未填专业'}"
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
        """选中行回填表单。"""
        if row < 0:
            return
        item = self._list.item(row)
        education_id = int(item.data(QtCore.Qt.ItemDataRole.UserRole))
        for record in self._vm.rows:
            if record.id == education_id:
                self._load(record)
                return

    def _load(self, record: object) -> None:
        """把 ORM 记录写进控件。"""
        self._current_id = record.id  # type: ignore[attr-defined]
        self._school.setText(record.school)  # type: ignore[attr-defined]
        self._degree.setCurrentText(record.degree_level)  # type: ignore[attr-defined]
        self._major.setText(record.major)  # type: ignore[attr-defined]
        forms.set_date(self._start, record.start_date)  # type: ignore[attr-defined]
        forms.set_date(self._end, record.end_date)  # type: ignore[attr-defined]
        self._current.setChecked(record.is_current)  # type: ignore[attr-defined]
        self._gpa.setText(record.gpa)  # type: ignore[attr-defined]
        self._courses.setText("、".join(record.courses))  # type: ignore[attr-defined]
        self._thesis.setText(record.thesis)  # type: ignore[attr-defined]
        self._notes.setPlainText(record.notes)  # type: ignore[attr-defined]
        self._delete.setEnabled(True)

    def _new(self) -> None:
        """清空为新建状态。"""
        self._current_id = None
        self._school.clear()
        self._degree.setCurrentIndex(1)
        self._major.clear()
        self._current.setChecked(False)
        self._gpa.clear()
        self._courses.clear()
        self._thesis.clear()
        self._notes.clear()
        self._delete.setEnabled(False)

    def _save(self) -> None:
        """新增或更新。"""
        data = EducationInput(
            school=self._school.text(),
            degree_level=self._degree.currentText(),
            major=self._major.text(),
            start_date=forms.to_date(self._start),
            end_date=None if self._current.isChecked() else forms.to_date(self._end),
            is_current=self._current.isChecked(),
            gpa=self._gpa.text(),
            courses=self._split(self._courses.text()),
            thesis=self._thesis.text(),
            notes=self._notes.toPlainText(),
        )
        if self._current_id is None:
            new_id = self._vm.add(data)
            if new_id is not None:
                self._select_id(new_id)
            return
        self._vm.update(self._current_id, data)

    def _select_id(self, target: int) -> None:
        """选中指定记录并回填，不依赖列表信号。"""
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
        """删除当前选中。"""
        if self._current_id is not None:
            self._vm.delete(self._current_id)
            self._current_id = None

    def _move(self, delta: int) -> None:
        """上移或下移列表项。"""
        self._vm.move(self._list.currentRow(), delta)

    @staticmethod
    def _split(value: str) -> list[str]:
        """逗号与顿号都作为分隔符。"""
        normalized = value.replace("、", ",").replace("；", ",").replace(";", ",")
        return [item.strip() for item in normalized.split(",") if item.strip()]
