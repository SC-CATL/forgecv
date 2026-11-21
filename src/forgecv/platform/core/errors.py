"""应用异常层次：统一携带 code、message、context。"""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    """所有可预期错误的基类。"""

    code: str = "app.error"

    def __init__(self, message: str, **context: Any) -> None:
        """记录错误信息与上下文。"""
        super().__init__(message)
        self.message = message
        self.context: dict[str, Any] = context

    def to_dict(self) -> dict[str, Any]:
        """转为可记录的结构。"""
        return {"code": self.code, "message": self.message, **self.context}


class ValidationError(AppError):
    """输入校验失败。"""

    code = "app.validation"


class NotFoundError(AppError):
    """目标不存在。"""

    code = "app.not_found"


class ConflictError(AppError):
    """并发冲突或唯一约束冲突。"""

    code = "app.conflict"


class DatabaseError(AppError):
    """数据库不可用或语句失败。"""

    code = "app.database"
