#!/usr/bin/env python3
"""Keep bundled copies of shared references identical across standalone Skills."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SHARED = ROOT / "shared"
REVIEW = {"ielts-buddy", "ielts-study-plan", "ielts-practice", "ielts-reading-review", "ielts-listening-review", "ielts-mock-review"}
DOCX = {"ielts-study-plan", "ielts-reading-review", "ielts-listening-review", "ielts-speaking-coach", "ielts-vocabulary-coach"}


def resource_pairs():
    for skill in sorted(SKILLS.iterdir()):
        if not skill.is_dir() or skill.name == "ielts-buddy-skills-updater":
            continue
        for name in ("api-access.md", "skill-taxonomy.json", "browser-routes.md"):
            yield SHARED / name, skill / "references" / name
        if skill.name in REVIEW:
            for name in ("learning-data.md", "review-records.md"):
                yield SHARED / name, skill / "references" / name
        if skill.name in DOCX:
            yield SHARED / "simple_docx.py", skill / "scripts" / "simple_docx.py"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for source, target in resource_pairs():
        if args.check:
            if not target.is_file() or target.read_bytes() != source.read_bytes():
                stale.append(str(target.relative_to(ROOT)))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    if stale:
        parser.error("outdated bundled resources: " + ", ".join(stale))
    print("shared resources checked" if args.check else "shared resources updated")


if __name__ == "__main__":
    main()
