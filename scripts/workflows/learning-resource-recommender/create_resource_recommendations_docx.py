#!/usr/bin/env python3
"""Create an IELTS learning-resource recommendation DOCX from a JSON plan."""

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
        return desktop / f"IELTS_Resource_Recommendations_{stamp}.docx"
    return plan_path.with_suffix(".docx")


def create(plan: dict[str, Any], output: Path) -> None:
    doc = SimpleDocx("雅思学习资源推荐", "learning-resource-recommender")
    doc.heading("雅思学习资源推荐", 1)
    doc.paragraph(f"目标：{normalize_spaces(plan.get('learner_goal', '雅思自学'))}")
    doc.paragraph(f"重点：{normalize_spaces(plan.get('focus', ''))}")
    doc.paragraph(f"水平：{normalize_spaces(plan.get('level', ''))}")
    doc.paragraph(f"时间预算：{normalize_spaces(plan.get('time_budget', ''))}")
    if plan.get("rationale"):
        doc.paragraph(plan["rationale"])

    recommendations = dicts(plan.get("recommendations", []))
    doc.heading("推荐资源", 2)
    rows = [
        [
            item.get("rank", ""),
            item.get("title", ""),
            item.get("category", ""),
            item.get("fit", ""),
            item.get("url", ""),
        ]
        for item in recommendations
    ] or [["", "", "", "没有提供资源。", ""]]
    doc.table(["排序", "资源", "分类", "适合原因", "URL"], rows, [700, 2100, 1800, 3000, 1760])

    doc.page_break()
    doc.heading("使用方法", 1)
    for item in recommendations:
        doc.heading(f"{item.get('rank', '')}. {normalize_spaces(item.get('title', '资源'))}", 2)
        if item.get("how_to_use"):
            doc.paragraph("怎么用", bold=True)
            doc.paragraph(item["how_to_use"])
        if item.get("bring_back"):
            doc.paragraph("带回给 Agent", bold=True)
            doc.paragraph(item["bring_back"])

    weekly_plan = strings(plan.get("weekly_plan", []))
    if weekly_plan:
        doc.page_break()
        doc.heading("一周计划", 1)
        for idx, item in enumerate(weekly_plan, start=1):
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
