#!/usr/bin/env python3
"""Validate an IELTS course-route workbook DOCX."""

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
    for marker in ["雅思课程路线学习手册", "下一步行动", "课程路线清单", "达标标准"]:
        if marker not in text:
            raise SystemExit(f"Missing required text: {marker}")
    if FONT not in doc_xml:
        raise SystemExit(f"{FONT} not found in document XML")
    tables = len(list(doc.iter(qn("tbl"))))
    if tables < 1:
        raise SystemExit("Expected at least one route table")
    if args.plan_json:
        plan = json.loads(args.plan_json.read_text(encoding="utf-8"))
        route_title = norm(plan.get("route_title", ""))
        if route_title and not contains(text, route_title):
            raise SystemExit("Route title missing from DOCX")
        found_course = False
        for subject in plan.get("subjects", []):
            if not isinstance(subject, dict):
                continue
            for unit in subject.get("units", []):
                if not isinstance(unit, dict):
                    continue
                for course in unit.get("courses", []):
                    if isinstance(course, dict) and course.get("title"):
                        found_course = True
                        if not contains(text, str(course["title"])[:100]):
                            raise SystemExit(f"Course title missing from DOCX: {course['title']}")
        if not found_course:
            raise SystemExit("Plan must contain at least one course")
    page_breaks = sum(1 for br in doc.iter(qn("br")) if br.get(qn("type")) == "page")
    words = len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+", text))
    print(f"OK: tables={tables}, page_breaks={page_breaks}, words={words}")


if __name__ == "__main__":
    main()
