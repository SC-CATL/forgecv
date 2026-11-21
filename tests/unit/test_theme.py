"""主题令牌与 QSS 生成。"""

from __future__ import annotations

from forgecv.platform.ui.kit.theme import (
    MODES,
    ThemeService,
    build_stylesheet,
    flatten,
    load_tokens,
)


def test_tokens_cover_every_mode() -> None:
    """每种模式都有完整颜色组。"""
    tokens = load_tokens()
    for mode in MODES:
        assert {"bg_canvas", "fg_default", "accent", "danger"} <= set(tokens[mode])


def test_flatten_exposes_spacing_and_radius() -> None:
    """分组令牌被展平为 QSS 占位符。"""
    flat = flatten(load_tokens())
    assert flat["space_md"] == "12"
    assert flat["radius_sm"] == "4"
    assert flat["font_family"]


def test_stylesheet_uses_mode_colors() -> None:
    """深色样式包含深色令牌值。"""
    tokens = load_tokens()
    light = build_stylesheet(tokens, "light")
    dark = build_stylesheet(tokens, "dark")
    assert tokens["light"]["bg_canvas"] in light
    assert tokens["dark"]["bg_canvas"] in dark
    assert "$" not in dark


def test_unknown_theme_falls_back_to_system() -> None:
    """非法主题名解析为具体模式而非崩溃。"""
    service = ThemeService()
    assert service.resolve("nope") in MODES


def test_apply_switches_mode_and_emits(qapp) -> None:
    """应用主题后当前模式更新。"""
    service = ThemeService()
    seen: list[str] = []
    service.changed.connect(seen.append)
    assert service.apply("dark") == "dark"
    assert service.current == "dark"
    assert service.color("bg_canvas").startswith("#")
    assert seen == ["dark"]
