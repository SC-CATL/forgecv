"""Result 值语义。"""

from __future__ import annotations

import pytest

from forgecv.platform.core.result import Result


def test_ok_carries_value() -> None:
    """成功结果可取到原值。"""
    result = Result.ok(42)
    assert result.is_ok
    assert result.unwrap() == 42
    assert result.error() is None


def test_err_carries_error() -> None:
    """失败结果保留错误且不可取值。"""
    result = Result.err("bad")
    assert not result.is_ok
    assert result.error() == "bad"
    with pytest.raises(RuntimeError):
        result.unwrap()


def test_unwrap_or_falls_back() -> None:
    """失败时返回默认值。"""
    assert Result.ok(1).unwrap_or(9) == 1
    assert Result.err("x").unwrap_or(9) == 9
