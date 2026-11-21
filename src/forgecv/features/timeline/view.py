"""统一时间轴页：学历、工作、项目按时间排列。"""

from __future__ import annotations

from typing import cast

from forgecv.features.timeline.schemas import TimelineData
from forgecv.features.timeline.viewmodel import TimelineViewModel
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.kit.format import period
from forgecv.platform.ui.qt import QtWidgets


class TimelinePage(QtWidgets.QWidget):
    """只读的纵向时间轴。"""

    def __init__(self, view_model: TimelineViewModel) -> None:
        """构建界面并加载。"""
        super().__init__()
        self._vm = view_model
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addWidget(forms.title("时间轴", self))
        outer.addWidget(forms.muted("学历、工作与项目叠加展示；同分区重叠会给出提示。", self))

        frame, layout = forms.card(self)
        row = QtWidgets.QHBoxLayout()
        self._summary = forms.muted("", frame)
        refresh = forms.button("刷新", frame, secondary=True)
        refresh.clicked.connect(self._vm.load)
        row.addWidget(self._summary)
        row.addStretch(1)
        row.addWidget(refresh)
        layout.addLayout(row)

        self._warnings = forms.muted("", frame)
        self._warnings.setWordWrap(True)
        layout.addWidget(self._warnings)

        self._list = QtWidgets.QListWidget(frame)
        self._list.setObjectName("ItemList")
        layout.addWidget(self._list, 1)
        outer.addWidget(frame, 1)

        self._vm.data_changed.connect(self._fill)
        self._vm.status_changed.connect(self._summary.setText)
        self._vm.load()

    def _fill(self, data: object) -> None:
        """写入事件与提示。"""
        snapshot = cast(TimelineData, data)
        self._list.clear()
        for event in snapshot.events:
            text = (
                f"{period(event.start, event.end, is_current=event.is_current)} · {event.kind}\n"
                f"{event.title} · {event.subtitle}"
            )
            self._list.addItem(QtWidgets.QListWidgetItem(text))
        if not snapshot.events:
            self._list.addItem(QtWidgets.QListWidgetItem("暂无事件，先去录入学历或项目。"))
        self._warnings.setText("；".join(snapshot.warnings))
