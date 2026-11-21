"""会话与工作单元：短事务、显式提交、异常回滚。"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from types import TracebackType

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

SessionFactory = sessionmaker[Session]


def create_session_factory(engine: Engine) -> SessionFactory:
    """创建会话工厂，提交后仍可读取属性。"""
    return sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


@contextmanager
def session_scope(factory: SessionFactory) -> Iterator[Session]:
    """只读或单次写操作推荐直接用这个上下文。"""
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class SessionUnitOfWork:
    """跨多次写操作的工作单元实现。"""

    def __init__(self, factory: SessionFactory) -> None:
        """记录工厂，进入时才开会话。"""
        self._factory = factory
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        """当前会话。"""
        if self._session is None:
            raise RuntimeError("工作单元尚未进入")
        return self._session

    def __enter__(self) -> SessionUnitOfWork:
        """开启新会话。"""
        self._session = self._factory()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """有异常则回滚，否则提交。"""
        if self._session is None:
            raise RuntimeError("工作单元尚未进入")
        session = self._session
        try:
            if exc_type is None:
                session.commit()
            else:
                session.rollback()
        finally:
            session.close()
            self._session = None
