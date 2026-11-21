"""自绘弹窗：语义结果记录。"""

from __future__ import annotations

from forgecv.platform.ui.kit.dialogs import _CardDialog


def test_dialog_records_outcome(qapp) -> None:
    """点击按钮后记录语义结果。"""
    dialog = _CardDialog(None, "标题", "正文", [("确定", "", "confirm")])
    dialog._finish("confirm")
    assert dialog.outcome() == "confirm"


def test_dialog_defaults_to_close(qapp) -> None:
    """未选择时视为关闭。"""
    dialog = _CardDialog(None, "标题", "正文", [("关闭", "", "close")])
    assert dialog.outcome() == "close"
