"""仓储：只做持久化，不含业务判断。"""

from __future__ import annotations

from sqlalchemy import select

from forgecv.features.settings.models import AppSetting
from forgecv.platform.adapters.db.session import SessionFactory, session_scope


class SettingsRepository:
    """app_settings 表的读写。"""

    def __init__(self, sessions: SessionFactory) -> None:
        """注入会话工厂，每次操作一个短事务。"""
        self._sessions = sessions

    def get(self, key: str) -> str | None:
        """读取单个键，不存在返回 None。"""
        with session_scope(self._sessions) as session:
            row = session.get(AppSetting, key)
            return None if row is None else row.value

    def all(self) -> dict[str, str]:
        """读取全部键值。"""
        with session_scope(self._sessions) as session:
            rows = session.scalars(select(AppSetting)).all()
            return {row.key: row.value for row in rows}

    def put(self, key: str, value: str) -> None:
        """写入或更新一个键。"""
        with session_scope(self._sessions) as session:
            row = session.get(AppSetting, key)
            if row is None:
                session.add(AppSetting(key=key, value=value))
                return
            row.value = value
