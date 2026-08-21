#!/usr/bin/env python3
"""Create an IELTS course-route workbook DOCX from a JSON plan."""

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
        return desktop / f"IELTS_Course_Route_Workbook_{stamp}.docx"
    return plan_path.with_suffix(".docx")


def course_rows(plan: dict[str, Any]) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for subject in dicts(plan.get("subjects", [])):
        subject_name = normalize_spaces(subject.get("subject", ""))
        for unit in dicts(subject.get("units", [])):
            unit_title = normalize_spaces(unit.get("title", ""))
            for course in dicts(unit.get("courses", [])):
                criteria = course.get("success_criteria", [])
                rows.append(
                    [
                        subject_name,
                        unit_title,
                        course.get("course_id", ""),
                        course.get("title", ""),
                        course.get("status", ""),
                        "; ".join(strings(criteria)) if isinstance(criteria, list) else criteria,
                    ]
                )
    return rows


def create(plan: dict[str, Any], output: Path) -> None:
    doc = SimpleDocx("雅思课程路线学习手册", "daily-study-loop")
    doc.heading("雅思课程路线学习手册", 1)
    doc.paragraph(f"路线：{normalize_spaces(plan.get('route_title', '雅思全科自学路线'))}")
    if plan.get("learner_goal"):
        doc.paragraph(f"目标：{normalize_spaces(plan['learner_goal'])}")
    if plan.get("timeframe"):
        doc.paragraph(f"时间范围：{normalize_spaces(plan['timeframe'])}")

    next_actions = dicts(plan.get("next_actions", []))
    if next_actions:
        doc.heading("下一步行动", 2)
        doc.table(
            ["优先级", "行动", "原因", "链接"],
            [[item.get("priority", ""), item.get("title", ""), item.get("reason", ""), item.get("browser_url", "")] for item in next_actions],
            [1000, 2800, 3200, 2360],
        )

    rows = course_rows(plan)
    doc.page_break()
    doc.heading("课程路线清单", 1)
    doc.table(
        ["科目", "单元", "课程 ID", "课程", "状态", "达标标准"],
        rows or [["", "", "", "", "", "没有提供课程路线。"]],
        [1100, 1700, 1000, 2400, 1100, 2060],
    )

    checkpoints = strings(plan.get("checkpoints", []))
    if checkpoints:
        doc.page_break()
        doc.heading("学习检查点", 1)
        for idx, item in enumerate(checkpoints, start=1):
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
