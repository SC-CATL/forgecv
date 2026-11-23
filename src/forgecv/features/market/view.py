"""技能市场页：浏览项目认可技能并一键学习。"""

from __future__ import annotations

from typing import cast

from forgecv.features.market.schemas import MarketEntry
from forgecv.features.market.viewmodel import MarketViewModel
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.kit.format import level_label
from forgecv.platform.ui.qt import QtCore, QtWidgets


class MarketPage(QtWidgets.QWidget):
    """左侧市场目录，右侧技能详情与学习按钮。"""

    def __init__(self, view_model: MarketViewModel) -> None:
        """构建界面并加载目录。"""
        super().__init__()
        self._vm = view_model
        self._selected_key: str | None = None
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addWidget(forms.title("技能市场", self))
        outer.addWidget(
            forms.muted(
                "学习后自动写入技能矩阵，并带上「市场认证」标签，表示本项目认可该技能。",
                self,
            )
        )

        split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        split.addWidget(self._build_list(split))
        split.addWidget(self._build_detail(split))
        split.setSizes([320, 740])
        outer.addWidget(split, 1)

        self._vm.rows_changed.connect(self._fill_rows)
        self._vm.status_changed.connect(self._status.setText)
        self._category.currentIndexChanged.connect(self._reload)
        self._vm.load()

    def _build_list(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """左侧分类筛选与技能目录。"""
        panel = QtWidgets.QWidget(parent)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 12, 0)
        self._category = QtWidgets.QComboBox(panel)
        self._category.addItem("全部分类", "")
        for name in self._vm.categories:
            self._category.addItem(name, name)
        self._list = QtWidgets.QListWidget(panel)
        self._list.setObjectName("ItemList")
        self._list.currentRowChanged.connect(self._select_row)
        self._count = forms.muted("", panel)
        layout.addWidget(self._category)
        layout.addWidget(self._list, 1)
        layout.addWidget(self._count)
        return panel

    def _build_detail(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """右侧技能详情卡片。"""
        area, layout = forms.scroll_form(parent)
        frame, card_layout = forms.card(area)
        self._name = forms.title("选择一项技能", frame)
        self._meta = forms.muted("", frame)
        self._tag = forms.muted("", frame)
        self._description = QtWidgets.QLabel("", frame)
        self._description.setWordWrap(True)
        self._hint = forms.muted(
            "加入后可在「技能矩阵」继续补充使用年限、自评分与证据链。", frame
        )
        self._learn = forms.button("学习并加入技能矩阵", frame)
        self._learn.setEnabled(False)
        self._learn.clicked.connect(self._learn_current)
        card_layout.addWidget(self._name)
        card_layout.addWidget(self._meta)
        card_layout.addWidget(self._tag)
        card_layout.addWidget(self._description)
        card_layout.addWidget(self._hint)
        card_layout.addWidget(self._learn)
        layout.addWidget(frame)
        self._status = forms.muted("", area)
        layout.addWidget(self._status)
        layout.addStretch(1)
        return area

    def _reload(self, _index: int = 0) -> None:
        """分类变化后重新加载。"""
        category = str(self._category.currentData() or "") or None
        self._vm.load(category)

    def _fill_rows(self, rows: object) -> None:
        """刷新市场目录，尽量保留当前选中项。"""
        records = cast(list[MarketEntry], rows)
        keep = self._selected_key
        self._count.setText(f"当前筛选 {len(records)} 项")
        self._list.blockSignals(True)
        self._list.clear()
        for entry in records:
            suffix = f" · {entry.market_tag}" if entry.learned else ""
            item = QtWidgets.QListWidgetItem(
                f"{entry.name}\n{entry.category} · {level_label(entry.level)}{suffix}"
            )
            item.setData(QtCore.Qt.ItemDataRole.UserRole, entry.key)
            self._list.addItem(item)
        self._list.blockSignals(False)
        if not records:
            self._selected_key = None
            self._clear_detail()
            return
        index = next(
            (i for i, entry in enumerate(records) if entry.key == keep), 0
        )
        self._list.setCurrentRow(index)

    def _select_row(self, row: int) -> None:
        """选中目录项后展示详情。"""
        if 0 <= row < len(self._vm.rows):
            self._show(self._vm.rows[row])

    def _show(self, entry: MarketEntry) -> None:
        """写入详情并同步学习按钮状态。"""
        self._selected_key = entry.key
        self._name.setText(entry.name)
        self._meta.setText(f"{entry.category} · 建议熟练度：{level_label(entry.level)}")
        state = "已加入技能矩阵" if entry.learned else "学习后自动标记"
        self._tag.setText(f"{entry.market_tag} · {state}")
        self._description.setText(entry.description)
        self._learn.setEnabled(not entry.learned)
        self._learn.setText("已加入技能矩阵" if entry.learned else "学习并加入技能矩阵")

    def _clear_detail(self) -> None:
        """空目录时回到占位状态。"""
        self._name.setText("当前分类暂无技能")
        self._meta.clear()
        self._tag.clear()
        self._description.clear()
        self._learn.setEnabled(False)
        self._learn.setText("学习并加入技能矩阵")

    def _learn_current(self) -> None:
        """学习当前选中的市场技能。"""
        if self._selected_key is not None:
            self._vm.learn(self._selected_key)
