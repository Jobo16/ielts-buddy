from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
FONT = "Times New Roman"


def normalize_spaces(text: Any) -> str:
    return " ".join(str(text).split())


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+", text))


def short_text(text: Any, limit: int = 180) -> str:
    text = normalize_spaces(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def xml_escape(text: Any) -> str:
    return html.escape(str(text), quote=False)


def run_xml(text: Any, *, bold: bool = False, italic: bool = False, color: str | None = None, size: int | None = None) -> str:
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


class SimpleDocx:
    def __init__(self, title: str, creator: str) -> None:
        self.title = title
        self.creator = creator
        self.body: list[str] = []

    def paragraph(self, text: Any, *, bold: bool = False, italic: bool = False, color: str | None = None) -> None:
        self.body.append(self.paragraph_xml([run_xml(text, bold=bold, italic=italic, color=color)]))

    def heading(self, text: str, level: int = 1) -> None:
        size = 32 if level == 1 else 26
        self.body.append(self.paragraph_xml([run_xml(text, bold=True, size=size)], style=f"Heading{level}", keep_next=True))

    def page_break(self) -> None:
        self.body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    def table(self, headers: list[str], rows: list[list[Any]], widths: list[int]) -> None:
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
            parts.append(self.cell_xml(header, width=width, bold=True, fill="EAF2F8"))
        parts.append("</w:tr>")
        for row in rows:
            parts.append("<w:tr>")
            for value, width in zip(row, widths):
                parts.append(self.cell_xml(value, width=width))
            parts.append("</w:tr>")
        parts.append("</w:tbl>")
        self.body.append("".join(parts))

    def save(self, output: Path) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        document = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:document xmlns:w="{W_NS}" xmlns:r="{R_NS}"><w:body>'
            f'{"".join(self.body)}'
            '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>'
            '</w:body></w:document>'
        )
        with ZipFile(output, "w", ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", self.content_types_xml())
            zf.writestr("_rels/.rels", self.rels_xml())
            zf.writestr("word/_rels/document.xml.rels", self.document_rels_xml())
            zf.writestr("word/document.xml", document)
            zf.writestr("word/styles.xml", self.styles_xml())
            zf.writestr("docProps/core.xml", self.core_xml())
            zf.writestr("docProps/app.xml", self.app_xml())

    @staticmethod
    def paragraph_xml(runs: list[str], *, style: str | None = None, keep_next: bool = False) -> str:
        ppr = []
        if style:
            ppr.append(f'<w:pStyle w:val="{style}"/>')
        if keep_next:
            ppr.append("<w:keepNext/>")
        ppr.append('<w:spacing w:after="120"/>')
        return f"<w:p><w:pPr>{''.join(ppr)}</w:pPr>{''.join(runs)}</w:p>"

    @staticmethod
    def cell_xml(text: Any, *, width: int, bold: bool = False, fill: str | None = None) -> str:
        shading = f'<w:shd w:fill="{fill}"/>' if fill else ""
        tcpr = f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shading}</w:tcPr>'
        return f"<w:tc>{tcpr}{SimpleDocx.paragraph_xml([run_xml(short_text(text), bold=bold)])}</w:tc>"

    def content_types_xml(self) -> str:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

    def rels_xml(self) -> str:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

    def document_rels_xml(self) -> str:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

    def styles_xml(self) -> str:
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W_NS}">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:rPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="Heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:b/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="Heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:b/><w:sz w:val="26"/><w:szCs w:val="26"/></w:rPr></w:style>
</w:styles>"""

    def app_xml(self) -> str:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
</Properties>"""

    def core_xml(self) -> str:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{xml_escape(self.title)}</dc:title>
  <dc:creator>{xml_escape(self.creator)}</dc:creator>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""
