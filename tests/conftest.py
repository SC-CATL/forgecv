"""测试夹具：离屏 Qt、内存库、临时文件库。"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("ENVIRONMENT", "test")

from forgecv.features.attachment import models as attachment_models  # noqa: F401
from forgecv.features.education import models as education_models  # noqa: F401
from forgecv.features.experience import models as experience_models  # noqa: F401
from forgecv.features.profile import models as profile_models  # noqa: F401
from forgecv.features.project import models as project_models  # noqa: F401
from forgecv.features.resume import models as resume_models  # noqa: F401
from forgecv.features.settings import models as settings_models  # noqa: F401
from forgecv.features.skill import models as skill_models  # noqa: F401
from forgecv.features.tag import models as tag_models  # noqa: F401
from forgecv.platform.adapters.db.base import Base
from forgecv.platform.adapters.db.session import (
    SessionFactory,
    create_session_factory,
)
from forgecv.platform.config import Settings


@pytest.fixture()
def engine() -> Iterator[Engine]:
    """每个测试一个独立内存库。"""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def sessions(engine: Engine) -> SessionFactory:
    """绑定内存库的会话工厂。"""
    return create_session_factory(engine)


@pytest.fixture()
def candidate(sessions: SessionFactory) -> int:
    """建一条候选人记录，满足其他切片的外键。"""
    from forgecv.features.profile.api import build_service
    from forgecv.features.profile.schemas import CandidateInput

    result = build_service(sessions).save(CandidateInput(full_name="测试候选人"))
    assert result.is_ok
    return result.unwrap().id


@pytest.fixture()
def settings(tmp_path: Path) -> Settings:
    """指向临时文件库的配置，供迁移测试使用。"""
    database = tmp_path / "app.db"
    return Settings(database_url=f"sqlite+pysqlite:///{database.as_posix()}")
