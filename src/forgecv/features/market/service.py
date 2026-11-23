"""领域服务：技能市场目录与学习动作。"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

from forgecv.features.market.catalog import MARKET_SKILLS
from forgecv.features.market.schemas import MarketEntry, MarketSkill
from forgecv.platform.core.errors import ValidationError
from forgecv.platform.core.result import Result


class SkillGateway(Protocol):
    """市场只依赖技能切片的最小写入口。"""

    def learn_market_skill(
        self,
        *,
        name: str,
        category: str,
        level: int,
        notes: str,
        market_key: str,
        market_tag: str,
    ) -> Result[Any, ValidationError]:
        """学习一项市场技能。"""
        ...

    def learned_market_keys(self) -> set[str]:
        """已学习市场技能标识。"""
        ...


class MarketService:
    """只读目录 + 学习写入技能矩阵。"""

    def __init__(
        self, skills: SkillGateway, catalog: Sequence[MarketSkill] = MARKET_SKILLS
    ) -> None:
        """注入技能服务与内置目录。"""
        self._skills = skills
        self._catalog = tuple(catalog)

    def categories(self) -> tuple[str, ...]:
        """目录里出现的分类，按首次出现顺序。"""
        return tuple(dict.fromkeys(item.category for item in self._catalog))

    def entries(self, category: str | None = None) -> list[MarketEntry]:
        """目录条目并标注是否已学习。"""
        learned = self._skills.learned_market_keys()
        return [
            MarketEntry(
                key=item.key,
                name=item.name,
                category=item.category,
                level=item.level,
                description=item.description,
                market_tag=item.market_tag,
                learned=item.key in learned,
            )
            for item in self._catalog
            if category is None or item.category == category
        ]

    def learn(self, key: str) -> Result[str, ValidationError]:
        """学习指定市场技能，返回技能名称。"""
        item = self._find(key)
        if item is None:
            return Result.err(ValidationError(f"市场技能不存在：{key}"))
        result = self._skills.learn_market_skill(
            name=item.name,
            category=item.category,
            level=item.level,
            notes=item.description,
            market_key=item.key,
            market_tag=item.market_tag,
        )
        if not result.is_ok:
            error = result.error()
            return Result.err(error or ValidationError(f"学习失败：{key}"))
        return Result.ok(item.name)

    def _find(self, key: str) -> MarketSkill | None:
        """按标识查找目录项。"""
        return next((item for item in self._catalog if item.key == key), None)
