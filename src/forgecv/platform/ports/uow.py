"""工作单元端口：业务只依赖这个协议，不直接摸 engine。"""

from __future__ import annotations

from types import TracebackType
from typing import Protocol

from sqlalchemy.orm import Session


class UnitOfWork(Protocol):
    """一次事务的边界。"""

    @property
    def session(self) -> Session:
        """当前事务的会话。"""
        ...

    def __enter__(self) -> UnitOfWork:
        """进入事务。"""
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """提交或回滚并关闭。"""
        ...
