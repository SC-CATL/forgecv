"""生成一个新的业务切片：七件套 + 一个服务测试。"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

INIT = '''"""{name} 切片。"""
'''

MODELS = '''"""ORM 模型：{name} 记录。"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from forgecv.platform.adapters.db.base import Base, TimestampMixin


class {cls}(Base, TimestampMixin):
    """{name} 的核心实体。"""

    __tablename__ = "{name}_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
'''

REPOSITORY = '''"""仓储：{name} 的持久化操作。"""

from __future__ import annotations

from sqlalchemy import func, select

from forgecv.features.{name}.models import {cls}
from forgecv.platform.adapters.db.session import SessionFactory, session_scope


class {cls}Repository:
    """{name}_records 表的读写。"""

    def __init__(self, sessions: SessionFactory) -> None:
        """注入会话工厂。"""
        self._sessions = sessions

    def count(self) -> int:
        """记录总数。"""
        with session_scope(self._sessions) as session:
            return int(session.scalar(select(func.count()).select_from({cls})) or 0)

    def add(self, title: str) -> None:
        """新增一条记录。"""
        with session_scope(self._sessions) as session:
            session.add({cls}(title=title))
'''

SERVICE = '''"""领域服务：{name} 的业务规则。"""

from __future__ import annotations

from forgecv.features.{name}.repository import {cls}Repository
from forgecv.platform.core.errors import ValidationError
from forgecv.platform.core.result import Result


class {cls}Service:
    """{name} 用例入口。"""

    def __init__(self, repository: {cls}Repository) -> None:
        """注入仓储。"""
        self._repository = repository

    def total(self) -> int:
        """当前记录数。"""
        return self._repository.count()

    def add(self, title: str) -> Result[str, ValidationError]:
        """校验后新增。"""
        cleaned = title.strip()
        if not cleaned:
            return Result.err(ValidationError("标题不能为空"))
        self._repository.add(cleaned)
        return Result.ok(cleaned)
'''

VIEWMODEL = '''"""视图模型：{name} 页面状态。"""

from __future__ import annotations

from forgecv.features.{name}.service import {cls}Service
from forgecv.platform.ui.qt import QtCore, Signal


class {cls}ViewModel(QtCore.QObject):
    """{name} 的展示状态。"""

    total_changed = Signal(int)

    def __init__(self, service: {cls}Service) -> None:
        """注入服务。"""
        super().__init__()
        self._service = service

    def refresh(self) -> None:
        """重新统计并广播。"""
        self.total_changed.emit(self._service.total())
'''

VIEW = '''"""{name} 页面：只拼控件与绑定信号。"""

from __future__ import annotations

from forgecv.features.{name}.viewmodel import {cls}ViewModel
from forgecv.platform.ui.qt import QtWidgets


class {cls}Page(QtWidgets.QWidget):
    """{name} 的默认页面。"""

    def __init__(self, view_model: {cls}ViewModel) -> None:
        """构建界面。"""
        super().__init__()
        self._vm = view_model
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(12)
        title = QtWidgets.QLabel("{name}", self)
        title.setObjectName("PageTitle")
        self._total = QtWidgets.QLabel("共 0 条", self)
        self._total.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(self._total)
        layout.addStretch(1)
        self._vm.total_changed.connect(lambda value: self._total.setText(f"共 {value} 条"))
        self._vm.refresh()
'''

API = '''"""切片对外唯一入口。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.{name}.repository import {cls}Repository
from forgecv.features.{name}.service import {cls}Service
from forgecv.features.{name}.view import {cls}Page
from forgecv.features.{name}.viewmodel import {cls}ViewModel
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "{name}"
TITLE = "{name}"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> {cls}Service:
    """构造切片服务。"""
    return {cls}Service({cls}Repository(sessions))


def register(host: Host) -> None:
    """注册路由。"""
    service = build_service(host.sessions)
    host.ui.pages.register(ROUTE, TITLE, lambda: {cls}Page({cls}ViewModel(service)))
'''

TEST = '''"""{name} 服务的最小回归。"""

from __future__ import annotations

from forgecv.features.{name}.api import build_service
from forgecv.platform.adapters.db.session import SessionFactory


def test_add_rejects_blank(sessions: SessionFactory) -> None:
    """空标题被拒绝。"""
    assert not build_service(sessions).add("   ").is_ok


def test_add_and_count(sessions: SessionFactory) -> None:
    """写入后计数递增。"""
    service = build_service(sessions)
    assert service.add("hello").is_ok
    assert service.total() == 1
'''

FILES = {
    "__init__.py": INIT,
    "models.py": MODELS,
    "repository.py": REPOSITORY,
    "service.py": SERVICE,
    "viewmodel.py": VIEWMODEL,
    "view.py": VIEW,
    "api.py": API,
}


def camel(name: str) -> str:
    """snake_case 转 PascalCase。"""
    return "".join(part.capitalize() for part in name.split("_"))


def package_name() -> str:
    """从 src 下唯一的包目录推断包名。"""
    candidates = [path for path in (ROOT / "src").iterdir() if (path / "__init__.py").is_file()]
    if len(candidates) != 1:
        raise SystemExit("无法确定包名，请检查 src/ 结构")
    return candidates[0].name


def render(template: str, name: str, cls: str) -> str:
    """渲染占位符。"""
    body = template.replace("{name}", name).replace("{cls}", cls)
    return body.replace("{package_name}", package_name())


def main(argv: list[str] | None = None) -> int:
    """创建切片目录与测试文件。"""
    parser = argparse.ArgumentParser(description="新增业务切片")
    parser.add_argument("name", help="切片名，snake_case")
    args = parser.parse_args(argv)
    if not NAME_PATTERN.match(args.name):
        raise SystemExit(f"切片名不合法：{args.name}")
    target = ROOT / "src" / package_name() / "features" / args.name
    if target.exists():
        raise SystemExit(f"切片已存在：{target}")
    target.mkdir(parents=True)
    cls = camel(args.name)
    for filename, template in FILES.items():
        (target / filename).write_text(render(template, args.name, cls), encoding="utf-8")
    test_dir = ROOT / "tests" / "unit"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / f"test_{args.name}_service.py"
    test_file.write_text(render(TEST, args.name, cls), encoding="utf-8")
    print(f"已生成切片：{target.relative_to(ROOT)}")
    print("下一步：在 app/window.py 中注册该切片路由。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
