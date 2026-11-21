"""概览页：统计卡片、能力雷达、标签分布与改进提示。"""

from __future__ import annotations

from typing import Any, cast

from forgecv.features.dashboard.schemas import DashboardData
from forgecv.features.dashboard.service import DIMENSIONS
from forgecv.features.dashboard.viewmodel import DashboardViewModel
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.kit.charts import RadarChart
from forgecv.platform.ui.qt import QtWidgets


class DashboardPage(QtWidgets.QWidget):
    """只读概览。"""

    def __init__(self, view_model: DashboardViewModel) -> None:
        """构建界面并加载。"""
        super().__init__()
        self._vm = view_model
        self._latest_radar: dict[str, int] | None = None
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addWidget(forms.title("概览", self))
        outer.addWidget(forms.muted("雷达为自评与档案完成度的混合口径，不是绝对能力排名。", self))

        self._stats_row = QtWidgets.QHBoxLayout()
        outer.addLayout(self._stats_row)
        self._stat_values: dict[str, QtWidgets.QLabel] = {}
        for label in ("学历", "经历", "项目", "技能", "标签"):
            frame, layout = forms.card(self, spacing=4)
            value = forms.title("0", frame)
            layout.addWidget(value)
            layout.addWidget(forms.muted(label, frame))
            self._stats_row.addWidget(frame)
            self._stat_values[label] = value

        content = QtWidgets.QHBoxLayout()
        self._radar = RadarChart(self)
        radar_card, radar_layout = forms.card(self)
        radar_layout.addWidget(forms.title("工程能力雷达", radar_card))
        radar_layout.addWidget(self._radar, 1)
        content.addWidget(radar_card, 3)

        right = QtWidgets.QVBoxLayout()
        tag_card, tag_layout = forms.card(self)
        tag_layout.addWidget(forms.title("标签分布", tag_card))
        self._tag_text = forms.muted("暂无标签", tag_card)
        self._tag_text.setWordWrap(True)
        tag_layout.addWidget(self._tag_text)
        tag_layout.addStretch(1)
        hint_card, hint_layout = forms.card(self)
        hint_layout.addWidget(forms.title("改进提示", hint_card))
        self._hints = forms.muted("暂无提示", hint_card)
        self._hints.setWordWrap(True)
        hint_layout.addWidget(self._hints)
        hint_layout.addStretch(1)
        right.addWidget(tag_card, 1)
        right.addWidget(hint_card, 1)
        content.addLayout(right, 2)
        outer.addLayout(content, 1)

        self._status = forms.muted("", self)
        outer.addWidget(self._status)
        self._vm.data_changed.connect(self._fill)
        self._vm.colors_changed.connect(self._paint)
        self._vm.status_changed.connect(self._status.setText)
        self._vm.load()

    def _fill(self, data: object) -> None:
        """写入统计、标签与提示。"""
        snapshot = cast(DashboardData, data)
        for label, value in snapshot.counts.items():
            if label in self._stat_values:
                self._stat_values[label].setText(str(value))
        self._tag_text.setText(self._format_tags(snapshot.tags))
        self._hints.setText(
            "\n".join(f"· {hint}" for hint in snapshot.hints) if snapshot.hints else "暂无提示"
        )
        self._latest_radar = snapshot.radar
        self._paint(self._vm.colors())

    def _paint(self, colors: object) -> None:
        """绘制雷达。"""
        snapshot = self._latest_radar
        if snapshot is None:
            return
        labels = list(DIMENSIONS)
        values = [int(snapshot[key]) for key in labels]
        self._radar.set_data(labels, values, cast(dict[str, str], colors))

    def _format_tags(self, tags: object) -> str:
        """标签分布转为多行文本。"""
        records = cast(dict[str, list[Any]], tags)
        if not records:
            return "暂无标签"
        lines: list[str] = []
        for dimension, rows in records.items():
            parts = " · ".join(f"{row.name}({row.count})" for row in rows)
            lines.append(f"{dimension}：{parts}")
        return "\n".join(lines)
