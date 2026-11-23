"""视图模型：技能市场目录筛选与学习状态。"""

from __future__ import annotations

from forgecv.features.market.schemas import MARKET_TAG, MarketEntry
from forgecv.features.market.service import MarketService
from forgecv.platform.ui.qt import QtCore, Signal


class MarketViewModel(QtCore.QObject):
    """技能市场页状态。"""

    rows_changed = Signal(object)
    status_changed = Signal(str)

    def __init__(self, service: MarketService) -> None:
        """注入市场服务。"""
        super().__init__()
        self._service = service
        self._rows: list[MarketEntry] = []
        self._category: str | None = None

    @property
    def rows(self) -> list[MarketEntry]:
        """当前目录条目。"""
        return self._rows

    @property
    def categories(self) -> tuple[str, ...]:
        """全部可选分类。"""
        return self._service.categories()

    @property
    def category(self) -> str | None:
        """当前筛选分类。"""
        return self._category

    def load(self, category: str | None = None) -> None:
        """按分类刷新目录与学习状态。"""
        self._category = category or None
        self._rows = self._service.entries(self._category)
        self.rows_changed.emit(self._rows)
        learned = sum(1 for row in self._rows if row.learned)
        self.status_changed.emit(f"共 {len(self._rows)} 项 · 已学习 {learned} 项")

    def learn(self, key: str) -> bool:
        """学习一项技能并刷新目录。"""
        result = self._service.learn(key)
        if not result.is_ok:
            self.status_changed.emit(f"学习失败：{result.error()}")
            return False
        name = result.unwrap()
        self.load(self._category)
        self.status_changed.emit(f"{name} 已加入技能矩阵（{MARKET_TAG}）")
        return True
