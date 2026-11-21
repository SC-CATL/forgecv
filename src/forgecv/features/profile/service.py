"""领域服务：候选人信息与证书的业务规则。"""

from __future__ import annotations

from forgecv.features.profile.models import Candidate, Certificate
from forgecv.features.profile.repository import ProfileRepository
from forgecv.features.profile.schemas import CandidateInput, CertificateInput
from forgecv.platform.core.errors import NotFoundError, ValidationError
from forgecv.platform.core.result import Result
from forgecv.platform.core.validation import clean, email_error, url_error


class ProfileService:
    """候选人档案用例入口。"""

    def __init__(self, repository: ProfileRepository) -> None:
        """注入仓储。"""
        self._repository = repository

    def load(self) -> Candidate | None:
        """读取候选人，未建档返回 None。"""
        return self._repository.get_candidate()

    def save(self, data: CandidateInput) -> Result[Candidate, ValidationError]:
        """校验并保存候选人信息。"""
        name = clean(data.full_name)
        if not name:
            return Result.err(ValidationError("姓名不能为空", field="full_name"))
        message = email_error(data.email)
        if message is not None:
            return Result.err(ValidationError(message))
        for value in (data.github_url, data.blog_url, data.website_url):
            link_error = url_error(value)
            if link_error is not None:
                return Result.err(ValidationError(link_error))
        cleaned = CandidateInput(
            full_name=name,
            headline=clean(data.headline),
            email=clean(data.email),
            phone=clean(data.phone),
            city=clean(data.city),
            github_url=clean(data.github_url),
            blog_url=clean(data.blog_url),
            website_url=clean(data.website_url),
            summary=data.summary.strip(),
        )
        return Result.ok(self._repository.save_candidate(cleaned))

    def certificates(self) -> list[Certificate]:
        """全部证书。"""
        return self._repository.list_certificates()

    def add_certificate(self, data: CertificateInput) -> Result[Certificate, ValidationError]:
        """校验后新增证书。"""
        name = clean(data.name)
        if not name:
            return Result.err(ValidationError("证书名称不能为空", field="name"))
        if data.issued_on and data.expires_on and data.expires_on < data.issued_on:
            return Result.err(ValidationError("到期日期不能早于颁发日期"))
        issue_url = clean(data.url)
        link_error = url_error(issue_url)
        if link_error is not None:
            return Result.err(ValidationError(link_error))
        cleaned = CertificateInput(
            name=name,
            issuer=clean(data.issuer),
            issued_on=data.issued_on,
            expires_on=data.expires_on,
            credential_id=clean(data.credential_id),
            url=issue_url,
            notes=data.notes.strip(),
            sort_order=data.sort_order,
        )
        return Result.ok(self._repository.add_certificate(cleaned))

    def delete_certificate(self, certificate_id: int) -> Result[bool, NotFoundError]:
        """删除证书，不存在时报错。"""
        if self._repository.delete_certificate(certificate_id):
            return Result.ok(True)
        return Result.err(NotFoundError(f"证书不存在：{certificate_id}"))
