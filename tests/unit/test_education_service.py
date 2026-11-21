"""education 服务：学历校验与排序。"""

from __future__ import annotations

from datetime import date

from forgecv.features.education.api import build_service
from forgecv.features.education.schemas import EducationInput
from forgecv.platform.adapters.db.session import SessionFactory


def _input(**overrides: object) -> EducationInput:
    """构造一条合法学历，按需覆盖字段。"""
    values: dict[str, object] = {
        "school": "浙江大学",
        "degree_level": "本科",
        "major": "软件工程",
        "start_date": date(2020, 9, 1),
        "end_date": date(2024, 6, 30),
    }
    values.update(overrides)
    return EducationInput(**values)  # type: ignore[arg-type]


def test_add_requires_school(sessions: SessionFactory, candidate: int) -> None:
    """院校必填。"""
    assert not build_service(sessions).add(_input(school="  ")).is_ok


def test_add_rejects_current_with_end_date(sessions: SessionFactory, candidate: int) -> None:
    """标记在读时不能有结束日期。"""
    result = build_service(sessions).add(_input(is_current=True))
    assert not result.is_ok


def test_add_and_list(sessions: SessionFactory, candidate: int) -> None:
    """新增后按顺序返回，并清理课程空白。"""
    service = build_service(sessions)
    result = service.add(_input(courses=[" 操作系统 ", ""]))
    assert result.is_ok
    rows = service.list_all()
    assert len(rows) == 1
    assert rows[0].courses == ["操作系统"]


def test_update_and_delete(sessions: SessionFactory, candidate: int) -> None:
    """覆盖与删除。"""
    service = build_service(sessions)
    row = service.add(_input()).unwrap()
    updated = service.update(row.id, _input(major="计算机科学"))
    assert updated.is_ok
    assert updated.unwrap().major == "计算机科学"
    assert service.delete(row.id).is_ok
    assert not service.delete(row.id).is_ok


def test_reorder_rewrites_sort_order(sessions: SessionFactory, candidate: int) -> None:
    """按 id 列表重写排序。"""
    service = build_service(sessions)
    first = service.add(_input()).unwrap()
    second = service.add(_input(school="复旦大学")).unwrap()
    service.reorder([second.id, first.id])
    rows = service.list_all()
    assert [row.id for row in rows] == [second.id, first.id]
