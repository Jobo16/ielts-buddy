#!/usr/bin/env python3
"""Create an IELTS Speaking report DOCX from a JSON plan."""

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
        return desktop / f"IELTS_Speaking_Report_{stamp}.docx"
    return plan_path.with_suffix(".docx")


def create(plan: dict[str, Any], output: Path) -> None:
    doc = SimpleDocx("雅思口语反馈报告", "speaking-coach")
    doc.heading("雅思口语反馈报告", 1)
    doc.paragraph(f"练习：{normalize_spaces(plan.get('session_title', '雅思口语练习'))}")
    doc.paragraph(f"部分：{normalize_spaces(plan.get('part', ''))}")
    doc.paragraph(f"分数参考：{normalize_spaces(plan.get('band_estimate', ''))}", bold=True)
    if plan.get("overall_feedback"):
        doc.paragraph(plan["overall_feedback"])

    scores = plan.get("criterion_scores", {})
    if isinstance(scores, dict) and scores:
        doc.heading("维度评分参考", 2)
        rows = []
        for key, raw in scores.items():
            if isinstance(raw, dict):
                rows.append([key, raw.get("score", ""), raw.get("note", "")])
            else:
                rows.append([key, raw, ""])
        doc.table(["维度", "分数", "说明"], rows, [2600, 1200, 5560])

    answers = dicts(plan.get("answers", []))
    doc.page_break()
    doc.heading("回答复盘", 1)
    for idx, item in enumerate(answers, start=1):
        doc.heading(f"回答 {idx}: {normalize_spaces(item.get('question', '口语回答'))}", 2)
        for label, key in [
            ("原回答", "answer"),
            ("反馈", "feedback"),
            ("自然表达版本", "natural_version"),
            ("重点", "focus"),
        ]:
            if item.get(key):
                doc.paragraph(label, bold=True)
                doc.paragraph(item[key])
        chunks = strings(item.get("reusable_chunks", []))
        if chunks:
            doc.paragraph("可复用表达", bold=True)
            for chunk in chunks:
                doc.paragraph(f"- {chunk}")

    patterns = strings(plan.get("recurring_patterns", []))
    next_questions = strings(plan.get("next_questions", []))
    if patterns or next_questions:
        doc.page_break()
    if patterns:
        doc.heading("反复出现的问题", 1)
        for item in patterns:
            doc.paragraph(f"- {item}")
    if next_questions:
        doc.heading("下一轮问题", 1)
        for idx, item in enumerate(next_questions, start=1):
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
