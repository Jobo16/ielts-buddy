#!/usr/bin/env python3
"""Extract readable IELTS Reading passage text from a DOCX."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"


def qn(tag: str) -> str:
    return f"{W}{tag}"


def text_of(el: ET.Element) -> str:
    parts: list[str] = []
    for child in el.iter():
        if child.tag == qn("t") and child.text:
            parts.append(child.text)
        elif child.tag == qn("tab"):
            parts.append("\t")
        elif child.tag == qn("br"):
            parts.append("\n")
    return "".join(parts)


def normalize_spaces(text: str) -> str:
    return " ".join(text.split())


def direct_paragraphs(root: ET.Element) -> list[ET.Element]:
    body = root.find(qn("body"))
    if body is None:
        return []
    return [child for child in list(body) if child.tag == qn("p")]


def is_question_boundary(text: str) -> bool:
    text = normalize_spaces(text)
    lower = text.lower()
    if re.match(r"^questions?\s+\d+(?:\s*[-–]\s*\d+)?\b", lower):
        return True
    if re.match(r"^(choose|complete|match|write)\b", lower) and len(text.split()) <= 18:
        return True
    markers = (
        "true, false or not given",
        "yes, no or not given",
        "choose the correct letter",
        "write the correct letter",
        "complete the summary",
        "reading passage questions",
    )
    return any(marker in lower for marker in markers)


def likely_title(paragraphs: list["Paragraph"]) -> str:
    for para in paragraphs[:8]:
        words = para.text.split()
        if 2 <= len(words) <= 14 and not is_question_boundary(para.text):
            return para.text
    return Path(paragraphs[0].source_file).stem if paragraphs else "IELTS Reading Passage"


@dataclass
class Paragraph:
    index: int
    text: str
    source_file: str


def extract_docx(path: Path) -> dict[str, object]:
    with ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))

    paragraphs: list[Paragraph] = []
    for index, paragraph in enumerate(direct_paragraphs(root), start=1):
        text = normalize_spaces(text_of(paragraph))
        if text:
            paragraphs.append(Paragraph(index=index, text=text, source_file=str(path)))

    passage: list[Paragraph] = []
    for para in paragraphs:
        if passage and is_question_boundary(para.text):
            break
        passage.append(para)

    if not passage:
        passage = paragraphs

    article_text = "\n\n".join(para.text for para in passage)
    return {
        "source_file": str(path),
        "title": likely_title(passage),
        "article_text": article_text,
        "passage_paragraph_indices": [para.index for para in passage],
        "paragraphs": [asdict(para) for para in paragraphs],
        "passage_paragraphs": [asdict(para) for para in passage],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    result = extract_docx(args.docx)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(args.output)
    else:
        print(text)


if __name__ == "__main__":
    main()
