"""领域服务：项目校验与用例。"""

from __future__ import annotations

from forgecv.features.project.models import PROJECT_STATUSES, Project, ProjectMetric
from forgecv.features.project.repository import ProjectRepository
from forgecv.features.project.schemas import MetricInput, ProjectInput
from forgecv.platform.core.errors import NotFoundError, ValidationError
from forgecv.platform.core.result import Result
from forgecv.platform.core.validation import clean, url_error


class ProjectService:
    """项目库用例入口。"""

    def __init__(self, repository: ProjectRepository) -> None:
        """注入仓储。"""
        self._repository = repository

    def list_all(self) -> list[Project]:
        """全部项目。"""
        return self._repository.list_all()

    def add(self, data: ProjectInput) -> Result[Project, ValidationError]:
        """校验后新增项目。"""
        validated = self._validate(data)
        if isinstance(validated, ValidationError):
            return Result.err(validated)
        return Result.ok(self._repository.add(validated))

    def update(self, project_id: int, data: ProjectInput) -> Result[Project, ValidationError]:
        """校验后覆盖项目。"""
        validated = self._validate(data)
        if isinstance(validated, ValidationError):
            return Result.err(validated)
        row = self._repository.update(project_id, validated)
        if row is None:
            return Result.err(ValidationError(f"项目不存在：{project_id}"))
        return Result.ok(row)

    def delete(self, project_id: int) -> Result[bool, NotFoundError]:
        """删除项目。"""
        if self._repository.delete(project_id):
            return Result.ok(True)
        return Result.err(NotFoundError(f"项目不存在：{project_id}"))

    def metrics_for(self, project_id: int) -> list[ProjectMetric]:
        """项目指标。"""
        return self._repository.metrics_for(project_id)

    def _validate(self, data: ProjectInput) -> ProjectInput | ValidationError:
        """清洗并校验项目输入。"""
        name = clean(data.name)
        direction = clean(data.direction)
        if not name or not direction:
            message = "项目名称不能为空" if not name else "请选择项目方向"
            return ValidationError(message)
        if data.status not in PROJECT_STATUSES:
            return ValidationError(f"未知项目状态：{data.status}")
        for value in (data.repo_url, data.demo_url):
            link_error = url_error(value)
            if link_error is not None:
                return ValidationError(link_error)
        if data.start_date and data.end_date and data.end_date < data.start_date:
            return ValidationError("结束日期不能早于开始日期")
        metrics = self._validate_metrics(data.metrics)
        if isinstance(metrics, ValidationError):
            return metrics
        highlights = [item.strip() for item in data.highlights if item.strip()]
        return ProjectInput(
            name=name,
            direction=direction,
            role=clean(data.role),
            start_date=data.start_date,
            end_date=data.end_date,
            status=data.status,
            repo_url=clean(data.repo_url),
            demo_url=clean(data.demo_url),
            summary=data.summary.strip(),
            architecture=data.architecture.strip(),
            highlights=highlights,
            challenges=data.challenges.strip(),
            retrospective=data.retrospective.strip(),
            ci_status=clean(data.ci_status),
            sort_order=data.sort_order,
            metrics=metrics,
        )

    @staticmethod
    def _validate_metrics(metrics: list[MetricInput]) -> list[MetricInput] | ValidationError:
        """指标键与值都必填，空行直接报错而不是静默丢弃。"""
        cleaned: list[MetricInput] = []
        for metric in metrics:
            key = clean(metric.key)
            value = clean(metric.value)
            if not key or not value:
                return ValidationError("指标的名称和值都不能为空", field="metrics")
            cleaned.append(
                MetricInput(
                    key=key,
                    value=value,
                    unit=clean(metric.unit),
                    note=clean(metric.note),
                    sort_order=metric.sort_order,
                )
            )
        return cleaned
