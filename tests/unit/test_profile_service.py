"""profile 服务：候选人保存与证书。"""

from __future__ import annotations

from datetime import date

from forgecv.features.profile.api import build_service
from forgecv.features.profile.schemas import CandidateInput, CertificateInput
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.core.validation import clean


def test_save_rejects_blank_name(sessions: SessionFactory) -> None:
    """姓名必填。"""
    assert not build_service(sessions).save(CandidateInput(full_name="  ")).is_ok


def test_save_rejects_bad_email(sessions: SessionFactory) -> None:
    """邮箱形态错误被拦截。"""
    result = build_service(sessions).save(CandidateInput(full_name="张三", email="bad"))
    assert not result.is_ok


def test_ensure_candidate_is_idempotent(sessions: SessionFactory) -> None:
    """空库也能建出固定 id 的候选人占位行。"""
    service = build_service(sessions)
    assert service.load() is None
    first = service.ensure()
    second = service.ensure()
    assert first.id == second.id == 1
    assert service.load() is not None


def test_save_and_load_roundtrip(sessions: SessionFactory) -> None:
    """保存后能读回并清理空白。"""
    service = build_service(sessions)
    result = service.save(CandidateInput(full_name=" 张三 ", city=" 杭州 "))
    assert result.is_ok
    loaded = service.load()
    assert loaded is not None
    assert loaded.full_name == "张三"
    assert loaded.city == "杭州"


def test_certificate_roundtrip(sessions: SessionFactory, candidate: int) -> None:
    """证书新增与删除。"""
    service = build_service(sessions)
    result = service.add_certificate(
        CertificateInput(name="CET-6", issuer="教育部", issued_on=date(2021, 6, 1))
    )
    assert result.is_ok
    certificate = result.unwrap()
    assert service.certificates()[0].name == "CET-6"
    assert service.delete_certificate(certificate.id).is_ok


def test_certificate_rejects_reversed_dates(sessions: SessionFactory, candidate: int) -> None:
    """到期早于颁发被拒绝。"""
    service = build_service(sessions)
    result = service.add_certificate(
        CertificateInput(
            name="证书", issued_on=date(2022, 1, 1), expires_on=date(2021, 1, 1)
        )
    )
    assert not result.is_ok


def test_clean_trims_whitespace() -> None:
    """公共清洗函数去首尾空白。"""
    assert clean("  a  ") == "a"
