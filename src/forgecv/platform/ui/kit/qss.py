"""全局样式模板：只读取令牌，不出现硬编码颜色。"""

from __future__ import annotations

from string import Template

_QSS = Template(
    """
QWidget {
    background: $bg_canvas;
    color: $fg_default;
    font-family: "$font_family";
    font-size: ${font_body}pt;
}
#NavList {
    background: $bg_surface;
    border: none;
    padding: $space_sm;
}
#NavList::item {
    padding: $space_sm $space_md;
    border-radius: $radius_sm;
    color: $fg_muted;
}
#NavList::item:selected {
    background: $bg_elevated;
    color: $fg_default;
}
#PageTitle {
    font-size: ${font_title}pt;
    font-weight: 600;
}
#Card {
    background: $bg_surface;
    border: 1px solid $border;
    border-radius: $radius_md;
    padding: $space_lg;
}
QPushButton {
    background: $accent;
    color: $accent_fg;
    border: none;
    border-radius: $radius_sm;
    padding: $space_sm $space_lg;
}
QPushButton:hover {
    background: $accent_hover;
}
QPushButton#Secondary {
    background: transparent;
    color: $accent;
    border: 1px solid $accent;
}
QPushButton#Danger {
    background: $danger;
    color: $accent_fg;
}
QComboBox, QLineEdit, QSpinBox {
    background: $bg_elevated;
    border: 1px solid $border;
    border-radius: $radius_sm;
    padding: $space_xs $space_sm;
}
QTextEdit, QPlainTextEdit, QDateEdit {
    background: $bg_elevated;
    border: 1px solid $border;
    border-radius: $radius_sm;
    padding: $space_xs $space_sm;
}
QTableWidget {
    background: $bg_elevated;
    border: 1px solid $border;
    border-radius: $radius_sm;
    gridline-color: $border;
}
QHeaderView::section {
    background: $bg_elevated;
    border: none;
    padding: $space_xs $space_sm;
}
QListWidget#ItemList {
    background: $bg_surface;
    border: 1px solid $border;
    border-radius: $radius_md;
    padding: $space_sm;
}
QListWidget#ItemList::item {
    padding: $space_sm;
    border-radius: $radius_sm;
}
QListWidget#ItemList::item:selected {
    background: $bg_elevated;
}
QCheckBox {
    background: transparent;
}
QLabel#Muted {
    color: $fg_muted;
}
QStatusBar {
    background: $bg_surface;
    color: $fg_muted;
}
"""
)


def render(values: dict[str, str]) -> str:
    """把令牌字典渲染为 QSS 文本。"""
    return _QSS.substitute(values).strip() + "\n"
