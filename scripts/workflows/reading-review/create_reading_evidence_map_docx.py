#!/usr/bin/env python3
"""Create an IELTS Reading evidence-map DOCX from a JSON review plan."""

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


def xml_escape(text: Any) -> str:
    return html.escape(str(text), quote=False)


def normalize_spaces(text: Any) -> str:
    return " ".join(str(text).split())


def short_text(text: Any, limit: int = 180) -> str:
    text = normalize_spaces(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+", text))


def run_xml(
    text: Any,
    *,
    bold: bool = False,
    italic: bool = False,
    color: str | None = None,
    size: int | None = None,
) -> str:
    text = str(text)
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


def text_paragraph(text: Any, *, bold: bool = False, italic: bool = False, color: str | None = None) -> str:
    return paragraph_xml([run_xml(text, bold=bold, italic=italic, color=color)])


def heading(text: str, level: int = 1) -> str:
    return paragraph_xml(
        [run_xml(text, bold=True, size=32 if level == 1 else 26)],
        style=f"Heading{level}",
        keep_next=True,
    )


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def cell_xml(text: Any, *, width: int, bold: bool = False, fill: str | None = None) -> str:
    shading = f'<w:shd w:fill="{fill}"/>' if fill else ""
    tcpr = f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shading}</w:tcPr>'
    return f"<w:tc>{tcpr}{paragraph_xml([run_xml(short_text(text), bold=bold)])}</w:tc>"


def table_xml(headers: list[str], rows: list[list[Any]], widths: list[int]) -> str:
    border = (
        '<w:top w:val="single" w:sz="4" w:color="CCCCCC"/>'
        '<w:left w:val="single" w:sz="4" w:color="CCCCCC"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="CCCCCC"/>'
        '<w:right w:val="single" w:sz="4" w:color="CCCCCC"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="CCCCCC"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="CCCCCC"/>'
    )
    parts = [
        '<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/><w:tblBorders>',
        border,
        '</w:tblBorders></w:tblPr><w:tblGrid>',
        "".join(f'<w:gridCol w:w="{width}"/>' for width in widths),
        "</w:tblGrid><w:tr>",
    ]
    for header, width in zip(headers, widths):
        parts.append(cell_xml(header, width=width, bold=True, fill="EAF2F8"))
    parts.append("</w:tr>")
    for row in rows:
        parts.append("<w:tr>")
        for value, width in zip(row, widths):
            parts.append(cell_xml(value, width=width))
        parts.append("</w:tr>")
    parts.append("</w:tbl>")
    return "".join(parts)


def list_of_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [normalize_spaces(item) for item in value if normalize_spaces(item)]


def item_rows(plan: dict[str, Any]) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for item in list_of_dicts(plan.get("items", [])):
        rows.append(
            [
                item.get("question_number", item.get("q", "")),
                item.get("question_type", ""),
                item.get("user_answer", ""),
                item.get("correct_answer", ""),
                item.get("error_type", ""),
                item.get("evidence", ""),
            ]
        )
    return rows


def detail_block(item: dict[str, Any]) -> list[str]:
    q = normalize_spaces(item.get("question_number", item.get("q", "")))
    question = normalize_spaces(item.get("question", ""))
    title = f"Q{q}: {question}" if q else question or "阅读题目"
    parts = [heading(title, 2)]
    if item.get("evidence"):
        parts.append(text_paragraph("证据", bold=True))
        parts.append(text_paragraph(item["evidence"]))
    if item.get("paraphrase_bridge"):
        parts.append(text_paragraph("同义替换桥", bold=True))
        parts.append(text_paragraph(item["paraphrase_bridge"]))
    if item.get("trap"):
        parts.append(text_paragraph("陷阱/干扰项", bold=True))
        parts.append(text_paragraph(item["trap"]))
    if item.get("why_correct"):
        parts.append(text_paragraph("正确答案为什么成立", bold=True))
        parts.append(text_paragraph(item["why_correct"]))
    if item.get("micro_drill"):
        parts.append(text_paragraph("微训练", bold=True))
        parts.append(text_paragraph(item["micro_drill"]))
    return parts


def document_xml(plan: dict[str, Any]) -> str:
    body: list[str] = []
    source_title = normalize_spaces(plan.get("source_title", "雅思阅读"))
    passage_title = normalize_spaces(plan.get("passage_title", ""))
    summary = normalize_spaces(plan.get("summary", ""))
    items = list_of_dicts(plan.get("items", []))

    body.append(heading("雅思阅读证据图", 1))
    body.append(text_paragraph(f"来源：{source_title}"))
    if passage_title:
        body.append(text_paragraph(f"文章：{passage_title}"))
    if summary:
        body.append(text_paragraph(summary))
    body.append(text_paragraph(f"复盘题目数：{len(items)}", bold=True))

    rows = item_rows(plan)
    if not rows:
        rows = [["", "", "", "", "", "没有提供复盘题目。"]]
    body.append(heading("答案证据图", 2))
    body.append(
        table_xml(
            ["题号", "题型", "你的答案", "正确答案", "错误类型", "证据"],
            rows,
            [600, 1500, 1300, 1300, 1700, 2960],
        )
    )

    body.append(page_break())
    body.append(heading("逐题分析", 1))
    for item in items:
        body.extend(detail_block(item))

    drills = list_of_strings(plan.get("review_prompts", []))
    if drills:
        body.append(page_break())
        body.append(heading("复习提示", 1))
        for idx, drill in enumerate(drills, start=1):
            body.append(text_paragraph(f"{idx}. {drill}"))

    vocabulary = list_of_dicts(plan.get("vocabulary", []))
    if vocabulary:
        body.append(heading("实用词汇", 2))
        vocab_rows = [
            [item.get("phrase", ""), item.get("meaning", ""), item.get("source_sentence", "")]
            for item in vocabulary
        ]
        body.append(table_xml(["词组", "含义", "来源句"], vocab_rows, [2200, 2800, 4360]))

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
  <dc:title>雅思阅读证据图</dc:title>
  <dc:creator>reading-review</dc:creator>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def default_output_path(plan_path: Path, source_docx: Path | None) -> Path:
    if source_docx is not None:
        return source_docx.with_name(f"{source_docx.stem}(evidence-map).docx")
    desktop = Path.home() / "Desktop"
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    if desktop.is_dir():
        return desktop / f"IELTS_Reading_Evidence_Map_{stamp}.docx"
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
    parser.add_argument("--source-docx", type=Path, default=None, help="Source passage DOCX used only to choose the default output path.")
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
