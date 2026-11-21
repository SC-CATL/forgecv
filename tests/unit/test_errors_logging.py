"""错误结构与日志配置。"""

from __future__ import annotations

import logging

from forgecv.platform.core.errors import (
    AppError,
    ConflictError,
    DatabaseError,
    NotFoundError,
    ValidationError,
)
from forgecv.platform.observability.logging import configure_logging, get_logger


def test_error_to_dict_merges_context() -> None:
    """错误字典包含 code、message 与上下文。"""
    error = ValidationError("邮箱非法", field="email")
    payload = error.to_dict()
    assert payload["code"] == "app.validation"
    assert payload["message"] == "邮箱非法"
    assert payload["field"] == "email"


def test_error_subclasses_have_codes() -> None:
    """每类错误有稳定 code。"""
    assert AppError("x").code == "app.error"
    assert NotFoundError("x").code == "app.not_found"
    assert ConflictError("x").code == "app.conflict"
    assert DatabaseError("x").code == "app.database"


def test_logging_can_be_reconfigured() -> None:
    """重复配置不抛错，级别生效。"""
    configure_logging("DEBUG")
    get_logger("test").info("hello", key="value")
    assert logging.getLogger().level == logging.DEBUG
