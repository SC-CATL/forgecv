"""通用校验函数。"""

from __future__ import annotations

from datetime import date

from forgecv.platform.core.validation import email_error, period_error, url_error


def test_email_error() -> None:
    """空值放行，缺 @ 拦截。"""
    assert email_error("") is None
    assert email_error("a@b.com") is None
    assert email_error("ab.com") is not None


def test_url_error() -> None:
    """只接受 http(s)。"""
    assert url_error("") is None
    assert url_error("https://example.com") is None
    assert url_error("ftp://example.com") is not None


def test_period_error() -> None:
    """当前态与结束日期互斥，结束不早于开始。"""
    assert period_error(date(2020, 1, 1), None, is_current=True) is None
    assert period_error(date(2020, 1, 1), None, is_current=False) is not None
    assert period_error(date(2020, 1, 1), date(2019, 1, 1), is_current=False) is not None
    assert period_error(None, None, is_current=True) is None
