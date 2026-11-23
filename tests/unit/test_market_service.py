"""market 服务：目录筛选与学习写入技能矩阵。"""

from __future__ import annotations

from forgecv.features.market.api import build_service
from forgecv.features.market.catalog import MARKET_SKILLS
from forgecv.features.profile.api import build_service as build_profile
from forgecv.features.skill.api import build_service as build_skills
from forgecv.features.skill.schemas import SkillInput
from forgecv.platform.adapters.db.session import SessionFactory


def test_catalog_categories_match_skill_matrix(
    sessions: SessionFactory, candidate: int
) -> None:
    """市场分类必须落在技能矩阵支持的分类内。"""
    market = build_service(sessions)
    skills = build_skills(sessions)
    assert market.categories()
    assert set(market.categories()) <= set(skills.categories())
    assert len(market.entries()) == len(MARKET_SKILLS)
    assert all(not entry.learned for entry in market.entries())


def test_learn_adds_market_skill_with_tag(
    sessions: SessionFactory, candidate: int
) -> None:
    """学习后技能落库，并带市场标识与认证标签。"""
    market = build_service(sessions)
    result = market.learn("python")
    assert result.is_ok
    assert result.unwrap() == "Python"
    rows = build_skills(sessions).list_all()
    assert len(rows) == 1
    assert rows[0].market_key == "python"
    assert rows[0].market_tag == "市场认证"
    learned = next(entry for entry in market.entries() if entry.key == "python")
    assert learned.learned


def test_learn_is_idempotent(sessions: SessionFactory, candidate: int) -> None:
    """重复学习同一市场技能不会复制记录。"""
    market = build_service(sessions)
    assert market.learn("sql").is_ok
    assert market.learn("sql").is_ok
    assert len(build_skills(sessions).list_all()) == 1


def test_learn_marks_existing_skill(
    sessions: SessionFactory, candidate: int
) -> None:
    """已有同名技能时保留原熟练度，只补市场标签。"""
    skills = build_skills(sessions)
    skills.add(SkillInput(name="Python", category="语言", level=4))
    assert build_service(sessions).learn("python").is_ok
    rows = skills.list_all()
    assert len(rows) == 1
    assert rows[0].level == 4
    assert rows[0].market_key == "python"
    assert rows[0].market_tag == "市场认证"


def test_learn_does_not_duplicate_name_across_categories(
    sessions: SessionFactory, candidate: int
) -> None:
    """同名技能在其他分类时也直接打标，不新增第二条。"""
    skills = build_skills(sessions)
    skills.add(SkillInput(name="Python", category="工具链", level=3))
    assert build_service(sessions).learn("python").is_ok
    rows = skills.list_all()
    assert len(rows) == 1
    assert rows[0].category == "工具链"
    assert rows[0].level == 3
    assert rows[0].market_key == "python"


def test_learn_works_on_fresh_database(sessions: SessionFactory) -> None:
    """空库先补候选人占位行后即可学习。"""
    build_profile(sessions).ensure()
    assert build_service(sessions).learn("python").is_ok
    assert len(build_skills(sessions).list_all()) == 1


def test_entries_can_be_filtered(sessions: SessionFactory, candidate: int) -> None:
    """按分类筛选只返回该分类条目。"""
    entries = build_service(sessions).entries("语言")
    assert entries
    assert all(entry.category == "语言" for entry in entries)


def test_unknown_market_key_is_rejected(
    sessions: SessionFactory, candidate: int
) -> None:
    """未知市场技能返回可读错误。"""
    result = build_service(sessions).learn("not-exist")
    assert not result.is_ok
    assert not build_skills(sessions).list_all()
