#!/usr/bin/env python3
"""Validate an IELTS Speaking report DOCX."""

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
        missing = sorted({"word/document.xml", "word/styles.xml", "[Content_Types].xml"} - set(zf.namelist()))
        if missing:
            raise SystemExit(f"Missing required DOCX parts: {missing}")
        doc_xml = zf.read("word/document.xml").decode("utf-8")
        doc = ET.fromstring(doc_xml)
    text = text_of(doc)
    for marker in ["雅思口语反馈报告", "分数参考", "回答复盘", "自然表达版本", "可复用表达"]:
        if marker not in text:
            raise SystemExit(f"Missing required text: {marker}")
    if FONT not in doc_xml:
        raise SystemExit(f"{FONT} not found in document XML")
    if args.plan_json:
        plan = json.loads(args.plan_json.read_text(encoding="utf-8"))
        if not plan.get("band_estimate"):
            raise SystemExit("Plan must contain band_estimate")
        for item in [x for x in plan.get("answers", []) if isinstance(x, dict)]:
            for key in ("question", "answer", "natural_version"):
                value = norm(item.get(key, ""))
                if value and not contains(text, value[:100]):
                    raise SystemExit(f"{key} missing from DOCX: {value[:100]}")
    tables = len(list(doc.iter(qn("tbl"))))
    words = len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+", text))
    print(f"OK: tables={tables}, words={words}")


if __name__ == "__main__":
    main()
