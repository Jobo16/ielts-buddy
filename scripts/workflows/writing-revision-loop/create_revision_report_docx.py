#!/usr/bin/env python3
"""Create an IELTS Writing revision report DOCX from a JSON revision plan."""

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
FONT = "Times New Roman"


def xml_escape(text: str) -> str:
    return html.escape(str(text), quote=False)


def normalize_spaces(text: Any) -> str:
    return " ".join(str(text).split())


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+", text))


def run_xml(text: str, *, bold: bool = False, italic: bool = False, color: str | None = None, size: int | None = None) -> str:
    if text == "":
        return ""
    props = [f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>']
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    if size:
        props.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    space = ' xml:space="preserve"' if text[:1].isspace() or text[-1:].isspace() else ""
    return f"<w:r><w:rPr>{''.join(props)}</w:rPr><w:t{space}>{xml_escape(text)}</w:t></w:r>"


def paragraph_xml(runs: list[str], *, style: str | None = None, keep_next: bool = False) -> str:
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if keep_next:
        ppr.append("<w:keepNext/>")
    ppr.append('<w:spacing w:after="120"/>')
    return f"<w:p><w:pPr>{''.join(ppr)}</w:pPr>{''.join(runs)}</w:p>"


def text_paragraph(text: str, *, bold: bool = False, italic: bool = False, color: str | None = None) -> str:
    return paragraph_xml([run_xml(text, bold=bold, italic=italic, color=color)])


def heading(text: str, level: int = 1) -> str:
    return paragraph_xml([run_xml(text, bold=True, size=32 if level == 1 else 26)], style=f"Heading{level}", keep_next=True)


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def cell_xml(text: str, *, width: int, bold: bool = False, fill: str | None = None) -> str:
    shading = f'<w:shd w:fill="{fill}"/>' if fill else ""
    tcpr = f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shading}</w:tcPr>'
    return f"<w:tc>{tcpr}{paragraph_xml([run_xml(text, bold=bold)])}</w:tc>"


def table_xml(headers: list[str], rows: list[list[str]], widths: list[int]) -> str:
    border = '<w:top w:val="single" w:sz="4" w:color="CCCCCC"/><w:left w:val="single" w:sz="4" w:color="CCCCCC"/><w:bottom w:val="single" w:sz="4" w:color="CCCCCC"/><w:right w:val="single" w:sz="4" w:color="CCCCCC"/><w:insideH w:val="single" w:sz="4" w:color="CCCCCC"/><w:insideV w:val="single" w:sz="4" w:color="CCCCCC"/>'
    table = [
        '<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/><w:tblBorders>',
        border,
        '</w:tblBorders></w:tblPr><w:tblGrid>',
        "".join(f'<w:gridCol w:w="{width}"/>' for width in widths),
        "</w:tblGrid>",
    ]
    table.append("<w:tr>")
    for header, width in zip(headers, widths):
        table.append(cell_xml(header, width=width, bold=True, fill="EAF2F8"))
    table.append("</w:tr>")
    for row in rows:
        table.append("<w:tr>")
        for value, width in zip(row, widths):
            table.append(cell_xml(value, width=width))
        table.append("</w:tr>")
    table.append("</w:tbl>")
    return "".join(table)


def status_label(status: str) -> str:
    labels = {
        "fixed": "Fixed",
        "improved": "Improved",
        "unchanged": "Unchanged",
        "worsened": "Worsened",
        "not_applicable": "No longer relevant",
        "not-applicable": "No longer relevant",
    }
    return labels.get(status.strip().lower(), status.strip() or "Unspecified")


def list_of_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [normalize_spaces(item) for item in value if normalize_spaces(item)]


def score_rows(scores: Any) -> list[list[str]]:
    if not isinstance(scores, dict):
        return []
    rows: list[list[str]] = []
    for criterion, raw in scores.items():
        if isinstance(raw, dict):
            rows.append([
                str(criterion),
                normalize_spaces(raw.get("before", "")),
                normalize_spaces(raw.get("after", "")),
                normalize_spaces(raw.get("note", "")),
            ])
        else:
            rows.append([str(criterion), "", normalize_spaces(raw), ""])
    return rows


def fix_rows(plan: dict[str, Any]) -> list[list[str]]:
    rows: list[list[str]] = []
    for item in list_of_dicts(plan.get("fix_checks", [])):
        rows.append([
            status_label(str(item.get("status", ""))),
            normalize_spaces(item.get("issue", "")),
            normalize_spaces(item.get("evidence") or item.get("before", "")),
            normalize_spaces(item.get("comment") or item.get("after", "")),
        ])
    return rows


def new_issue_rows(plan: dict[str, Any]) -> list[list[str]]:
    rows: list[list[str]] = []
    for item in list_of_dicts(plan.get("new_issues", [])):
        rows.append([
            normalize_spaces(item.get("issue", "")),
            normalize_spaces(item.get("evidence", "")),
            normalize_spaces(item.get("fix") or item.get("comment", "")),
        ])
    return rows


def document_xml(plan: dict[str, Any]) -> str:
    body: list[str] = []
    task_type = normalize_spaces(plan.get("task_type", "雅思写作"))
    prompt = normalize_spaces(plan.get("prompt", ""))
    original_band = normalize_spaces(plan.get("original_band", ""))
    revised_band = normalize_spaces(plan.get("revised_band", ""))

    body.append(heading("雅思写作二改报告", 1))
    body.append(text_paragraph(f"任务：{task_type}"))
    if prompt:
        body.append(text_paragraph(f"题目：{prompt}"))
    if original_band or revised_band:
        body.append(text_paragraph(f"分数变化参考：{original_band or 'N/A'} → {revised_band or 'N/A'}", bold=True))
    judgement = normalize_spaces(plan.get("overall_judgement", ""))
    if judgement:
        body.append(text_paragraph(judgement))

    body.append(heading("修改检查", 2))
    rows = fix_rows(plan)
    if not rows:
        rows = [["未指定", "没有提供原问题", "", "交付前补充修改检查项。"]]
    body.append(table_xml(["状态", "原问题", "证据", "教师备注"], rows, [1500, 2600, 2600, 2660]))

    score_movement = score_rows(plan.get("criterion_scores", {}))
    if score_movement:
        body.append(heading("分数变化参考", 2))
        body.append(table_xml(["维度", "修改前", "修改后", "原因"], score_movement, [2400, 1200, 1200, 4560]))

    issues = new_issue_rows(plan)
    if issues:
        body.append(heading("新问题", 2))
        body.append(table_xml(["问题", "证据", "修改建议"], issues, [2400, 3360, 3600]))

    body.append(page_break())
    body.append(heading("修改后答案", 2))
    revised = list_of_strings(plan.get("revised_essay", []))
    if revised:
        for paragraph in revised:
            body.append(text_paragraph(paragraph))
        body.append(text_paragraph(f"({word_count(' '.join(revised))} words)", italic=True))
    else:
        body.append(text_paragraph("未提供修改后答案。"))

    body.append(page_break())
    body.append(heading("下一轮改写目标", 2))
    target = normalize_spaces(plan.get("next_rewrite_target", ""))
    body.append(text_paragraph(target or "根据上方未解决的修改项，重写一个段落。", bold=True))

    drills = list_of_strings(plan.get("micro_drills", []))
    if drills:
        body.append(heading("微训练", 2))
        for idx, drill in enumerate(drills, start=1):
            body.append(text_paragraph(f"{idx}. {drill}"))

    body.append("<w:sectPr><w:pgSz w:w=\"12240\" w:h=\"15840\"/><w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\"/></w:sectPr>")
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}" xmlns:r="{R_NS}"><w:body>{"".join(body)}</w:body></w:document>'
    )


def content_types_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""


def rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def document_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""


def styles_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W_NS}">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:rPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="Heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:b/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="Heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:b/><w:sz w:val="26"/><w:szCs w:val="26"/></w:rPr></w:style>
</w:styles>"""


def app_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
</Properties>"""


def core_xml() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>雅思写作二改报告</dc:title>
  <dc:creator>writing-revision-loop</dc:creator>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def default_output_path(plan_path: Path, source_docx: Path | None) -> Path:
    if source_docx is not None:
        stem = source_docx.stem.replace("(reviewed)", "")
        return source_docx.with_name(f"{stem}(revision-report).docx")
    desktop = Path.home() / "Desktop"
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    if desktop.is_dir():
        return desktop / f"IELTS_Writing_Revision_Report_{stamp}.docx"
    return plan_path.with_suffix(".docx")


def create_docx(plan: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml())
        zf.writestr("_rels/.rels", rels_xml())
        zf.writestr("word/_rels/document.xml.rels", document_rels_xml())
        zf.writestr("word/document.xml", document_xml(plan))
        zf.writestr("word/styles.xml", styles_xml())
        zf.writestr("docProps/core.xml", core_xml())
        zf.writestr("docProps/app.xml", app_xml())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--source-docx", type=Path, default=None, help="Reviewed DOCX used only to choose the default output path.")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--cleanup-plan", action="store_true")
    args = parser.parse_args()

    plan = json.loads(args.plan_json.read_text(encoding="utf-8"))
    output = args.output or default_output_path(args.plan_json, args.source_docx)
    create_docx(plan, output)
    if args.cleanup_plan:
        args.plan_json.unlink(missing_ok=True)
    print(output)


if __name__ == "__main__":
    main()
