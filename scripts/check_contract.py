#!/usr/bin/env python3
"""Validate learner API snapshots, or refresh them from the main application."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
URL = "https://work.ieltsbuddy.igopx.cn/api/v1/agent/capabilities"
FIELDS = (
    "id", "operationName", "auth", "scopes", "sideEffect",
    "destructive", "requestSchema", "requestHeaders",
)


def public_capabilities(payload: dict) -> dict[str, dict]:
    operations = payload["capabilities"]
    if not isinstance(operations, list):
        raise ValueError("capabilities must be a list")
    result = {item["operationName"]: {key: item[key] for key in FIELDS} for item in operations}
    if len(result) != len(operations):
        raise ValueError("duplicate operationName")
    return result


def refresh(source: Path) -> None:
    script = """
import { AGENT_API_VERSION, listCapabilityApiDocumentation } from './packages/ai-capabilities/src/index.ts';
process.stdout.write(JSON.stringify({ version: AGENT_API_VERSION, capabilities: listCapabilityApiDocumentation() }));
"""
    payload = json.loads(subprocess.check_output(
        ["node", "--import", "tsx", "--input-type=module", "-e", script], cwd=source, text=True,
    ))
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    operations = public_capabilities(payload)
    write_contract("agent-api-public.json", {
        "schemaVersion": 2,
        "apiVersion": payload["version"],
        "source": "IeltsBuddy/packages/ai-capabilities",
        "sourceRevision": revision,
        "capabilities": list(operations.values()),
    })
    write_contract("ielts-buddy-api-operations.json", {"schemaVersion": 1, "tools": list(operations)})
    footprints = next(item for item in payload["capabilities"] if item["id"] == "footprints.list")
    write_contract("footprints-list.json", {
        key: footprints[key] for key in ("id", "operationName", "requestSchema", "response")
    })


def write_contract(filename: str, value: dict) -> None:
    (CONTRACTS / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compare(pinned: dict, catalog: dict) -> None:
    expected = public_capabilities(pinned)
    actual_names = {entry["operationName"] for entry in catalog["capabilities"]}
    missing = sorted(expected.keys() - actual_names)
    extra = sorted(actual_names - expected.keys())
    changed = sorted(
        entry["operationName"] for entry in catalog["capabilities"]
        if entry["operationName"] in expected
        and any(entry.get(key) != expected[entry["operationName"]][key] for key in FIELDS)
    )
    if missing or extra or changed or catalog.get("version") != pinned["apiVersion"]:
        raise ValueError(
            f"public contract differs: expected={pinned['apiVersion']}, deployed={catalog.get('version')}, "
            f"missing={missing}, extra={extra}, changed={changed}"
        )
    public_capabilities(catalog)
    print(f"public API {pinned['apiVersion']} matches: {len(expected)} operations")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--live", action="store_true", help="compare with the deployed API")
    mode.add_argument("--sync-from", type=Path, metavar="IELTSBUDDY", help="refresh snapshots from a local main application checkout")
    parser.add_argument("--url", default=URL, help="API discovery or developer catalog URL for --live")
    args = parser.parse_args()
    if args.sync_from is not None:
        refresh(args.sync_from.resolve())
    pinned = json.loads((CONTRACTS / "agent-api-public.json").read_text(encoding="utf-8"))
    if not args.live:
        print(f"pinned public API {pinned['apiVersion']}: {len(public_capabilities(pinned))} operations")
        return
    request = Request(args.url, headers={"User-Agent": "ielts-buddy-skills-contract-check/1.1"})
    with urlopen(request, timeout=20) as response:
        live = json.load(response)
    if "code" in live and live["code"] != 0:
        raise ValueError(f"public capability endpoint returned code {live['code']}")
    compare(pinned, live.get("data", live))


if __name__ == "__main__":
    main()
