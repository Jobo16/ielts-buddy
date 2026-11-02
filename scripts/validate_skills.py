#!/usr/bin/env python3
"""Validate standalone Skill distribution and its pinned public API contract."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"\]\(([^)]+)\)")
OPERATION = re.compile(r"\bielts_(?:notes|feedback|learning|courses|assets|resources|vocabulary|prep|prediction|practice|dictation|question_research|speaking_materials|review|mock|writing|footprints|learner|study_todos|study_plans|notifications)_[a-z0-9_]+\b")
FORBIDDEN_TEXT = (re.compile(r"/Users/"), re.compile(r"\bDownloads\b"), re.compile(r"\bCambridge IELTS\b", re.I))


def tracked_and_new():
    raw = subprocess.check_output(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT)
    return sorted(ROOT / name.decode() for name in raw.split(b"\0") if name and (ROOT / name.decode()).is_file())


def validate():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    published = json.loads((ROOT / "contracts/agent-api-public.json").read_text())
    operation_names = {item["operationName"] for item in published["capabilities"]}
    assert set(json.loads((ROOT / "contracts/ielts-buddy-api-operations.json").read_text())["tools"]) == operation_names
    assert len(operation_names) == len(published["capabilities"])
    listed = {item["id"] for item in manifest["skills"]}
    assert len(listed) == len(manifest["skills"])
    assert listed == {item.name for item in SKILLS.iterdir() if item.is_dir()}
    assert "ielts-buddy" in listed and "ielts-buddy-skills-updater" in listed
    for item in manifest["skills"]:
        name = item["id"]
        assert NAME.fullmatch(name) and item["entry"] == f"skills/{name}/SKILL.md"
        root = SKILLS / name
        skill = (root / "SKILL.md").read_text()
        assert skill.startswith(f"---\nname: {name}\n") and "\ndescription: " in skill.split("---", 2)[1]
        assert f"${name}" in (root / "agents/openai.yaml").read_text()
        assert json.loads((root / "manifest.json").read_text())["version"] == manifest["version"]
        if name == "ielts-buddy": assert (root / "scripts/ielts_buddy_api.py").is_file()
        if name == "ielts-buddy-skills-updater": assert (root / "scripts/update_skills.py").is_file()
        for p in root.rglob("*.md"):
            text = p.read_text()
            for op in OPERATION.findall(text):
                if op not in operation_names and op != "ielts_buddy_api":
                    raise ValueError(f"{p}: unknown API operation {op}")
            for target in LINK.findall(text):
                if target.startswith(("https://", "http://", "#", "mailto:")):continue
                if not (p.parent / target.split("#", 1)[0]).exists():
                    raise ValueError(f"{p}: missing link {target}")
            for script in re.findall(r"(?<![\w/])scripts/[a-z0-9_./-]+\.py", text):
                if not (root / script).is_file():
                    # The connection script is optional in task Skills, never a hidden dependency.
                    if script != "scripts/ielts_buddy_api.py":
                        raise ValueError(f"{p}: missing script {script}")
    methods = manifest["workflows"]
    assert len({item["id"] for item in methods}) == len(methods)
    assert {item["path"] for item in methods} == {p.relative_to(ROOT).as_posix() for p in SKILLS.glob("*/references/*/WORKFLOW.md")}
    for item in methods:
        assert item["skillId"] in listed and item["path"].startswith(f"skills/{item['skillId']}/")
    for p in tracked_and_new():
        if p.name == ".DS_Store" or p.suffix.lower() in {".pdf", ".doc", ".docx"}:
            raise ValueError(f"forbidden file: {p}")
        if p.suffix.lower() in {".md", ".json", ".yaml", ".py", ".txt"} and p.name != "validate_skills.py":
            value = p.read_text()
            for pattern in FORBIDDEN_TEXT:
                if pattern.search(value):raise ValueError(f"forbidden text in {p}: {pattern.pattern}")
    print(f"validated {len(listed)} standalone Skills, {len(methods)} methods, {len(operation_names)} public operations")


if __name__ == "__main__":
    validate()
