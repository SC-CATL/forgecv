"""技能矩阵页：技能编辑与证据链。"""

from __future__ import annotations

from typing import Any, cast

from forgecv.features.skill.schemas import SkillInput
from forgecv.features.skill.viewmodel import SkillViewModel
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.qt import QtCore, QtWidgets


class SkillPage(QtWidgets.QWidget):
    """左侧技能列表，右侧技能表单与证据。"""

    def __init__(self, view_model: SkillViewModel) -> None:
        """构建界面并加载。"""
        super().__init__()
        self._vm = view_model
        self._current_id: int | None = None
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addWidget(forms.title("技能矩阵", self))
        outer.addWidget(forms.muted("熟练度是自评；每条技能尽量挂上项目或经历作为证据。", self))

        split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        split.addWidget(self._build_list(split))
        split.addWidget(self._build_form(split))
        split.setSizes([320, 740])
        outer.addWidget(split, 1)

        self._vm.rows_changed.connect(self._fill_list)
        self._vm.evidence_changed.connect(self._fill_evidence)
        self._vm.sources_changed.connect(self._fill_sources)
        self._vm.status_changed.connect(self._status.setText)
        self._vm.load()

    def _build_list(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """左侧技能列表。"""
        panel = QtWidgets.QWidget(parent)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 12, 0)
        self._list = QtWidgets.QListWidget(panel)
        self._list.setObjectName("ItemList")
        self._list.currentRowChanged.connect(self._on_row)
        layout.addWidget(self._list, 1)
        add = forms.button("新增技能", panel)
        add.clicked.connect(self._new)
        layout.addWidget(add)
        return panel

    def _build_form(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """右侧表单与证据区。"""
        area, layout = forms.scroll_form(parent)
        layout.addWidget(self._build_skill_card(area))
        layout.addWidget(self._build_evidence_card(area))
        self._status = forms.muted("", area)
        layout.addWidget(self._status)
        layout.addStretch(1)
        return area

    def _build_skill_card(self, parent: QtWidgets.QWidget) -> QtWidgets.QFrame:
        """技能字段卡片。"""
        frame, card_layout = forms.card(parent)
        card_layout.addWidget(forms.title("技能详情", frame))
        body = forms.form()
        self._category = QtWidgets.QComboBox(frame)
        self._category.addItems(list(self._vm.categories))
        self._name = QtWidgets.QLineEdit(frame)
        self._level = QtWidgets.QComboBox(frame)
        for value, label in self._vm.levels.items():
            self._level.addItem(f"{value} · {label}", value)
        self._years = QtWidgets.QDoubleSpinBox(frame)
        self._years.setRange(-1, 50)
        self._years.setDecimals(1)
        self._years.setSpecialValueText("未填")
        self._score = QtWidgets.QSpinBox(frame)
        self._score.setRange(-1, 100)
        self._score.setSpecialValueText("未填")
        self._notes = QtWidgets.QTextEdit(frame)
        self._notes.setFixedHeight(70)
        body.addRow("分类", self._category)
        body.addRow("名称", self._name)
        body.addRow("熟练度", self._level)
        body.addRow("使用年限", self._years)
        body.addRow("自评分", self._score)
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
        return frame

    def _build_evidence_card(self, parent: QtWidgets.QWidget) -> QtWidgets.QFrame:
        """证据卡片：列表 + 快速新增。"""
        frame, layout = forms.card(parent)
        layout.addWidget(forms.title("能力证据", frame))
        self._evidence = QtWidgets.QListWidget(frame)
        self._evidence.setObjectName("ItemList")
        self._evidence.setFixedHeight(120)
        layout.addWidget(self._evidence)
        row = QtWidgets.QHBoxLayout()
        self._source = QtWidgets.QComboBox(frame)
        self._statement = QtWidgets.QLineEdit(frame)
        self._statement.setPlaceholderText("这条证据说明了什么")
        self._metric = QtWidgets.QLineEdit(frame)
        self._metric.setPlaceholderText("量化口径，可空")
        add = forms.button("添加证据", frame, secondary=True)
        add.clicked.connect(self._add_evidence)
        row.addWidget(self._source, 2)
        row.addWidget(self._statement, 3)
        row.addWidget(self._metric, 2)
        row.addWidget(add)
        layout.addLayout(row)
        actions = QtWidgets.QHBoxLayout()
        actions.addStretch(1)
        self._delete_evidence = forms.button("删除证据", frame, danger=True)
        self._delete_evidence.setEnabled(False)
        self._delete_evidence.clicked.connect(self._remove_evidence)
        self._evidence.currentRowChanged.connect(
            lambda row: self._delete_evidence.setEnabled(row >= 0)
        )
        actions.addWidget(self._delete_evidence)
        layout.addLayout(actions)
        return frame

    def _fill_list(self, rows: object) -> None:
        """刷新技能列表。"""
        records = cast(list[Any], rows)
        keep = self._current_id
        self._list.blockSignals(True)
        self._list.clear()
        for row in records:
            item = QtWidgets.QListWidgetItem(
                f"{row.name}\n{row.category} · {self._vm.levels.get(row.level, row.level)}"
            )
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

    def _fill_sources(self, sources: object) -> None:
        """刷新证据来源下拉框。"""
        records = cast(list[Any], sources)
        self._source.clear()
        for key, label in records:
            self._source.addItem(str(label), str(key))

    def _fill_evidence(self, rows: object) -> None:
        """刷新证据列表。"""
        records = cast(list[Any], rows)
        self._evidence.clear()
        for row in records:
            suffix = f"（{row.metric_note}）" if row.metric_note else ""
            item = QtWidgets.QListWidgetItem(f"{row.statement}{suffix}")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, row.id)
            self._evidence.addItem(item)
        self._delete_evidence.setEnabled(False)

    def _on_row(self, row: int) -> None:
        """选中技能后回填并加载证据。"""
        if row < 0:
            return
        target = int(self._list.item(row).data(QtCore.Qt.ItemDataRole.UserRole))
        for record in self._vm.rows:
            if record.id == target:
                self._load(record)
                self._vm.select(record.id)
                return

    def _load(self, record: object) -> None:
        """写入技能字段。"""
        self._current_id = record.id  # type: ignore[attr-defined]
        self._category.setCurrentText(record.category)  # type: ignore[attr-defined]
        self._name.setText(record.name)  # type: ignore[attr-defined]
        index = self._level.findData(record.level)  # type: ignore[attr-defined]
        self._level.setCurrentIndex(max(index, 0))
        self._years.setValue(record.years if record.years is not None else -1)  # type: ignore[attr-defined]
        self._score.setValue(record.self_score if record.self_score is not None else -1)  # type: ignore[attr-defined]
        self._notes.setPlainText(record.notes)  # type: ignore[attr-defined]
        self._delete.setEnabled(True)

    def _new(self) -> None:
        """清空为新建。"""
        self._current_id = None
        self._category.setCurrentIndex(0)
        self._name.clear()
        self._level.setCurrentIndex(1)
        self._years.setValue(-1)
        self._score.setValue(-1)
        self._notes.clear()
        self._evidence.clear()
        self._delete.setEnabled(False)

    def _save(self) -> None:
        """新增或更新技能。"""
        data = SkillInput(
            name=self._name.text(),
            category=self._category.currentText(),
            level=int(self._level.currentData()),
            years=None if self._years.value() < 0 else float(self._years.value()),
            self_score=None if self._score.value() < 0 else int(self._score.value()),
            notes=self._notes.toPlainText(),
        )
        if self._current_id is None:
            new_id = self._vm.add(data)
            if new_id is not None:
                self._select_id(new_id)
            return
        self._vm.update(self._current_id, data)

    def _select_id(self, target: int) -> None:
        """选中指定技能。"""
        for index in range(self._list.count()):
            if self._list.item(index).data(QtCore.Qt.ItemDataRole.UserRole) == target:
                self._list.blockSignals(True)
                self._list.setCurrentRow(index)
                self._list.blockSignals(False)
        for record in self._vm.rows:
            if record.id == target:
                self._load(record)
                self._vm.select(record.id)
                return

    def _add_evidence(self) -> None:
        """用快速表单新增证据。"""
        if self._current_id is None:
            self._status.setText("请先保存技能")
            return
        source = str(self._source.currentData() or "")
        if self._vm.add_evidence(
            self._current_id,
            self._statement.text(),
            self._metric.text(),
            source,
        ):
            self._statement.clear()
            self._metric.clear()

    def _remove_evidence(self) -> None:
        """删除选中证据。"""
        item = self._evidence.currentItem()
        if item is not None and self._current_id is not None:
            self._vm.delete_evidence(
                self._current_id, int(item.data(QtCore.Qt.ItemDataRole.UserRole))
            )

    def _delete_current(self) -> None:
        """删除当前技能。"""
        if self._current_id is not None:
            self._vm.delete(self._current_id)
            self._current_id = None
