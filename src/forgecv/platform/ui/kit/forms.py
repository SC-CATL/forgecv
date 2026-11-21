"""表单与卡片小部件：统一页面骨架，页面层不再重复布局代码。"""

from __future__ import annotations

from datetime import date

from forgecv.platform.ui.qt import QtCore, QtWidgets


def title(text: str, parent: QtWidgets.QWidget | None = None) -> QtWidgets.QLabel:
    """页面主标题。"""
    label = QtWidgets.QLabel(text, parent)
    label.setObjectName("PageTitle")
    return label


def muted(text: str = "", parent: QtWidgets.QWidget | None = None) -> QtWidgets.QLabel:
    """次要说明文字。"""
    label = QtWidgets.QLabel(text, parent)
    label.setObjectName("Muted")
    return label


def card(
    parent: QtWidgets.QWidget, *, spacing: int = 12
) -> tuple[QtWidgets.QFrame, QtWidgets.QVBoxLayout]:
    """带边框卡片与它的纵向布局。"""
    frame = QtWidgets.QFrame(parent)
    frame.setObjectName("Card")
    layout = QtWidgets.QVBoxLayout(frame)
    layout.setSpacing(spacing)
    return frame, layout


def form() -> QtWidgets.QFormLayout:
    """统一的表单布局。"""
    layout = QtWidgets.QFormLayout()
    layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
    layout.setSpacing(8)
    return layout


def button(
    text: str,
    parent: QtWidgets.QWidget | None = None,
    *,
    secondary: bool = False,
    danger: bool = False,
) -> QtWidgets.QPushButton:
    """主/次/危险三种按钮。"""
    widget = QtWidgets.QPushButton(text, parent)
    if danger:
        widget.setObjectName("Danger")
    elif secondary:
        widget.setObjectName("Secondary")
    return widget


def date_edit(
    parent: QtWidgets.QWidget | None = None, *, initial: date | None = None
) -> QtWidgets.QDateEdit:
    """带日历弹窗的日期输入。"""
    widget = QtWidgets.QDateEdit(parent)
    widget.setCalendarPopup(True)
    widget.setDisplayFormat("yyyy-MM-dd")
    value = initial or date.today()
    widget.setDate(QtCore.QDate(value.year, value.month, value.day))
    return widget


def to_date(widget: QtWidgets.QDateEdit) -> date:
    """QDate 转 Python date。"""
    value = widget.date()
    return date(value.year(), value.month(), value.day())


def set_date(widget: QtWidgets.QDateEdit, value: date | None) -> None:
    """写入日期；None 时回到今天，由调用方的「当前」复选框兜底。"""
    target = value or date.today()
    widget.setDate(QtCore.QDate(target.year, target.month, target.day))


def scroll_form(
    parent: QtWidgets.QWidget,
) -> tuple[QtWidgets.QScrollArea, QtWidgets.QVBoxLayout]:
    """可滚动的编辑区，返回容器与内容布局。"""
    area = QtWidgets.QScrollArea(parent)
    area.setWidgetResizable(True)
    area.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
    body = QtWidgets.QWidget(area)
    layout = QtWidgets.QVBoxLayout(body)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(16)
    area.setWidget(body)
    return area, layout
