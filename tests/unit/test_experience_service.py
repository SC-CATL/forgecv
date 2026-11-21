"""experience 服务：经历校验与量化条目。"""

from __future__ import annotations

from datetime import date

from forgecv.features.experience.api import build_service
from forgecv.features.experience.schemas import ExperienceInput
from forgecv.platform.adapters.db.session import SessionFactory


def test_add_requires_company_and_role(sessions: SessionFactory, candidate: int) -> None:
    """公司与职位都必填。"""
    service = build_service(sessions)
    assert not service.add(ExperienceInput(company="", role="")).is_ok
    assert not service.add(ExperienceInput(company="某公司", role=" ")).is_ok


def test_add_cleans_highlights(sessions: SessionFactory, candidate: int) -> None:
    """亮点条目去空白并丢弃空串。"""
    result = build_service(sessions).add(
        ExperienceInput(
            company="某公司",
            role="后端",
            start_date=date(2023, 1, 1),
            is_current=True,
            highlights=[" 提升 30% ", ""],
        )
    )
    assert result.is_ok
    assert result.unwrap().highlights == ["提升 30%"]


def test_end_before_start_rejected(sessions: SessionFactory, candidate: int) -> None:
    """结束早于开始被拒绝。"""
    result = build_service(sessions).add(
        ExperienceInput(
            company="某公司",
            role="后端",
            start_date=date(2023, 1, 1),
            end_date=date(2022, 1, 1),
        )
    )
    assert not result.is_ok


def test_update_missing_returns_error(sessions: SessionFactory, candidate: int) -> None:
    """更新不存在的经历返回校验错误。"""
    result = build_service(sessions).update(
        999, ExperienceInput(company="某公司", role="后端", start_date=date(2023, 1, 1))
    )
    assert not result.is_ok
