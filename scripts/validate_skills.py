#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THIS_FILE = Path(__file__).resolve()
SKILLS_DIR = ROOT / "skills"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
LOCAL_CODE_PATH_PATTERN = re.compile(r"`((?:\.\.?/|references/|scripts/|workflows/)[^`\s]+)`")
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".txt"}
FORBIDDEN_SUFFIXES = {".pdf", ".doc", ".docx"}
FORBIDDEN_NAMES = {".DS_Store"}
FORBIDDEN_TEXT_PATTERNS = [
    re.compile(r"/Users/"),
    re.compile(r"\bDownloads\b"),
    re.compile(r"\bC1[5-9]T\d\b"),
    re.compile(r"\bCambridge IELTS\b", re.IGNORECASE),
]


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError(f"{path}: unclosed YAML frontmatter")
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, separator, value = line.partition(":")
        if not separator or not key.strip() or not value.strip():
            raise ValueError(f"{path}: invalid frontmatter line: {line}")
        fields[key.strip()] = value.strip().strip('"')
    return fields


def validate_skill(skill_dir: Path) -> dict[str, object]:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        raise ValueError(f"{skill_dir}: missing SKILL.md")
    validate_skill_file(skill_file)

    openai_file = skill_dir / "agents" / "openai.yaml"
    if not openai_file.is_file():
        raise ValueError(f"{skill_dir}: missing agents/openai.yaml")
    fields = parse_frontmatter(skill_file)
    openai_text = openai_file.read_text(encoding="utf-8")
    if f"${fields['name']}" not in openai_text:
        raise ValueError(f"{openai_file}: default_prompt must mention ${fields['name']}")
    skill_manifest = json.loads((skill_dir / "manifest.json").read_text(encoding="utf-8"))
    if skill_manifest.get("id") != fields["name"]:
        raise ValueError(f"{skill_dir}: manifest id must match Skill name")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(skill_manifest.get("version", ""))):
        raise ValueError(f"{skill_dir}: manifest version must be stable semver")
    if skill_manifest.get("audience") != "learner":
        raise ValueError(f"{skill_dir}: manifest audience must be learner")
    for script in ("learning_store.py",):
        if not (skill_dir / "scripts" / script).is_file():
            raise ValueError(f"{skill_dir}: missing scripts/{script}")
    return skill_manifest


def validate_skill_file(skill_file: Path) -> None:
    fields = parse_frontmatter(skill_file)
    if set(fields) != {"name", "description"}:
        raise ValueError(f"{skill_file}: frontmatter must contain only name and description")
    if fields["name"] != skill_file.parent.name:
        raise ValueError(f"{skill_file}: name must match directory")
    if not NAME_PATTERN.fullmatch(fields["name"]):
        raise ValueError(f"{skill_file}: invalid skill name")
    if len(fields["description"]) < 40:
        raise ValueError(f"{skill_file}: description is too short")


def iter_repository_files() -> list[Path]:
    ignored_parts = {".git", "__pycache__", ".pytest_cache"}
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file() and not any(part in ignored_parts for part in path.parts)
    )


def validate_repository_files() -> None:
    forbidden_files = [
        path
        for path in iter_repository_files()
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES
    ]
    if forbidden_files:
        raise ValueError(f"forbidden files: {forbidden_files}")

    for path in iter_repository_files():
        if path.resolve() == THIS_FILE:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(text):
                raise ValueError(f"{path}: forbidden text pattern: {pattern.pattern}")


def validate_markdown_links() -> None:
    for path in iter_repository_files():
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
            target = raw_target.strip("<>")
            if target.startswith(("#", "http://", "https://", "mailto:", "app://")):
                continue
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            if not (path.parent / target_path).exists():
                raise ValueError(f"{path}: missing markdown target: {target}")


def validate_local_code_paths() -> None:
    for path in iter_repository_files():
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for target in LOCAL_CODE_PATH_PATTERN.findall(text):
            target_path = target.rstrip(".,;:")
            if not (path.parent / target_path).exists():
                raise ValueError(f"{path}: missing local code path: {target}")


def validate_workflows(skill_dirs: list[Path]) -> int:
    workflow_count = 0
    for skill_dir in skill_dirs:
        workflows_dir = skill_dir / "workflows"
        workflow_files = sorted(workflows_dir.glob("*/WORKFLOW.md")) if workflows_dir.is_dir() else []
        if not workflow_files:
            raise ValueError(f"{skill_dir}: missing workflows")
        nested_skill_files = sorted(workflows_dir.rglob("SKILL.md"))
        if nested_skill_files:
            raise ValueError(f"{skill_dir}: internal workflows must use WORKFLOW.md: {nested_skill_files}")
        router = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        for workflow_file in workflow_files:
            text = workflow_file.read_text(encoding="utf-8")
            if text.startswith("---\n") or not text.startswith("# "):
                raise ValueError(f"{workflow_file}: internal workflow must start with one H1 and no frontmatter")
            target = workflow_file.relative_to(skill_dir).as_posix()
            if target not in router:
                raise ValueError(f"{workflow_file}: workflow is not routed from {skill_dir.name}/SKILL.md")
        workflow_count += len(workflow_files)
    return workflow_count


def validate_json_files() -> None:
    for path in iter_repository_files():
        if path.suffix.lower() == ".json":
            json.loads(path.read_text(encoding="utf-8"))


def validate_repository_manifest(manifest: dict[str, object], skill_manifests: dict[str, dict[str, object]]) -> None:
    if manifest.get("schemaVersion") != 1:
        raise ValueError("repository manifest must use schemaVersion 1")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version", ""))):
        raise ValueError("repository manifest version must be stable semver")
    entries = manifest.get("skills")
    if not isinstance(entries, list):
        raise ValueError("repository manifest skills must be an array")
    manifest_skill_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("repository manifest skill entry must be an object")
        skill_id = entry.get("id")
        if skill_id not in skill_manifests:
            raise ValueError(f"repository manifest has unknown skill: {skill_id}")
        if skill_id in manifest_skill_ids:
            raise ValueError(f"repository manifest has duplicate skill: {skill_id}")
        manifest_skill_ids.add(skill_id)
        expected_path = f"skills/{skill_id}"
        if entry.get("path") != expected_path or entry.get("entry") != f"{expected_path}/SKILL.md":
            raise ValueError(f"repository manifest has invalid paths for {skill_id}")
        for field in ("name", "summary"):
            if not isinstance(entry.get(field), str) or not str(entry[field]).strip():
                raise ValueError(f"repository manifest has incomplete distribution data for {skill_id}")


def validate_python_scripts() -> None:
    for path in sorted((ROOT / "skills").rglob("*.py")):
        result = subprocess.run(
            [sys.executable, str(path), "--help"],
            cwd=path.parent,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise ValueError(f"{path}: --help failed: {result.stderr.strip()}")


def main() -> None:
    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    if not skill_dirs:
        raise ValueError("no skills found")
    skill_files = sorted(SKILLS_DIR.rglob("SKILL.md"))
    for skill_file in skill_files:
        validate_skill_file(skill_file)
    skill_manifests = {skill_dir.name: validate_skill(skill_dir) for skill_dir in skill_dirs}

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    manifest_skills = {item["id"] for item in manifest["skills"]}
    directory_skills = {path.name for path in skill_dirs}
    if manifest_skills != directory_skills:
        raise ValueError("manifest skills do not match skills directory")
    validate_repository_manifest(manifest, skill_manifests)

    validate_repository_files()
    validate_json_files()
    validate_markdown_links()
    validate_local_code_paths()
    workflow_count = validate_workflows(skill_dirs)
    validate_python_scripts()
    print(
        f"validated {len(skill_dirs)} top-level skill(s), "
        f"{len(skill_files)} skill file(s), {workflow_count} workflow(s)"
    )


if __name__ == "__main__":
    main()
