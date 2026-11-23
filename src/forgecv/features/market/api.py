"""market 切片对外入口：目录服务与页面注册。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.market.service import MarketService
from forgecv.features.market.view import MarketPage
from forgecv.features.market.viewmodel import MarketViewModel
from forgecv.features.skill.api import build_service as build_skills
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "market"
TITLE = "技能市场"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> MarketService:
    """构造市场服务，学习动作交给技能切片。"""
    return MarketService(build_skills(sessions))


def register(host: Host) -> None:
    """注册路由。"""
    service = build_service(host.sessions)
    host.ui.pages.register(
        ROUTE,
        TITLE,
        lambda: MarketPage(MarketViewModel(service)),
    )
