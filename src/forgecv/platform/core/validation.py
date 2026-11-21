"""通用输入校验：只返回错误文案，不抛异常，供各切片服务复用。"""

from __future__ import annotations

from datetime import date

URL_PREFIXES = ("http://", "https://")


def clean(value: str) -> str:
    """去掉首尾空白。"""
    return value.strip()


def email_error(value: str) -> str | None:
    """邮箱只做基本形态校验，避免误杀合法地址。"""
    if not value:
        return None
    if "@" not in value or value.startswith("@") or value.endswith("@"):
        return "邮箱格式不正确"
    return None


def url_error(value: str) -> str | None:
    """链接只接受 http(s)。"""
    if not value:
        return None
    if not value.startswith(URL_PREFIXES):
        return "链接必须以 http:// 或 https:// 开头"
    return None


def period_error(start: date | None, end: date | None, *, is_current: bool) -> str | None:
    """校验起止时间与「当前」标记是否自洽。"""
    if is_current and end is not None:
        return "标记为当前时不应填写结束日期"
    if not is_current and start is not None and end is None:
        return "请填写结束日期，或标记为当前"
    if start is not None and end is not None and end < start:
        return "结束日期不能早于开始日期"
    return None
