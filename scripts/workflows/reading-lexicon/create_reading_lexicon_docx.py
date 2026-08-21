#!/usr/bin/env python3
"""Create an IELTS Reading lexicon DOCX from a JSON plan."""

from __future__ import annotations

import argparse
import copy
import html
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
FONT = "Times New Roman"
COMMENT_TZ = timezone(timedelta(hours=8))

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def xml_escape(text: str) -> str:
    return html.escape(text, quote=False)


def normalize_spaces(text: str) -> str:
    return " ".join(str(text).split())


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+", text))


def short_text(text: str, limit: int = 150) -> str:
    text = normalize_spaces(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "."


def run_xml(
    text: str,
    *,
    bold: bool = False,
    italic: bool = False,
    color: str | None = None,
    size: int | None = None,
    style: str | None = None,
) -> str:
    if text == "":
        return ""
    props = []
    if style:
        props.append(f'<w:rStyle w:val="{style}"/>')
    props.append(f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>')
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


def paragraph_xml(runs: list[str], style: str | None = None, keep_next: bool = False) -> str:
    ppr_parts = []
    if style:
        ppr_parts.append(f'<w:pStyle w:val="{style}"/>')
    if keep_next:
        ppr_parts.append("<w:keepNext/>")
    ppr_parts.append('<w:spacing w:after="120"/>')
    ppr = f"<w:pPr>{''.join(ppr_parts)}</w:pPr>"
    return f"<w:p>{ppr}{''.join(runs)}</w:p>"


def heading(text: str, level: int = 1) -> str:
    return paragraph_xml([run_xml(text, bold=True)], style=f"Heading{level}", keep_next=True)


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def comment_reference_run(cid: int) -> str:
    return (
        '<w:r><w:rPr><w:rStyle w:val="CommentReference"/>'
        f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/></w:rPr>'
        f'<w:commentReference w:id="{cid}"/></w:r>'
    )


def text_of(el: ET.Element) -> str:
    return "".join(t.text or "" for t in el.iter(qn(W_NS, "t")))


def direct_paragraphs(doc: ET.Element) -> list[ET.Element]:
    body = doc.find(qn(W_NS, "body"))
    if body is None:
        return []
    return [child for child in list(body) if child.tag == qn(W_NS, "p")]


def normalized_with_map(text: str) -> tuple[str, list[int]]:
    chars: list[str] = []
    index_map: list[int] = []
    pending_space = False
    pending_index = 0
    for idx, char in enumerate(text):
        if char.isspace():
            if chars and not pending_space:
                pending_space = True
                pending_index = idx
            continue
        if pending_space:
            chars.append(" ")
            index_map.append(pending_index)
            pending_space = False
        chars.append(char)
        index_map.append(idx)
    return "".join(chars), index_map


def find_loose_span(text: str, needle: str) -> tuple[int, int] | None:
    needle = needle.strip()
    if not needle:
        return None
    exact = text.find(needle)
    if exact >= 0:
        return exact, exact + len(needle)
    normalized_text, text_map = normalized_with_map(text.lower())
    normalized_needle = normalize_spaces(needle).lower()
    pos = normalized_text.find(normalized_needle)
    if pos < 0:
        return None
    end_pos = pos + len(normalized_needle) - 1
    return text_map[pos], text_map[end_pos] + 1


def parse_body_fragment(body_fragment: str) -> list[ET.Element]:
    wrapper = ET.fromstring(f'<w:wrapper xmlns:w="{W_NS}" xmlns:r="{R_NS}">{body_fragment}</w:wrapper>')
    return list(wrapper)


def runs_with_comment_ranges(text: str, ranges: list[dict[str, Any]]) -> list[str]:
    ranges = sorted(ranges, key=lambda item: (int(item["start"]), int(item["end"])))
    runs: list[str] = []
    cursor = 0
    for item in ranges:
        start, end, cid = int(item["start"]), int(item["end"]), int(item["id"])
        if cursor < start:
            runs.append(run_xml(text[cursor:start]))
        runs.append(f'<w:commentRangeStart w:id="{cid}"/>')
        runs.append(run_xml(text[start:end]))
        runs.append(f'<w:commentRangeEnd w:id="{cid}"/>')
        runs.append(comment_reference_run(cid))
        cursor = end
    if cursor < len(text):
        runs.append(run_xml(text[cursor:]))
    return runs


def replace_paragraph_runs(paragraph: ET.Element, ranges: list[dict[str, Any]]) -> None:
    original_text = text_of(paragraph)
    ppr = paragraph.find(qn(W_NS, "pPr"))
    ppr_copy = copy.deepcopy(ppr) if ppr is not None else None
    paragraph.clear()
    if ppr_copy is not None:
        paragraph.append(ppr_copy)
    for child in parse_body_fragment("".join(runs_with_comment_ranges(original_text, ranges))):
        paragraph.append(child)


def overlaps(span: tuple[int, int], ranges: list[dict[str, Any]]) -> bool:
    start, end = span
    return any(not (end <= int(item["start"]) or start >= int(item["end"])) for item in ranges)


def non_overlapping_span(text: str, start: int, end: int, ranges: list[dict[str, Any]]) -> tuple[int, int] | None:
    start = max(0, min(start, len(text)))
    end = max(start, min(end, len(text)))
    if start < end and not overlaps((start, end), ranges):
        return start, end
    for match in re.finditer(r"\S+", text[start:end]):
        candidate = (start + match.start(), start + match.end())
        if not overlaps(candidate, ranges):
            return candidate
    return None


def normalize_plan_indices(value: Any, paragraph_count: int) -> set[int]:
    if value is None:
        return set()
    values = value if isinstance(value, list) else [value]
    positions: set[int] = set()
    for raw in values:
        try:
            index = int(raw)
        except (TypeError, ValueError):
            continue
        if 1 <= index <= paragraph_count:
            positions.add(index - 1)
        elif 0 <= index < paragraph_count:
            positions.add(index)
    return positions


def allowed_paragraph_positions(plan: dict[str, Any], paragraph_count: int) -> set[int] | None:
    for key in ("passage_paragraph_indices", "article_paragraph_indices", "source_paragraph_indices"):
        positions = normalize_plan_indices(plan.get(key), paragraph_count)
        if positions:
            return positions
    return None


def term_value(term: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = term.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def terms_of(plan: dict[str, Any]) -> list[dict[str, Any]]:
    raw_terms = plan.get("terms") or plan.get("items") or plan.get("lexicon") or []
    if not isinstance(raw_terms, list):
        raise SystemExit("Lexicon plan must contain a terms array")
    terms = [term for term in raw_terms if isinstance(term, dict) and term_value(term, "phrase", "term")]
    if not terms:
        raise SystemExit("Lexicon plan does not contain any terms with a phrase")
    return terms


def phrase_of(term: dict[str, Any]) -> str:
    return term_value(term, "phrase", "term")


def expansion_text(term: dict[str, Any]) -> str:
    value = term.get("expansion") or term.get("expansions") or term.get("related")
    if isinstance(value, list):
        return "; ".join(normalize_spaces(item) for item in value if normalize_spaces(item))
    if isinstance(value, str):
        return normalize_spaces(value)
    return ""


def comment_text_for_term(term: dict[str, Any]) -> str:
    meaning = term_value(term, "meaning", "meaning_zh", "definition")
    usage = term_value(term, "usage", "note", "why")
    if meaning and usage:
        return short_text(f"{meaning} | {usage}", 240)
    return short_text(meaning or usage or phrase_of(term), 240)


def cell_xml(text: str, *, shaded: bool = False, bold: bool = False, width: int = 2400) -> str:
    shade = '<w:shd w:fill="D9EAF7"/>' if shaded else ""
    tcpr = f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shade}</w:tcPr>'
    return f"<w:tc>{tcpr}{paragraph_xml([run_xml(text, bold=bold)])}</w:tc>"


def table_xml(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    widths = [2500, 3600, 4500]
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for width in widths)
    body = [
        '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/>'
        '<w:tblBorders><w:top w:val="single" w:sz="6" w:color="B7C9D6"/>'
        '<w:left w:val="single" w:sz="6" w:color="B7C9D6"/>'
        '<w:bottom w:val="single" w:sz="6" w:color="B7C9D6"/>'
        '<w:right w:val="single" w:sz="6" w:color="B7C9D6"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="D7E1E8"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="D7E1E8"/></w:tblBorders></w:tblPr>'
        f"<w:tblGrid>{grid}</w:tblGrid>"
    ]
    for row_index, row in enumerate(rows):
        body.append("<w:tr>")
        for cell_index, value in enumerate(row[:3]):
            body.append(
                cell_xml(
                    normalize_spaces(value),
                    shaded=row_index == 0,
                    bold=row_index == 0 or cell_index == 0,
                    width=widths[cell_index],
                )
            )
        body.append("</w:tr>")
    body.append("</w:tbl>")
    return "".join(body)


def review_prompts(plan: dict[str, Any], terms: list[dict[str, Any]]) -> list[str]:
    raw = plan.get("review_prompts") or plan.get("prompts") or []
    if isinstance(raw, list) and raw:
        return [normalize_spaces(item) for item in raw if normalize_spaces(item)]
    prompts: list[str] = []
    for term in terms[:8]:
        phrase = phrase_of(term)
        example = term_value(term, "example")
        if example:
            cloze = re.sub(re.escape(phrase), "________", example, count=1, flags=re.I)
            prompts.append(cloze if cloze != example else f"Use '{phrase}' in one sentence about the reading passage.")
        else:
            prompts.append(f"Use '{phrase}' in one sentence about the reading passage.")
    return prompts


def lexicon_body_xml(plan: dict[str, Any], include_initial_break: bool) -> str:
    terms = terms_of(plan)
    body: list[str] = []
    if include_initial_break:
        body.append(page_break())

    title = term_value(plan, "title") or "雅思阅读词汇手册"
    source_title = term_value(plan, "source_title", "passage_title")
    body.append(paragraph_xml([run_xml(title, bold=True, color="1F4E79", size=36)], style="Title"))
    if source_title:
        body.append(paragraph_xml([run_xml(source_title, italic=True, color="555555")]))
    body.append(paragraph_xml([run_xml(f"{len(terms)} 个高价值篇章词组", bold=True)]))

    rows = [["词组", "含义", "为什么重要"]]
    for term in terms:
        rows.append([
            phrase_of(term),
            short_text(term_value(term, "meaning", "meaning_zh", "definition"), 120),
            short_text(term_value(term, "usage", "note", "why"), 140),
        ])
    body.append(heading("核心词汇", 2))
    body.append(table_xml(rows))

    body.append(heading("用法说明", 2))
    for index, term in enumerate(terms, start=1):
        phrase = phrase_of(term)
        part = term_value(term, "part_of_speech", "pos")
        category = term_value(term, "category")
        band_value = term_value(term, "band_value", "priority")
        meta = "; ".join(item for item in (part, category, band_value) if item)
        body.append(paragraph_xml([run_xml(f"{index}. {phrase}", bold=True, color="1F4E79"), run_xml(f" ({meta})" if meta else "", italic=True)], keep_next=True))
        meaning = term_value(term, "meaning", "meaning_zh", "definition")
        if meaning:
            body.append(paragraph_xml([run_xml("含义：", bold=True), run_xml(meaning)]))
        usage = term_value(term, "usage", "note", "why")
        if usage:
            body.append(paragraph_xml([run_xml("用法：", bold=True), run_xml(usage)]))
        expansion = expansion_text(term)
        if expansion:
            body.append(paragraph_xml([run_xml("拓展：", bold=True), run_xml(expansion)]))
        example = term_value(term, "example")
        if example:
            body.append(paragraph_xml([run_xml("例句：", bold=True), run_xml(example, italic=True)]))
        source = term_value(term, "source_sentence", "source")
        if source:
            body.append(paragraph_xml([run_xml("来源：", bold=True), run_xml(short_text(source, 260), color="555555")]))

    body.append(page_break())
    body.append(heading("复习提示", 2))
    for index, prompt in enumerate(review_prompts(plan, terms), start=1):
        body.append(paragraph_xml([run_xml(f"{index}. ", bold=True), run_xml(prompt)]))
    return "".join(body)


def content_types_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/comments.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>
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
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" Target="comments.xml"/>
</Relationships>"""


def styles_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W_NS}">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:rPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:qFormat/><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:b/><w:color w:val="1F4E79"/><w:sz w:val="36"/><w:szCs w:val="36"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="Heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:b/><w:color w:val="1F4E79"/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="Heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:b/><w:color w:val="1F4E79"/><w:sz w:val="26"/><w:szCs w:val="26"/></w:rPr></w:style>
  <w:style w:type="character" w:styleId="CommentReference"><w:name w:val="Comment Reference"/><w:semiHidden/><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/><w:vertAlign w:val="superscript"/><w:color w:val="0000FF"/></w:rPr></w:style>
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
  <dc:title>雅思阅读词汇手册</dc:title>
  <dc:creator>ielts-reading-lexicon</dc:creator>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def comments_xml(comments: list[dict[str, Any]], author: str) -> str:
    now = datetime.now(COMMENT_TZ).isoformat(timespec="seconds")
    body = []
    for item in comments:
        cid = int(item["id"])
        text = xml_escape(str(item["text"]))
        body.append(
            f'<w:comment w:id="{cid}" w:author="{xml_escape(author)}" w:date="{now}" w:initials="CE">'
            '<w:p><w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:annotationRef/></w:r>'
            f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/></w:rPr><w:t>{text}</w:t></w:r></w:p></w:comment>'
        )
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + f'<w:comments xmlns:w="{W_NS}">{"".join(body)}</w:comments>'


def register_document_namespaces(document_xml: str) -> None:
    match = re.search(r"<w:document\b([^>]*)>", document_xml)
    if not match:
        return
    for prefix, uri in re.findall(r'xmlns:([^=\s]+)="([^"]+)"', match.group(1)):
        ET.register_namespace(prefix, uri)


def restore_document_root_namespaces(serialized_xml: str, original_xml: str) -> str:
    original_match = re.search(r"<w:document\b[^>]*>", original_xml)
    output_match = re.search(r"<w:document\b[^>]*>", serialized_xml)
    if not original_match or not output_match:
        return serialized_xml
    original_tag = original_match.group(0)
    output_tag = output_match.group(0)
    original_namespaces = dict(re.findall(r'xmlns:([^=\s]+)="([^"]+)"', original_tag))
    output_prefixes = set(re.findall(r'xmlns:([^=\s]+)="[^"]+"', output_tag))
    original_ignorable = re.search(r'\bmc:Ignorable="([^"]*)"', original_tag)
    if original_ignorable:
        ignorable_attr = f'mc:Ignorable="{original_ignorable.group(1)}"'
        if re.search(r'\b(?:mc|ns\d+):Ignorable="[^"]*"', output_tag):
            output_tag = re.sub(r'\b(?:mc|ns\d+):Ignorable="[^"]*"', ignorable_attr, output_tag)
        else:
            output_tag = output_tag[:-1] + f" {ignorable_attr}>"
    additions = []
    for prefix, uri in original_namespaces.items():
        if prefix not in output_prefixes:
            additions.append(f' xmlns:{prefix}="{html.escape(uri, quote=True)}"')
    if additions:
        output_tag = output_tag[:-1] + "".join(additions) + ">"
    restored = serialized_xml[: output_match.start()] + output_tag + serialized_xml[output_match.end():]
    original_decl = re.match(r"\s*(<\?xml[^>]*\?>)", original_xml)
    if original_decl and not restored.lstrip().startswith("<?xml"):
        restored = original_decl.group(1) + "\n" + restored
    return restored


def insert_body_fragment(body: ET.Element, body_fragment: str) -> None:
    insert_at = len(body)
    body_children = list(body)
    if body_children and body_children[-1].tag == qn(W_NS, "sectPr"):
        insert_at -= 1
    for child in parse_body_fragment(body_fragment):
        body.insert(insert_at, child)
        insert_at += 1


def annotate_document_xml(document_bytes: bytes, plan: dict[str, Any], start_comment_id: int) -> tuple[bytes, list[dict[str, Any]]]:
    original_xml = document_bytes.decode("utf-8")
    register_document_namespaces(original_xml)
    document = ET.fromstring(document_bytes)
    body = document.find(qn(W_NS, "body"))
    if body is None:
        raise SystemExit("Could not find document body insertion point")
    paragraphs = [child for child in list(body) if child.tag == qn(W_NS, "p")]
    allowed = allowed_paragraph_positions(plan, len(paragraphs))
    search_positions = sorted(allowed) if allowed else list(range(len(paragraphs)))
    comment_ranges: dict[int, list[dict[str, Any]]] = {}
    new_comments: list[dict[str, Any]] = []
    unmatched: list[str] = []
    next_comment_id = start_comment_id

    for term in terms_of(plan):
        phrase = phrase_of(term)
        matched = False
        for paragraph_idx in search_positions:
            paragraph_text = text_of(paragraphs[paragraph_idx])
            span = find_loose_span(paragraph_text, phrase)
            if span is None:
                continue
            ranges = comment_ranges.setdefault(paragraph_idx, [])
            usable = non_overlapping_span(paragraph_text, span[0], span[1], ranges)
            if usable is None:
                continue
            item = {
                "start": usable[0],
                "end": usable[1],
                "text": comment_text_for_term(term),
                "id": next_comment_id,
            }
            ranges.append(item)
            new_comments.append(item)
            next_comment_id += 1
            matched = True
            break
        if not matched:
            unmatched.append(phrase)

    if unmatched:
        raise SystemExit(f"Could not anchor phrase(s) in the source DOCX: {', '.join(unmatched[:6])}")

    for paragraph_idx, ranges in comment_ranges.items():
        replace_paragraph_runs(paragraphs[paragraph_idx], ranges)
    insert_body_fragment(body, lexicon_body_xml(plan, include_initial_break=True))
    serialized = ET.tostring(document, encoding="unicode")
    serialized = restore_document_root_namespaces(serialized, original_xml)
    return serialized.encode("utf-8"), new_comments


def max_existing_comment_id(zf: ZipFile) -> int:
    if "word/comments.xml" not in zf.namelist():
        return -1
    root = ET.fromstring(zf.read("word/comments.xml"))
    ids = []
    for comment in root.findall(qn(W_NS, "comment")):
        cid = comment.get(qn(W_NS, "id"))
        if cid is not None and cid.isdigit():
            ids.append(int(cid))
    return max(ids) if ids else -1


def merge_comments_xml(existing: bytes | None, new_comments: list[dict[str, Any]], author: str) -> bytes:
    root = ET.fromstring(existing) if existing else ET.Element(qn(W_NS, "comments"))
    now = datetime.now(COMMENT_TZ).isoformat(timespec="seconds")
    for item in new_comments:
        comment = ET.SubElement(root, qn(W_NS, "comment"), {
            qn(W_NS, "id"): str(int(item["id"])),
            qn(W_NS, "author"): author,
            qn(W_NS, "date"): now,
            qn(W_NS, "initials"): "CE",
        })
        para = ET.SubElement(comment, qn(W_NS, "p"))
        ref_run = ET.SubElement(para, qn(W_NS, "r"))
        ref_pr = ET.SubElement(ref_run, qn(W_NS, "rPr"))
        ET.SubElement(ref_pr, qn(W_NS, "rStyle"), {qn(W_NS, "val"): "CommentReference"})
        ET.SubElement(ref_run, qn(W_NS, "annotationRef"))
        text_run = ET.SubElement(para, qn(W_NS, "r"))
        text_pr = ET.SubElement(text_run, qn(W_NS, "rPr"))
        ET.SubElement(text_pr, qn(W_NS, "rFonts"), {
            qn(W_NS, "ascii"): FONT,
            qn(W_NS, "hAnsi"): FONT,
            qn(W_NS, "cs"): FONT,
        })
        text_node = ET.SubElement(text_run, qn(W_NS, "t"))
        text_node.text = str(item["text"])
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def ensure_comment_relationship(rels_bytes: bytes | None) -> bytes:
    root = ET.fromstring(rels_bytes) if rels_bytes else ET.Element(qn(PKG_REL_NS, "Relationships"))
    for rel in root.findall(qn(PKG_REL_NS, "Relationship")):
        if rel.get("Type") == "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments":
            return ET.tostring(root, encoding="utf-8", xml_declaration=True)
    existing_ids = {rel.get("Id", "") for rel in root.findall(qn(PKG_REL_NS, "Relationship"))}
    next_num = 1
    while f"rId{next_num}" in existing_ids:
        next_num += 1
    ET.SubElement(root, qn(PKG_REL_NS, "Relationship"), {
        "Id": f"rId{next_num}",
        "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments",
        "Target": "comments.xml",
    })
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def ensure_comments_content_type(content_types_bytes: bytes) -> bytes:
    root = ET.fromstring(content_types_bytes)
    for override in root.findall(qn(CT_NS, "Override")):
        if override.get("PartName") == "/word/comments.xml":
            return ET.tostring(root, encoding="utf-8", xml_declaration=True)
    ET.SubElement(root, qn(CT_NS, "Override"), {
        "PartName": "/word/comments.xml",
        "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml",
    })
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def default_output_path(input_path: Path | None) -> Path:
    if input_path:
        return input_path.with_name(f"{input_path.stem}(lexicon).docx")
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    return Path.home() / "Desktop" / f"IELTS_Reading_Lexicon_{stamp}.docx"


def avoid_overwrite(path: Path) -> Path:
    if not path.exists():
        return path
    suffix = path.suffix
    stem = path.stem
    parent = path.parent
    if stem.endswith("(lexicon)"):
        prefix = stem[: -len("(lexicon)")]
        template = lambda n: parent / f"{prefix}(lexicon {n}){suffix}"
    else:
        template = lambda n: parent / f"{stem} {n}{suffix}"
    for n in range(2, 100):
        candidate = template(n)
        if not candidate.exists():
            return candidate
    raise SystemExit(f"Could not find non-overwriting filename for {path}")


def write_standalone_docx(plan: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}" xmlns:r="{R_NS}"><w:body>'
        + lexicon_body_xml(plan, include_initial_break=False)
        + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>'
        + "</w:body></w:document>"
    )
    with ZipFile(output, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml())
        zf.writestr("_rels/.rels", rels_xml())
        zf.writestr("docProps/app.xml", app_xml())
        zf.writestr("docProps/core.xml", core_xml())
        zf.writestr("word/_rels/document.xml.rels", document_rels_xml())
        zf.writestr("word/document.xml", doc_xml)
        zf.writestr("word/styles.xml", styles_xml())
        zf.writestr("word/comments.xml", comments_xml([], "Cyber Esme"))


def write_annotated_docx(plan: dict[str, Any], input_docx: Path, output: Path, author: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if input_docx.resolve() != output.resolve():
        shutil.copyfile(input_docx, output)
    with ZipFile(output, "r") as zin:
        existing = {name: zin.read(name) for name in zin.namelist()}
        start_comment_id = max_existing_comment_id(zin) + 1
    document_xml_bytes, new_comments = annotate_document_xml(existing["word/document.xml"], plan, start_comment_id)
    replacements = {
        "word/document.xml": document_xml_bytes,
        "word/comments.xml": merge_comments_xml(existing.get("word/comments.xml"), new_comments, author),
        "word/_rels/document.xml.rels": ensure_comment_relationship(existing.get("word/_rels/document.xml.rels")),
        "[Content_Types].xml": ensure_comments_content_type(existing["[Content_Types].xml"]),
    }
    with ZipFile(output, "w", ZIP_DEFLATED) as zout:
        for name, data in existing.items():
            zout.writestr(name, replacements.get(name, data))
        for name, data in replacements.items():
            if name not in existing:
                zout.writestr(name, data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lexicon_json", type=Path)
    parser.add_argument("--input-docx", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--author", default="Cyber Esme")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--cleanup-plan", action="store_true")
    args = parser.parse_args()

    plan = json.loads(args.lexicon_json.read_text(encoding="utf-8"))
    output = args.output or default_output_path(args.input_docx)
    if not args.overwrite:
        output = avoid_overwrite(output)
    if args.input_docx:
        write_annotated_docx(plan, args.input_docx, output, args.author)
    else:
        write_standalone_docx(plan, output)
    print(output)
    if args.cleanup_plan:
        args.lexicon_json.unlink()
        print(f"Deleted temporary lexicon plan: {args.lexicon_json}")


if __name__ == "__main__":
    main()
