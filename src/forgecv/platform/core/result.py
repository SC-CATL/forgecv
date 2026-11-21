"""Result：可预期失败用值表达，异常只用于意外。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True, slots=True)
class Result(Generic[T, E]):
    """成功携带值，失败携带错误。"""

    _value: T | None = None
    _error: E | None = None

    @classmethod
    def ok(cls, value: T) -> Result[T, E]:
        """构造成功结果。"""
        return cls(_value=value)

    @classmethod
    def err(cls, error: E) -> Result[T, E]:
        """构造失败结果。"""
        return cls(_error=error)

    @property
    def is_ok(self) -> bool:
        """是否成功。"""
        return self._error is None

    def unwrap(self) -> T:
        """取成功值，失败时抛错。"""
        if self._error is not None or self._value is None:
            raise RuntimeError(f"unwrap on failed result: {self._error!r}")
        return self._value

    def unwrap_or(self, default: T) -> T:
        """成功时取值，否则取默认值。"""
        return self._value if self._error is None and self._value is not None else default

    def error(self) -> E | None:
        """取错误值。"""
        return self._error
