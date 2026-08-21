#!/usr/bin/env python3
"""Create an IELTS Listening error notebook DOCX from a JSON plan."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from simple_docx import SimpleDocx, normalize_spaces, word_count  # noqa: E402


def dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def strings(value: Any) -> list[str]:
    return [normalize_spaces(item) for item in value if normalize_spaces(item)] if isinstance(value, list) else []


def default_output(plan_path: Path) -> Path:
    desktop = Path.home() / "Desktop"
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    if desktop.is_dir():
        return desktop / f"IELTS_Listening_Error_Notebook_{stamp}.docx"
    return plan_path.with_suffix(".docx")


def create(plan: dict[str, Any], output: Path) -> None:
    doc = SimpleDocx("雅思听力错题本", "listening-error-review")
    doc.heading("雅思听力错题本", 1)
    doc.paragraph(f"来源：{normalize_spaces(plan.get('source_title', '雅思听力'))}")
    if plan.get("section_title"):
        doc.paragraph(f"部分：{normalize_spaces(plan['section_title'])}")
    if plan.get("summary"):
        doc.paragraph(plan["summary"])

    items = dicts(plan.get("items", []))
    rows = [
        [
            item.get("question_number", item.get("q", "")),
            item.get("user_answer", ""),
            item.get("correct_answer", ""),
            item.get("error_type", ""),
            item.get("replay_target", ""),
            item.get("micro_drill", ""),
        ]
        for item in items
    ] or [["", "", "", "", "", "没有提供听力错题。"]]
    doc.heading("错题地图", 2)
    doc.table(["题号", "你的答案", "正确答案", "错误类型", "重听重点", "微训练"], rows, [600, 1500, 1500, 1700, 2100, 1960])

    doc.page_break()
    doc.heading("逐题分析", 1)
    for item in items:
        q = normalize_spaces(item.get("question_number", item.get("q", "")))
        doc.heading(f"Q{q}: {normalize_spaces(item.get('correct_answer', 'Listening item'))}", 2)
        for label, key in [
            ("原文/提示", "transcript"),
            ("为什么错", "cause"),
            ("重听重点", "replay_target"),
            ("微训练", "micro_drill"),
        ]:
            if item.get(key):
                doc.paragraph(label, bold=True)
                doc.paragraph(item[key])

    review_plan = strings(plan.get("review_plan", []))
    if review_plan:
        doc.page_break()
        doc.heading("复习计划", 1)
        for idx, item in enumerate(review_plan, start=1):
            doc.paragraph(f"{idx}. {item}")

    vocabulary = dicts(plan.get("vocabulary", []))
    if vocabulary:
        doc.heading("实用词汇", 2)
        doc.table(
            ["词组", "含义", "来源句"],
            [[item.get("phrase", ""), item.get("meaning", ""), item.get("source_sentence", "")] for item in vocabulary],
            [2200, 2600, 4560],
        )

    if items:
        text = " ".join(str(item.get("transcript", "")) for item in items)
        if text:
            doc.paragraph(f"已复盘文本片段词数：{word_count(text)}", italic=True)
    doc.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--cleanup-plan", action="store_true")
    args = parser.parse_args()
    plan = json.loads(args.plan_json.read_text(encoding="utf-8"))
    output = args.output or default_output(args.plan_json)
    create(plan, output)
    if args.cleanup_plan:
        args.plan_json.unlink(missing_ok=True)
    print(output)


if __name__ == "__main__":
    main()
