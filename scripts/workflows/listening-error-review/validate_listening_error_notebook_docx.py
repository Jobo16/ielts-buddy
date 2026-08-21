#!/usr/bin/env python3
"""Validate an IELTS Listening error notebook DOCX."""

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


def norm(text: str) -> str:
    return " ".join(str(text).split())


def contains(haystack: str, needle: str) -> bool:
    return norm(needle).lower() in norm(haystack).lower()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--plan-json", type=Path, default=None)
    args = parser.parse_args()

    with ZipFile(args.docx) as zf:
        names = set(zf.namelist())
        missing = sorted({"word/document.xml", "word/styles.xml", "[Content_Types].xml"} - names)
        if missing:
            raise SystemExit(f"Missing required DOCX parts: {missing}")
        doc_xml = zf.read("word/document.xml").decode("utf-8")
        doc = ET.fromstring(doc_xml)
    text = text_of(doc)
    for marker in ["雅思听力错题本", "错题地图", "逐题分析", "重听重点", "微训练"]:
        if marker not in text:
            raise SystemExit(f"Missing required text: {marker}")
    tables = len(list(doc.iter(qn("tbl"))))
    if tables < 1:
        raise SystemExit("Expected at least one table")
    if FONT not in doc_xml:
        raise SystemExit(f"{FONT} not found in document XML")
    if args.plan_json:
        plan = json.loads(args.plan_json.read_text(encoding="utf-8"))
        items = [item for item in plan.get("items", []) if isinstance(item, dict)]
        if not items:
            raise SystemExit("Plan must contain listening items")
        for item in items:
            for key in ("correct_answer", "error_type", "replay_target", "micro_drill"):
                value = norm(item.get(key, ""))
                if value and not contains(text, value[:100]):
                    raise SystemExit(f"{key} missing from DOCX: {value[:100]}")
    page_breaks = sum(1 for br in doc.iter(qn("br")) if br.get(qn("type")) == "page")
    words = len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+", text))
    print(f"OK: tables={tables}, page_breaks={page_breaks}, words={words}")


if __name__ == "__main__":
    main()
