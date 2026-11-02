#!/usr/bin/env python3
"""Validate an IELTS Writing revision report DOCX."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"
FONT = "Times New Roman"


def qn(tag: str) -> str:
    return f"{W}{tag}"


def text_of(el: ET.Element) -> str:
    return "".join(t.text or "" for t in el.iter(qn("t")))


def normalize_spaces(text: str) -> str:
    return " ".join(text.split())


def contains_text(haystack: str, needle: str) -> bool:
    return normalize_spaces(needle).lower() in normalize_spaces(haystack).lower()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--plan-json", type=Path, default=None)
    args = parser.parse_args()

    with ZipFile(args.docx) as zf:
        names = set(zf.namelist())
        required = {"word/document.xml", "word/styles.xml", "[Content_Types].xml"}
        missing = sorted(required - names)
        if missing:
            raise SystemExit(f"Missing required DOCX parts: {missing}")
        doc_xml = zf.read("word/document.xml").decode("utf-8")
        doc = ET.fromstring(doc_xml)

    all_text = text_of(doc)
    for marker in [
        "雅思写作二改报告",
        "修改检查",
        "状态",
        "原问题",
        "教师备注",
        "修改后答案",
        "下一轮改写目标",
    ]:
        if marker not in all_text:
            raise SystemExit(f"Missing required revision report text: {marker}")

    tables = len(list(doc.iter(qn("tbl"))))
    if tables < 1:
        raise SystemExit("Expected at least one fix-check table")

    page_breaks = sum(1 for br in doc.iter(qn("br")) if br.get(qn("type")) == "page")
    if page_breaks < 2:
        raise SystemExit(f"Expected at least 2 page breaks, found {page_breaks}")

    if FONT not in doc_xml:
        raise SystemExit(f"{FONT} not found in document XML")

    if args.plan_json:
        plan = json.loads(args.plan_json.read_text(encoding="utf-8"))
        for item in plan.get("fix_checks", []):
            if isinstance(item, dict):
                issue = normalize_spaces(str(item.get("issue", "")))
                if issue and not contains_text(all_text, issue):
                    raise SystemExit(f"Fix-check issue missing from DOCX: {issue}")
        revised = plan.get("revised_essay", [])
        if isinstance(revised, list):
            for paragraph in revised:
                snippet = normalize_spaces(str(paragraph))[:80]
                if snippet and not contains_text(all_text, snippet):
                    raise SystemExit(f"Revised essay paragraph missing from DOCX: {snippet}")
        target = normalize_spaces(str(plan.get("next_rewrite_target", "")))
        if target and not contains_text(all_text, target[:80]):
            raise SystemExit("Next rewrite target missing from DOCX")

    paragraphs = len([p for p in doc.iter(qn("p")) if normalize_spaces(text_of(p))])
    words = len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+", all_text))
    print(f"OK: tables={tables}, page_breaks={page_breaks}, paragraphs={paragraphs}, words={words}")


if __name__ == "__main__":
    main()
