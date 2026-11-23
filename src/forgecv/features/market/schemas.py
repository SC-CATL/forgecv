"""视图数据：技能市场目录与展示条目。"""

from __future__ import annotations

from dataclasses import dataclass

MARKET_TAG = "市场认证"


@dataclass(frozen=True, slots=True)
class MarketSkill:
    """市场内置的一项技能。"""

    key: str
    name: str
    category: str
    level: int
    description: str
    market_tag: str = MARKET_TAG


@dataclass(frozen=True, slots=True)
class MarketEntry:
    """市场条目 + 当前候选人是否已学习。"""

    key: str
    name: str
    category: str
    level: int
    description: str
    market_tag: str
    learned: bool
