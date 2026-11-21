"""结构化日志：控制台输出，级别由配置决定。"""

from __future__ import annotations

import logging
from typing import cast

import structlog

_LEVELS = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING}


def configure_logging(level: str = "INFO") -> None:
    """配置标准库与 structlog，重复调用只调整级别。"""
    numeric = _LEVELS.get(level.upper(), logging.INFO)
    logging.basicConfig(level=numeric, format="%(message)s", force=True)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(numeric),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """按模块名取日志器。"""
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))
