"""Alembic 环境：URL 来自应用配置，SQLite 使用 batch 模式。"""

from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from forgecv.features.attachment import models as attachment_models  # noqa: E402, F401
from forgecv.features.education import models as education_models  # noqa: E402, F401
from forgecv.features.experience import models as experience_models  # noqa: E402, F401
from forgecv.features.profile import models as profile_models  # noqa: E402, F401
from forgecv.features.project import models as project_models  # noqa: E402, F401
from forgecv.features.resume import models as resume_models  # noqa: E402, F401
from forgecv.features.settings import models as settings_models  # noqa: E402, F401
from forgecv.features.skill import models as skill_models  # noqa: E402, F401
from forgecv.features.tag import models as tag_models  # noqa: E402, F401
from forgecv.platform.adapters.db.base import Base  # noqa: E402
from forgecv.platform.config import load_settings  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def database_url() -> str:
    """优先使用命令行注入的 URL，否则读应用配置。"""
    return config.get_main_option("sqlalchemy.url") or load_settings().database_url


def run_offline() -> None:
    """生成 SQL 脚本时使用。"""
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_online() -> None:
    """直连数据库执行迁移。"""
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = database_url()
    engine = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_offline()
else:
    run_online()
