#!/usr/bin/env python3
"""Compare the pinned learner API contract with the deployed public catalog."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = "https://work.ieltsbuddy.igopx.cn/api/v1/agent/capabilities"
FIELDS = ("id", "operationName", "auth", "scopes", "sideEffect", "requestSchema")


def public_capabilities(payload: dict) -> dict[str, dict]:
    operations = payload["capabilities"]
    if not isinstance(operations, list):
        raise ValueError("capabilities must be a list")
    result = {item["operationName"]: {key: item[key] for key in FIELDS} for item in operations}
    if len(result) != len(operations):
        raise ValueError("duplicate operationName")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="compare with the deployed public API")
    args = parser.parse_args()
    pinned = json.loads((ROOT / "contracts/agent-api-public.json").read_text(encoding="utf-8"))
    expected = public_capabilities(pinned)
    if not args.live:
        print(f"pinned public contract: {len(expected)} operations")
        return
    request = Request(URL, headers={"User-Agent": "ielts-buddy-skills-contract-check/1.0"})
    with urlopen(request, timeout=20) as response:
        live = json.load(response)
    if live.get("code") != 0:
        raise ValueError(f"public capability endpoint returned code {live.get('code')}")
    actual = public_capabilities(live["data"])
    if expected != actual:
        missing = sorted(expected.keys() - actual.keys())
        extra = sorted(actual.keys() - expected.keys())
        changed = sorted(name for name in expected.keys() & actual.keys() if expected[name] != actual[name])
        raise ValueError(f"deployed public contract differs: missing={missing}, extra={extra}, changed={changed}")
    print(f"deployed public contract matches: {len(expected)} operations")


if __name__ == "__main__":
    main()
