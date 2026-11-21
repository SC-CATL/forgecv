"""领域服务：校验输入，返回 Result，不碰 Qt。"""

from __future__ import annotations

from forgecv.features.settings.repository import SettingsRepository
from forgecv.platform.config import THEMES
from forgecv.platform.core.errors import ValidationError
from forgecv.platform.core.result import Result

THEME_KEY = "ui.theme"
DEFAULT_THEME = "system"


class SettingsService:
    """主题偏好的唯一写入口。"""

    def __init__(self, repository: SettingsRepository) -> None:
        """注入仓储。"""
        self._repository = repository

    def theme(self) -> str:
        """读取主题，非法历史值回退默认。"""
        value = self._repository.get(THEME_KEY)
        return value if value in THEMES else DEFAULT_THEME

    def save_theme(self, mode: str) -> Result[str, ValidationError]:
        """校验后保存主题。"""
        if mode not in THEMES:
            return Result.err(ValidationError(f"未知主题：{mode}", allowed=list(THEMES)))
        self._repository.put(THEME_KEY, mode)
        return Result.ok(mode)
