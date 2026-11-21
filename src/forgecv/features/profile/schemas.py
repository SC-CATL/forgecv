"""输入模型：界面与服务的边界，不依赖 Qt 与数据库。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True, kw_only=True)
class CandidateInput:
    """候选人可编辑字段。"""

    full_name: str
    headline: str = ""
    email: str = ""
    phone: str = ""
    city: str = ""
    github_url: str = ""
    blog_url: str = ""
    website_url: str = ""
    summary: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class CertificateInput:
    """证书输入。"""

    name: str
    issuer: str = ""
    issued_on: date | None = None
    expires_on: date | None = None
    credential_id: str = ""
    url: str = ""
    notes: str = ""
    sort_order: int = 0
