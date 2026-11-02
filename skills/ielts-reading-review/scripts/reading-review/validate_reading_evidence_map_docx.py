#!/usr/bin/env python3
"""Validate an IELTS Reading evidence-map DOCX."""

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
        "雅思阅读证据图",
        "答案证据图",
        "逐题分析",
        "证据",
        "同义替换桥",
        "陷阱/干扰项",
        "错误类型",
    ]:
        if marker not in all_text:
            raise SystemExit(f"Missing required evidence-map text: {marker}")

    tables = len(list(doc.iter(qn("tbl"))))
    if tables < 1:
        raise SystemExit("Expected at least one evidence-map table")

    page_breaks = sum(1 for br in doc.iter(qn("br")) if br.get(qn("type")) == "page")
    if page_breaks < 1:
        raise SystemExit(f"Expected at least 1 page break, found {page_breaks}")

    if FONT not in doc_xml:
        raise SystemExit(f"{FONT} not found in document XML")

    if args.plan_json:
        plan = json.loads(args.plan_json.read_text(encoding="utf-8"))
        items = [item for item in plan.get("items", []) if isinstance(item, dict)]
        if not items:
            raise SystemExit("Plan must contain at least one reading review item")
        for item in items:
            for key in ("correct_answer", "evidence", "paraphrase_bridge", "error_type"):
                value = normalize_spaces(str(item.get(key, "")))
                if value and not contains_text(all_text, value[:100]):
                    raise SystemExit(f"{key} missing from DOCX: {value[:100]}")
            q = normalize_spaces(str(item.get("question_number", item.get("q", ""))))
            if q and not contains_text(all_text, q):
                raise SystemExit(f"Question number missing from DOCX: {q}")

    paragraphs = len([p for p in doc.iter(qn("p")) if normalize_spaces(text_of(p))])
    words = len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+", all_text))
    print(f"OK: tables={tables}, page_breaks={page_breaks}, paragraphs={paragraphs}, words={words}")


if __name__ == "__main__":
    main()
