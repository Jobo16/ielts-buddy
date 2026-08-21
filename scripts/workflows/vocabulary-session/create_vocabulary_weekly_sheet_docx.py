#!/usr/bin/env python3
"""Create an IELTS vocabulary weekly sheet DOCX from a JSON plan."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from simple_docx import SimpleDocx, normalize_spaces  # noqa: E402


def dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def strings(value: Any) -> list[str]:
    return [normalize_spaces(item) for item in value if normalize_spaces(item)] if isinstance(value, list) else []


def default_output(plan_path: Path) -> Path:
    desktop = Path.home() / "Desktop"
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    if desktop.is_dir():
        return desktop / f"IELTS_Vocabulary_Weekly_Sheet_{stamp}.docx"
    return plan_path.with_suffix(".docx")


def create(plan: dict[str, Any], output: Path) -> None:
    doc = SimpleDocx("雅思词汇周复习表", "vocabulary-session")
    doc.heading("雅思词汇周复习表", 1)
    doc.paragraph(f"周次：{normalize_spaces(plan.get('week_title', '本周'))}")
    doc.paragraph(f"词书：{normalize_spaces(plan.get('wordbook', '雅思词汇'))}")
    if plan.get("summary"):
        doc.paragraph(plan["summary"])

    stats = plan.get("stats", {})
    if isinstance(stats, dict) and stats:
        doc.heading("进度概览", 2)
        doc.table(["指标", "数值"], [[key, value] for key, value in stats.items()], [3600, 5760])

    words = dicts(plan.get("words", []))
    doc.heading("单词复习表", 2)
    rows = [
        [
            item.get("phrase", ""),
            item.get("meaning", ""),
            item.get("learning_state", ""),
            item.get("last_rating", ""),
            item.get("next_review_at", ""),
            item.get("example", ""),
        ]
        for item in words
    ] or [["", "", "", "", "", "没有提供单词。"]]
    doc.table(["词组", "含义", "状态", "上次", "下次复习", "例句"], rows, [1700, 1900, 1100, 900, 1500, 2260])

    weak = dicts(plan.get("weak_words", []))
    due = dicts(plan.get("due_reviews", []))
    if weak or due:
        doc.page_break()
    if weak:
        doc.heading("薄弱词", 1)
        doc.table(
            ["词组", "问题", "修正方式"],
            [[item.get("phrase", ""), item.get("problem", ""), item.get("fix", "")] for item in weak],
            [2200, 3360, 3800],
        )
    if due:
        doc.heading("下一批待复习", 1)
        doc.table(
            ["词组", "到期时间", "模式"],
            [[item.get("phrase", ""), item.get("due_at", ""), item.get("mode", "")] for item in due],
            [3200, 2600, 3560],
        )

    prompts = strings(plan.get("practice_prompts", []))
    if prompts:
        doc.page_break()
        doc.heading("练习提示", 1)
        for idx, item in enumerate(prompts, start=1):
            doc.paragraph(f"{idx}. {item}")
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
