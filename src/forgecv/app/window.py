"""主窗口装配：注册切片路由，选定首页。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from forgecv.features.dashboard.api import register as register_dashboard
from forgecv.features.education.api import register as register_education
from forgecv.features.experience.api import register as register_experience
from forgecv.features.export.api import register as register_export
from forgecv.features.profile.api import register as register_profile
from forgecv.features.project.api import register as register_project
from forgecv.features.resume.api import register as register_resume
from forgecv.features.settings.api import register as register_settings
from forgecv.features.skill.api import register as register_skill
from forgecv.features.snapshot.api import register as register_snapshot
from forgecv.features.tag.api import register as register_tag
from forgecv.features.timeline.api import register as register_timeline
from forgecv.platform.ui.kit.layout import ShellWindow

if TYPE_CHECKING:
    from forgecv.app.container import Container


def build_window(container: Container) -> ShellWindow:
    """创建外壳、注册路由并落到首页。"""
    shell = container.ui.create_shell(container.settings.app_title)
    register_dashboard(container)
    register_profile(container)
    register_education(container)
    register_timeline(container)
    register_experience(container)
    register_project(container)
    register_tag(container)
    register_skill(container)
    register_resume(container)
    register_export(container)
    register_snapshot(container)
    register_settings(container)
    routes = container.ui.pages.routes()
    if routes:
        container.ui.pages.navigate(routes[0])
    shell.statusBar().showMessage(f"环境：{container.settings.environment}")
    return shell
