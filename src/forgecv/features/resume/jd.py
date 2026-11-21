"""JD 覆盖分析：本地词表 + 已有技能/标签，不联网。"""

from __future__ import annotations

from dataclasses import dataclass

VOCAB = (
    "Python", "Java", "Go", "Rust", "C++", "C#", "TypeScript", "JavaScript",
    "SQL", "MySQL", "PostgreSQL", "Redis", "Kafka", "RabbitMQ", "MongoDB",
    "Linux", "Docker", "Kubernetes", "Git", "CI/CD", "Jenkins", "Nginx",
    "AWS", "GCP", "Azure", "分布式", "微服务", "高并发", "性能优化", "可观测性",
    "单元测试", "集成测试", "测试", "算法", "数据结构", "计算机网络", "操作系统",
    "数据库", "缓存", "消息队列", "嵌入式", "前端", "后端", "全栈",
    "机器学习", "深度学习", "PyTorch", "TensorFlow", "数据分析", "推荐系统",
    "FastAPI", "Django", "Flask", "Spring", "React", "Vue", "Qt", "PySide6",
)


@dataclass(frozen=True, slots=True)
class JDReport:
    """岗位覆盖结果。"""

    coverage: int
    matched: list[str]
    missing: list[str]
    message: str


def _unique(words: list[str]) -> list[str]:
    """按小写去重，保留原始写法。"""
    seen: set[str] = set()
    result: list[str] = []
    for word in words:
        key = word.lower()
        if key not in seen:
            seen.add(key)
            result.append(word)
    return result


def analyze(jd_text: str, known: list[str]) -> JDReport:
    """计算覆盖率与缺口。"""
    text = jd_text.strip()
    if not text:
        return JDReport(0, [], [], "粘贴 JD 后点击分析")
    lowered = text.lower()
    known_table = {word.lower(): word for word in known if word}
    vocab_hits = _unique([word for word in VOCAB if word.lower() in lowered])
    known_hits = _unique([word for word in known if word and word.lower() in lowered])
    if not vocab_hits:
        message = "JD 中没有识别到词表内的技术关键词"
        return JDReport(0, known_hits, [], message)
    matched = [word for word in vocab_hits if word.lower() in known_table]
    missing = [word for word in vocab_hits if word.lower() not in known_table]
    coverage = round(len(matched) / len(vocab_hits) * 100)
    return JDReport(
        coverage=coverage,
        matched=_unique([*matched, *known_hits]),
        missing=missing,
        message="",
    )
