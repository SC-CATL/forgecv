"""项目库页：左侧项目列表，右侧档案、指标与标签。"""

from __future__ import annotations

from typing import Any, cast

from forgecv.features.project.fragments import MetricsEditor, TagPicker
from forgecv.features.project.schemas import ProjectInput
from forgecv.features.project.viewmodel import ProjectViewModel
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.qt import QtCore, QtWidgets

DIRECTIONS = ("后端", "嵌入式", "算法", "客户端", "工具链", "其他")
STATUSES = (("wip", "进行中"), ("online", "已上线"), ("archived", "已归档"))


class ProjectPage(QtWidgets.QWidget):
    """项目的增删改、指标编辑与四维标签选择。"""

    def __init__(self, view_model: ProjectViewModel) -> None:
        """构建界面并加载。"""
        super().__init__()
        self._vm = view_model
        self._current_id: int | None = None
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addWidget(forms.title("项目库", self))
        outer.addWidget(forms.muted("项目是能力证据的载体：方向、指标、标签缺一不可。", self))

        split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        split.addWidget(self._build_list(split))
        split.addWidget(self._build_form(split))
        split.setSizes([300, 760])
        outer.addWidget(split, 1)

        self._vm.rows_changed.connect(self._fill_list)
        self._vm.tags_changed.connect(self._tags.set_tags)
        self._vm.project_tags_changed.connect(self._tags.set_selected)
        self._vm.metrics_changed.connect(self._metrics_editor.set_metrics)
        self._vm.status_changed.connect(self._status.setText)
        self._vm.load()

    def _build_list(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """左侧项目列表。"""
        panel = QtWidgets.QWidget(parent)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 12, 0)
        self._list = QtWidgets.QListWidget(panel)
        self._list.setObjectName("ItemList")
        self._list.currentRowChanged.connect(self._on_row)
        layout.addWidget(self._list, 1)
        add = forms.button("新增项目", panel)
        add.clicked.connect(self._new)
        layout.addWidget(add)
        return panel

    def _build_form(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """右侧编辑区：档案 + 指标 + 标签。"""
        area, layout = forms.scroll_form(parent)
        layout.addWidget(self._build_archive(area))
        self._metrics_editor = MetricsEditor(area)
        self._metrics = self._metrics_editor.table
        layout.addWidget(self._metrics_editor)
        self._tags = TagPicker(area, self._vm.dimension_labels)
        self._tag_list = self._tags.list
        layout.addWidget(self._tags)
        self._status = forms.muted("", area)
        layout.addWidget(self._status)
        layout.addStretch(1)
        return area

    def _build_archive(self, parent: QtWidgets.QWidget) -> QtWidgets.QFrame:
        """项目档案卡片。"""
        frame, card_layout = forms.card(parent)
        card_layout.addWidget(forms.title("项目档案", frame))
        body = forms.form()
        self._name = QtWidgets.QLineEdit(frame)
        self._direction = QtWidgets.QComboBox(frame)
        self._direction.addItems(DIRECTIONS)
        self._direction.setEditable(True)
        self._role = QtWidgets.QLineEdit(frame)
        self._start = forms.date_edit(frame)
        self._end = forms.date_edit(frame)
        self._open = QtWidgets.QCheckBox("无结束时间", frame)
        self._open.toggled.connect(lambda checked: self._end.setEnabled(not checked))
        end_row = QtWidgets.QHBoxLayout()
        end_row.addWidget(self._end, 1)
        end_row.addWidget(self._open)
        self._status_combo = QtWidgets.QComboBox(frame)
        for code, label in STATUSES:
            self._status_combo.addItem(label, code)
        self._repo = QtWidgets.QLineEdit(frame)
        self._demo = QtWidgets.QLineEdit(frame)
        self._summary = QtWidgets.QTextEdit(frame)
        self._summary.setFixedHeight(60)
        self._architecture = QtWidgets.QTextEdit(frame)
        self._architecture.setFixedHeight(60)
        self._highlights = QtWidgets.QTextEdit(frame)
        self._highlights.setFixedHeight(90)
        self._highlights.setPlaceholderText("每行一条：问题 → 动作 → 结果")
        self._challenges = QtWidgets.QTextEdit(frame)
        self._challenges.setFixedHeight(50)
        self._retro = QtWidgets.QTextEdit(frame)
        self._retro.setFixedHeight(50)
        self._ci = QtWidgets.QLineEdit(frame)
        self._ci.setPlaceholderText("如 passing / failing")
        self._archive_rows(body, end_row)
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

    def _archive_rows(
        self,
        body: QtWidgets.QFormLayout,
        end_row: QtWidgets.QHBoxLayout,
    ) -> None:
        """按顺序把档案字段放进表单。"""
        body.addRow("项目名", self._name)
        body.addRow("方向", self._direction)
        body.addRow("我的角色", self._role)
        body.addRow("开始", self._start)
        body.addRow("结束", end_row)
        body.addRow("状态", self._status_combo)
        body.addRow("仓库", self._repo)
        body.addRow("演示", self._demo)
        body.addRow("一句话说明", self._summary)
        body.addRow("架构", self._architecture)
        body.addRow("亮点", self._highlights)
        body.addRow("难点", self._challenges)
        body.addRow("复盘", self._retro)
        body.addRow("CI 状态", self._ci)

    def _fill_list(self, rows: object) -> None:
        """刷新项目列表。"""
        records = cast(list[Any], rows)
        keep = self._current_id
        self._list.blockSignals(True)
        self._list.clear()
        for row in records:
            item = QtWidgets.QListWidgetItem(f"{row.name}\n{row.direction} · {row.status}")
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
        """选中项目后加载详情。"""
        if row < 0:
            return
        target = int(self._list.item(row).data(QtCore.Qt.ItemDataRole.UserRole))
        for record in self._vm.rows:
            if record.id == target:
                self._load(record)
                self._vm.select(record.id)
                return

    def _load(self, record: object) -> None:
        """写入项目字段。"""
        self._current_id = record.id  # type: ignore[attr-defined]
        self._name.setText(record.name)  # type: ignore[attr-defined]
        self._direction.setCurrentText(record.direction)  # type: ignore[attr-defined]
        self._role.setText(record.role)  # type: ignore[attr-defined]
        forms.set_date(self._start, record.start_date)  # type: ignore[attr-defined]
        forms.set_date(self._end, record.end_date)  # type: ignore[attr-defined]
        self._open.setChecked(record.end_date is None)  # type: ignore[attr-defined]
        index = self._status_combo.findData(record.status)  # type: ignore[attr-defined]
        self._status_combo.setCurrentIndex(max(index, 0))
        self._repo.setText(record.repo_url)  # type: ignore[attr-defined]
        self._demo.setText(record.demo_url)  # type: ignore[attr-defined]
        self._summary.setPlainText(record.summary)  # type: ignore[attr-defined]
        self._architecture.setPlainText(record.architecture)  # type: ignore[attr-defined]
        self._highlights.setPlainText("\n".join(record.highlights))  # type: ignore[attr-defined]
        self._challenges.setPlainText(record.challenges)  # type: ignore[attr-defined]
        self._retro.setPlainText(record.retrospective)  # type: ignore[attr-defined]
        self._ci.setText(record.ci_status)  # type: ignore[attr-defined]
        self._delete.setEnabled(True)

    def _new(self) -> None:
        """清空为新建。"""
        self._current_id = None
        self._name.clear()
        self._direction.setCurrentIndex(0)
        self._role.clear()
        self._open.setChecked(True)
        self._status_combo.setCurrentIndex(0)
        self._repo.clear()
        self._demo.clear()
        self._summary.clear()
        self._architecture.clear()
        self._highlights.clear()
        self._challenges.clear()
        self._retro.clear()
        self._ci.clear()
        self._metrics_editor.clear()
        self._tags.clear()
        self._delete.setEnabled(False)

    def _save(self) -> None:
        """保存项目与标签。"""
        data = self._collect()
        selected_tags = self._tags.selected_ids()
        was_new = self._current_id is None
        project_id = self._vm.add(data) if was_new else self._current_id
        if project_id is None:
            return
        if not was_new and not self._vm.update(project_id, data):
            return
        self._vm.set_tags(project_id, selected_tags)
        self._current_id = project_id

    def _collect(self) -> ProjectInput:
        """从控件构造输入。"""
        return ProjectInput(
            name=self._name.text(),
            direction=self._direction.currentText(),
            role=self._role.text(),
            start_date=forms.to_date(self._start),
            end_date=None if self._open.isChecked() else forms.to_date(self._end),
            status=str(self._status_combo.currentData()),
            repo_url=self._repo.text(),
            demo_url=self._demo.text(),
            summary=self._summary.toPlainText(),
            architecture=self._architecture.toPlainText(),
            highlights=self._lines(self._highlights.toPlainText()),
            challenges=self._challenges.toPlainText(),
            retrospective=self._retro.toPlainText(),
            ci_status=self._ci.text(),
            metrics=self._metrics_editor.collect(),
        )

    def _delete_current(self) -> None:
        """删除选中项目。"""
        if self._current_id is not None:
            self._vm.delete(self._current_id)
            self._current_id = None

    @staticmethod
    def _lines(value: str) -> list[str]:
        """按行拆分亮点。"""
        return [line.strip() for line in value.splitlines() if line.strip()]
