"""雷达图：只读取外部传入的颜色，不在控件内写死任何色值。"""

from __future__ import annotations

import math

from forgecv.platform.ui.qt import QtCore, QtGui, QtWidgets

RINGS = 4
LABEL_PADDING = 18


class RadarChart(QtWidgets.QWidget):
    """八维能力雷达，标注「自评」。"""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """初始化空数据。"""
        super().__init__(parent)
        self._labels: list[str] = []
        self._values: list[int] = []
        self._colors: dict[str, str] = {}
        self.setMinimumHeight(320)

    def set_data(
        self, labels: list[str], values: list[int], colors: dict[str, str]
    ) -> None:
        """写入维度、分值与主题颜色，然后重绘。"""
        self._labels = labels
        self._values = values
        self._colors = colors
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:  # noqa: N802
        """自绘网格、轴、多边形与标签。"""
        super().paintEvent(event)
        if not self._labels or not self._colors:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        center = QtCore.QPointF(self.width() / 2, self.height() / 2)
        radius = min(self.width(), self.height()) / 2 - LABEL_PADDING * 2
        self._draw_grid(painter, center, radius)
        self._draw_polygon(painter, center, radius)
        self._draw_labels(painter, center, radius)
        painter.end()

    def _draw_grid(
        self, painter: QtGui.QPainter, center: QtCore.QPointF, radius: float
    ) -> None:
        """同心多边形与轴线。"""
        painter.setPen(QtGui.QPen(QtGui.QColor(self._colors["border"]), 1))
        count = len(self._labels)
        for ring in range(1, RINGS + 1):
            scale = radius * ring / RINGS
            points = [self._point(center, scale, index) for index in range(count)]
            painter.drawPolygon(QtGui.QPolygonF(points))
        for index in range(count):
            painter.drawLine(center, self._point(center, radius, index))

    def _draw_polygon(
        self, painter: QtGui.QPainter, center: QtCore.QPointF, radius: float
    ) -> None:
        """数据多边形与顶点。"""
        accent = QtGui.QColor(self._colors["accent"])
        fill = QtGui.QColor(accent)
        fill.setAlpha(60)
        painter.setBrush(fill)
        painter.setPen(QtGui.QPen(accent, 2))
        points = [
            self._point(center, radius * min(max(value, 0), 100) / 100, index)
            for index, value in enumerate(self._values)
        ]
        painter.drawPolygon(QtGui.QPolygonF(points))
        painter.setBrush(QtGui.QColor(self._colors["surface"]))
        for point in points:
            painter.drawEllipse(point, 3, 3)

    def _draw_labels(
        self, painter: QtGui.QPainter, center: QtCore.QPointF, radius: float
    ) -> None:
        """维度名与分值。"""
        painter.setPen(QtGui.QPen(QtGui.QColor(self._colors["muted"]), 1))
        for index, label in enumerate(self._labels):
            point = self._point(center, radius + 16, index)
            text = f"{label} {self._values[index]}"
            rect = painter.fontMetrics().boundingRect(text)
            painter.drawText(
                QtCore.QPointF(point.x() - rect.width() / 2, point.y() + rect.height() / 4),
                text,
            )

    def _point(self, center: QtCore.QPointF, radius: float, index: int) -> QtCore.QPointF:
        """第 index 个维度的坐标，从正上方开始顺时针。"""
        total = len(self._labels) or 1
        angle = math.pi * 2 * index / total - math.pi / 2
        return QtCore.QPointF(
            center.x() + radius * math.cos(angle),
            center.y() + radius * math.sin(angle),
        )
