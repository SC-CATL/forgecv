"""Word 导出：按 docs/engineering/export-spec.md 的版式生成 docx。"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from forgecv.features.resume.document import ResumeDocument

FONT_TITLE = "微软雅黑"
FONT_BODY = "宋体"
MUTED = "5c6a7a"
ACCENT = "2f6fed"
PAGE_WIDTH = Cm(17.4)


def _set_font(
    run: Run,
    *,
    name: str,
    size: float,
    bold: bool = False,
    color: str | None = None,
) -> None:
    """设置字体并显式写入 eastAsia，避免 Word 中文回退。"""
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), name)
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)


def _paragraph(doc: DocxDocument, *, space_after: float = 3) -> Paragraph:
    """统一段后距与行距。"""
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(space_after)
    paragraph.paragraph_format.line_spacing = 1.15
    return paragraph


def _add_run(
    paragraph: Paragraph,
    text: str,
    *,
    size: float,
    name: str = FONT_BODY,
    bold: bool = False,
    color: str | None = None,
) -> None:
    """向段落追加一个带样式的 run。"""
    run = paragraph.add_run(text)
    _set_font(run, name=name, size=size, bold=bold, color=color)


def _heading(doc: DocxDocument, text: str) -> None:
    """分区标题 + 下划线。"""
    paragraph = _paragraph(doc)
    _add_run(paragraph, text, size=12, bold=True, name=FONT_TITLE)
    ppr = paragraph._p.get_or_add_pPr()
    border = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "888888")
    border.append(bottom)
    ppr.append(border)


def _entry(doc: DocxDocument, left: str, right: str) -> None:
    """左侧主标题 + 右对齐时间。"""
    paragraph = _paragraph(doc)
    paragraph.paragraph_format.tab_stops.add_tab_stop(PAGE_WIDTH, WD_TAB_ALIGNMENT.RIGHT)
    _add_run(paragraph, left, size=10.5, bold=True, name=FONT_TITLE)
    _add_run(paragraph, f"\t{right}", size=9, color=MUTED)


def _bullet(doc: DocxDocument, text: str) -> None:
    """条目要点。"""
    paragraph = _paragraph(doc)
    paragraph.paragraph_format.left_indent = Cm(0.4)
    _add_run(paragraph, f"· {text}", size=10.5)


def _muted_line(doc: DocxDocument, text: str, *, color: str | None = None) -> None:
    """次要行：标签 / 指标 / 联系方式。"""
    paragraph = _paragraph(doc)
    _add_run(paragraph, text, size=9, color=color)


def _write_header(doc: DocxDocument, document: ResumeDocument) -> None:
    """姓名、意向与联系方式。"""
    paragraph = _paragraph(doc)
    _add_run(paragraph, document.full_name or "未填写姓名", size=18, bold=True, name=FONT_TITLE)
    if document.headline:
        _add_run(paragraph, f"  {document.headline}", size=10.5, color=MUTED)
    contact = [part for part in (document.city, document.email, document.phone) if part]
    if contact:
        _muted_line(doc, " | ".join(contact))
    if document.links:
        _muted_line(doc, " | ".join(document.links))


def _write_education(doc: DocxDocument, document: ResumeDocument) -> None:
    """教育经历。"""
    if not document.educations:
        return
    _heading(doc, "教育经历")
    for row in document.educations:
        _entry(doc, f"{row.school} · {row.degree} · {row.major}", row.period)
        if row.gpa or row.courses:
            extras = []
            if row.gpa:
                extras.append(f"GPA {row.gpa}")
            if row.courses:
                extras.append(f"主修：{'、'.join(row.courses)}")
            _muted_line(doc, " · ".join(extras))
        if row.thesis:
            _muted_line(doc, f"论文：{row.thesis}")


def _write_experience(doc: DocxDocument, document: ResumeDocument) -> None:
    """工作经历。"""
    if not document.experiences:
        return
    _heading(doc, "工作经历")
    for row in document.experiences:
        _entry(doc, f"{row.company} · {row.role}", row.period)
        for item in row.highlights:
            _bullet(doc, item)


def _write_projects(doc: DocxDocument, document: ResumeDocument) -> None:
    """项目经历。"""
    if not document.projects:
        return
    _heading(doc, "项目经历")
    for row in document.projects:
        title = f"{row.name} · {row.role}" if row.role else row.name
        _entry(doc, f"{title} · {row.direction}", row.period)
        if row.tags:
            _muted_line(doc, " · ".join(row.tags), color=ACCENT)
        for item in row.highlights:
            _bullet(doc, item)
        if row.metrics:
            _muted_line(doc, "指标：" + " · ".join(row.metrics))


def _write_skills(doc: DocxDocument, document: ResumeDocument) -> None:
    """技术能力。"""
    if not document.skill_groups:
        return
    _heading(doc, "技术能力")
    for category, skills in document.skill_groups.items():
        paragraph = _paragraph(doc)
        _add_run(paragraph, f"{category}：", size=10.5, bold=True, name=FONT_TITLE)
        parts = []
        for skill in skills:
            years = f"，{skill.years:g} 年" if skill.years else ""
            parts.append(f"{skill.name}（{skill.level}{years}）")
        _add_run(paragraph, " · ".join(parts), size=10.5)


def _write_certificates(doc: DocxDocument, document: ResumeDocument) -> None:
    """证书与荣誉。"""
    if not document.certificates:
        return
    _heading(doc, "证书与荣誉")
    for row in document.certificates:
        issued = f" · {row.issued_on.isoformat()}" if row.issued_on else ""
        _muted_line(doc, f"{row.name} · {row.issuer}{issued}")


def _add_field(paragraph: Paragraph, instruction: str) -> None:
    """插入 PAGE / NUMPAGES 域。"""
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    code = OxmlElement("w:instrText")
    code.set(qn("xml:space"), "preserve")
    code.text = f" {instruction} "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(code)
    run._r.append(end)


def _write_footer(doc: DocxDocument, document: ResumeDocument) -> None:
    """页脚：姓名 · 第 X 页 / 共 Y 页。"""
    footer = doc.sections[0].footer
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _add_run(paragraph, f"{document.full_name} · 第 ", size=8, color=MUTED)
    _add_field(paragraph, "PAGE")
    _add_run(paragraph, " 页 / 共 ", size=8, color=MUTED)
    _add_field(paragraph, "NUMPAGES")
    _add_run(paragraph, " 页", size=8, color=MUTED)


def write_docx(document: ResumeDocument, target: Path) -> Path:
    """写出 docx，返回落盘路径。"""
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(1.8)
    section.right_margin = Cm(1.8)
    _write_header(doc, document)
    _write_education(doc, document)
    _write_experience(doc, document)
    _write_projects(doc, document)
    _write_skills(doc, document)
    _write_certificates(doc, document)
    _write_footer(doc, document)
    target.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(target))
    return target
