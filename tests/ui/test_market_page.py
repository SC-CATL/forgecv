"""技能市场页：目录浏览、分类筛选与一键学习。"""

from __future__ import annotations

import pytest

from forgecv.features.market.api import build_service as build_market
from forgecv.features.market.catalog import MARKET_SKILLS
from forgecv.features.market.view import MarketPage
from forgecv.features.market.viewmodel import MarketViewModel
from forgecv.features.skill.api import build_service as build_skills
from forgecv.platform.adapters.db.session import SessionFactory

pytestmark = pytest.mark.ui


def _page(sessions: SessionFactory) -> MarketPage:
    return MarketPage(MarketViewModel(build_market(sessions)))


def test_market_lists_and_learns(
    qtbot, sessions: SessionFactory, candidate: int
) -> None:
    """选中目录项后学习，技能落库且按钮转为已加入。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    assert page._list.count() == len(MARKET_SKILLS)

    page._list.setCurrentRow(0)
    assert page._learn.isEnabled()
    page._learn.click()

    assert not page._learn.isEnabled()
    assert page._tag.text().startswith("市场认证")
    rows = build_skills(sessions).list_all()
    assert len(rows) == 1
    assert rows[0].market_tag == "市场认证"


def test_market_filter_only_shows_category(
    qtbot, sessions: SessionFactory, candidate: int
) -> None:
    """分类筛选只展示对应分类的技能。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    index = page._category.findData("语言")
    assert index > 0
    page._category.setCurrentIndex(index)
    expected = sum(1 for skill in MARKET_SKILLS if skill.category == "语言")
    assert page._list.count() == expected
    assert all(row.category == "语言" for row in page._vm.rows)
