"""简历版本页：版本编排、实时预览、健康度与 JD 覆盖。"""

from __future__ import annotations

from typing import Any, cast

from forgecv.features.resume.checks import LEVELS, CheckIssue
from forgecv.features.resume.jd import JDReport
from forgecv.features.resume.models import TEMPLATES, ResumeVersion
from forgecv.features.resume.schemas import ItemCatalog, VersionInput
from forgecv.features.resume.viewmodel import ResumeViewModel
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.qt import QtCore, QtWidgets


class ResumePage(QtWidgets.QWidget):
    """左版本 / 中编排 / 右预览。"""

    def __init__(self, view_model: ResumeViewModel) -> None:
        """构建界面并加载。"""
        super().__init__()
        self._vm = view_model
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addWidget(forms.title("简历版本", self))
        outer.addWidget(
            forms.muted(
                "按岗位勾选条目；预览与未来的 Word 导出使用同一份渲染数据。", self
            )
        )
        split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        split.addWidget(self._build_versions(split))
        split.addWidget(self._build_editor(split))
        split.addWidget(self._build_preview(split))
        split.setSizes([220, 520, 420])
        outer.addWidget(split, 1)

        self._vm.versions_changed.connect(self._fill_versions)
        self._vm.version_changed.connect(self._fill_version)
        self._vm.catalog_changed.connect(self._fill_catalog)
        self._vm.preview_changed.connect(self._preview.setPlainText)
        self._vm.checks_changed.connect(self._fill_checks)
        self._vm.jd_changed.connect(self._fill_jd)
        self._vm.status_changed.connect(self._status.setText)
        self._vm.load()

    def _build_versions(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """左侧版本列表。"""
        panel = QtWidgets.QWidget(parent)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 12, 0)
        self._versions = QtWidgets.QListWidget(panel)
        self._versions.setObjectName("ItemList")
        self._versions.currentRowChanged.connect(self._on_version)
        layout.addWidget(self._versions, 1)
        add = forms.button("新建版本", panel)
        add.clicked.connect(self._create)
        delete = forms.button("删除当前", panel, danger=True)
        delete.clicked.connect(self._vm.delete_current)
        layout.addWidget(add)
        layout.addWidget(delete)
        return panel

    def _build_editor(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """中间编辑区。"""
        area, layout = forms.scroll_form(parent)
        layout.addWidget(self._build_settings(area))
        layout.addWidget(self._build_items(area))
        layout.addWidget(self._build_jd(area))
        self._status = forms.muted("", area)
        layout.addWidget(self._status)
        layout.addStretch(1)
        return area

    def _build_settings(self, parent: QtWidgets.QWidget) -> QtWidgets.QFrame:
        """版本设置卡片。"""
        frame, layout = forms.card(parent)
        layout.addWidget(forms.title("版本设置", frame))
        body = forms.form()
        self._name = QtWidgets.QLineEdit(frame)
        self._target = QtWidgets.QLineEdit(frame)
        self._template = QtWidgets.QComboBox(frame)
        self._template.addItems(TEMPLATES)
        self._default = QtWidgets.QCheckBox("设为默认版本", frame)
        body.addRow("版本名", self._name)
        body.addRow("目标岗位", self._target)
        body.addRow("导出模板", self._template)
        body.addRow("", self._default)
        layout.addLayout(body)
        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        save = forms.button("保存设置", frame)
        save.clicked.connect(self._save_settings)
        row.addWidget(save)
        layout.addLayout(row)
        return frame

    def _build_items(self, parent: QtWidgets.QWidget) -> QtWidgets.QFrame:
        """条目勾选与排序卡片。"""
        frame, layout = forms.card(parent)
        layout.addWidget(forms.title("条目编排", frame))
        layout.addWidget(forms.muted("勾选加入版本；未勾选时预览包含全部内容。", frame))
        self._available = QtWidgets.QListWidget(frame)
        self._available.setObjectName("ItemList")
        self._available.setMinimumHeight(170)
        self._available.itemChanged.connect(self._on_item_toggled)
        layout.addWidget(self._available)
        self._selected = QtWidgets.QListWidget(frame)
        self._selected.setObjectName("ItemList")
        self._selected.setFixedHeight(90)
        layout.addWidget(self._selected)
        row = QtWidgets.QHBoxLayout()
        up = forms.button("上移", frame, secondary=True)
        up.clicked.connect(lambda: self._move(-1))
        down = forms.button("下移", frame, secondary=True)
        down.clicked.connect(lambda: self._move(1))
        row.addWidget(up)
        row.addWidget(down)
        row.addStretch(1)
        layout.addLayout(row)
        return frame

    def _build_jd(self, parent: QtWidgets.QWidget) -> QtWidgets.QFrame:
        """JD 分析卡片。"""
        frame, layout = forms.card(parent)
        layout.addWidget(forms.title("岗位 JD 覆盖", frame))
        self._jd_text = QtWidgets.QTextEdit(frame)
        self._jd_text.setFixedHeight(90)
        self._jd_text.setPlaceholderText("粘贴目标岗位 JD，本地分析，不联网")
        layout.addWidget(self._jd_text)
        self._jd_result = forms.muted("粘贴 JD 后点击分析", frame)
        self._jd_result.setWordWrap(True)
        layout.addWidget(self._jd_result)
        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        analyze = forms.button("分析覆盖", frame)
        analyze.clicked.connect(self._analyze)
        row.addWidget(analyze)
        layout.addLayout(row)
        return frame

    def _build_preview(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """右侧预览与检查结果。"""
        panel = QtWidgets.QWidget(parent)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(12, 0, 0, 0)
        self._preview = QtWidgets.QPlainTextEdit(panel)
        self._preview.setReadOnly(True)
        layout.addWidget(self._preview, 3)
        frame, card_layout = forms.card(panel)
        card_layout.addWidget(forms.title("健康度检查", frame))
        self._checks = forms.muted("", frame)
        self._checks.setWordWrap(True)
        card_layout.addWidget(self._checks)
        layout.addWidget(frame, 1)
        return panel

    def _fill_versions(self, rows: object) -> None:
        """刷新版本列表。"""
        records = cast(list[Any], rows)
        self._versions.blockSignals(True)
        self._versions.clear()
        for row in records:
            suffix = "（默认）" if row.is_default else ""
            item = QtWidgets.QListWidgetItem(f"{row.name}{suffix}")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, row.id)
            self._versions.addItem(item)
        self._versions.blockSignals(False)
        current = self._vm.current
        if current is not None:
            self._select_version_row(current.id)

    def _fill_version(self, version: object) -> None:
        """回填版本设置。"""
        record = cast(ResumeVersion, version)
        self._name.setText(record.name)
        self._target.setText(record.target_role)
        index = self._template.findText(record.template)
        self._template.setCurrentIndex(max(index, 0))
        self._default.setChecked(record.is_default)
        self._jd_text.setPlainText(record.target_jd)
        self._select_version_row(record.id)

    def _fill_catalog(self, catalog: object) -> None:
        """写入可选与已选条目。"""
        snapshot = cast(ItemCatalog, catalog)
        selected_keys = {item.key for item in snapshot.selected}
        self._available.blockSignals(True)
        self._available.clear()
        for option in snapshot.available:
            item = QtWidgets.QListWidgetItem(option.label)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, option.key)
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            state = (
                QtCore.Qt.CheckState.Checked
                if option.key in selected_keys
                else QtCore.Qt.CheckState.Unchecked
            )
            item.setCheckState(state)
            self._available.addItem(item)
        self._available.blockSignals(False)
        self._selected.clear()
        for entry in snapshot.selected:
            widget = QtWidgets.QListWidgetItem(entry.label)
            widget.setData(QtCore.Qt.ItemDataRole.UserRole, entry.row_id)
            self._selected.addItem(widget)

    def _fill_checks(self, issues: object) -> None:
        """渲染健康度建议。"""
        records = cast(list[CheckIssue], issues)
        if not records:
            self._checks.setText("没有发现明显问题。")
            return
        lines = [f"[{LEVELS.get(row.level, row.level)}] {row.message}" for row in records]
        self._checks.setText("\n".join(lines))

    def _fill_jd(self, report: object) -> None:
        """渲染 JD 覆盖率。"""
        result = cast(JDReport, report)
        if result.message and not result.missing and not result.matched:
            self._jd_result.setText(result.message)
            return
        matched = "、".join(result.matched) or "无"
        missing = "、".join(result.missing) or "无"
        self._jd_result.setText(
            f"覆盖率 {result.coverage}% · 已匹配：{matched} · 缺口：{missing}"
        )

    def _on_version(self, row: int) -> None:
        """切换版本。"""
        if row < 0:
            return
        version_id = int(self._versions.item(row).data(QtCore.Qt.ItemDataRole.UserRole))
        current = self._vm.current
        if current is None or current.id != version_id:
            self._vm.select(version_id)

    def _on_item_toggled(self, item: QtWidgets.QListWidgetItem) -> None:
        """勾选状态变化时增删条目。"""
        key = str(item.data(QtCore.Qt.ItemDataRole.UserRole))
        checked = item.checkState() == QtCore.Qt.CheckState.Checked
        self._vm.toggle_item(key, checked)

    def _create(self) -> None:
        """新建一个空版本。"""
        name = self._name.text().strip() or "新版本"
        self._vm.create(VersionInput(name=name, target_role=self._target.text()))

    def _save_settings(self) -> None:
        """保存当前版本设置。"""
        self._vm.update(
            VersionInput(
                name=self._name.text(),
                target_role=self._target.text(),
                target_jd=self._jd_text.toPlainText(),
                template=self._template.currentText(),
                theme="light",
                is_default=self._default.isChecked(),
            )
        )

    def _analyze(self) -> None:
        """触发 JD 分析。"""
        self._vm.analyze_jd(self._jd_text.toPlainText())

    def _move(self, delta: int) -> None:
        """上移或下移已选条目。"""
        item = self._selected.currentItem()
        if item is not None:
            self._vm.move_item(int(item.data(QtCore.Qt.ItemDataRole.UserRole)), delta)

    def _select_version_row(self, version_id: int) -> None:
        """同步左侧列表选中行。"""
        for row in range(self._versions.count()):
            if self._versions.item(row).data(QtCore.Qt.ItemDataRole.UserRole) == version_id:
                self._versions.blockSignals(True)
                self._versions.setCurrentRow(row)
                self._versions.blockSignals(False)
                return
