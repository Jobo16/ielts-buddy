#!/usr/bin/env python3
"""Filter the curated IELTS Buddy learning-resource catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_CATALOG = (
    Path(__file__).resolve().parents[3]
    / "workflows"
    / "common"
    / "learning-resource-recommender"
    / "references"
    / "resources.json"
)


def load_catalog(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if value.get("schemaVersion") != 1 or not isinstance(value.get("resources"), list):
        raise ValueError(f"Invalid resource catalog: {path}")
    return value


def score(item: dict[str, Any], skill: str | None, query: str | None) -> int:
    value = 0
    if skill and skill in item.get("skills", []):
        value += 10
    blob = " ".join(
        [
            str(item.get("title", "")),
            str(item.get("description", "")),
            str(item.get("provider", "")),
            " ".join(item.get("skills", [])),
        ]
    ).lower()
    if query:
        for token in query.lower().split():
            if token and token in blob:
                value += 2
    if item.get("official"):
        value += 3
    if "ielts" in item.get("skills", []):
        value += 2
    if item.get("transcript") == "yes":
        value += 1
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", default=None)
    parser.add_argument("--level", default=None)
    parser.add_argument("--query", default=None)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    catalog = load_catalog(DEFAULT_CATALOG)
    items = catalog["resources"]
    if args.level:
        items = [item for item in items if args.level.upper() in item.get("levels", [])]
    if args.skill or args.query:
        items = sorted(items, key=lambda item: score(item, args.skill, args.query), reverse=True)
        items = [item for item in items if score(item, args.skill, args.query) > 0]
    items = items[: max(1, args.limit)]
    payload = {
        "source": str(DEFAULT_CATALOG),
        "lastReviewed": catalog["lastReviewed"],
        "count": len(items),
        "items": items,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
