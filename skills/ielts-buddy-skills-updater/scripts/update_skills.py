#!/usr/bin/env python3
"""Transactionally update IELTS Buddy learner Skills from the fixed OSS source."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import zipfile


PROJECT = "ielts-buddy-agent-skills"
SCHEMA_VERSION = "1.0.0"
PUBLIC_BASE_URL = "https://ieltsbuddy-content.oss-cn-hangzhou.aliyuncs.com"
OBJECT_PREFIX = "learner-skills"
DEFAULT_LATEST_URL = f"{PUBLIC_BASE_URL}/{OBJECT_PREFIX}/latest.json"
RELEASE_STATE = ".ielts-buddy-agent-release.json"
ARCHIVE_ROOT = f"{PROJECT}/"
UPDATER_SKILL = "ielts-buddy-skills-updater"
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class UpdateError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_https(value: str, allow_file_url: bool) -> None:
    scheme = urlparse(value).scheme.lower()
    if scheme == "https" or (allow_file_url and scheme == "file"):
        return
    raise UpdateError("更新源和 ZIP 必须使用 HTTPS")


def download_json(url: str, allow_file_url: bool) -> dict[str, Any]:
    require_https(url, allow_file_url)
    request = Request(url, headers={"User-Agent": "ielts-buddy-skills-updater/1.0"})
    with urlopen(request, timeout=30) as response:
        payload = response.read()
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UpdateError("latest.json 不是有效 UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise UpdateError("latest.json 顶层必须是对象")
    return value


def validate_skill_ids(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise UpdateError("Manifest 缺少 Skills 清单")
    if any(not isinstance(item, str) or not SKILL_NAME_PATTERN.fullmatch(item) for item in value):
        raise UpdateError("Manifest 包含非法 Skill ID")
    if len(value) != len(set(value)):
        raise UpdateError("Manifest 包含重复 Skill ID")
    if UPDATER_SKILL not in value:
        raise UpdateError("Manifest 缺少内置更新 Skill")
    return sorted(value)


def validate_manifest(manifest: dict[str, Any], allow_file_url: bool) -> list[str]:
    if manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("project") != PROJECT:
        raise UpdateError("Manifest 项目或格式无效")
    commit = manifest.get("source_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise UpdateError("Manifest commit 无效")
    if not isinstance(manifest.get("version"), str) or not re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]):
        raise UpdateError("Manifest 版本无效")
    if manifest.get("preview") is not False:
        raise UpdateError("拒绝安装预览发行包")
    skills = validate_skill_ids(manifest.get("skills"))
    archive = manifest.get("archive")
    if not isinstance(archive, dict) or not isinstance(archive.get("url"), str):
        raise UpdateError("Manifest 缺少 ZIP URL")
    require_https(archive["url"], allow_file_url)
    if not allow_file_url:
        expected = f"{PUBLIC_BASE_URL}/{OBJECT_PREFIX}/releases/{commit}/{PROJECT}.zip"
        if archive["url"] != expected:
            raise UpdateError("Manifest ZIP 不在固定 OSS 发行路径")
    if not isinstance(archive.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", archive["sha256"]):
        raise UpdateError("Manifest ZIP SHA-256 无效")
    if not isinstance(archive.get("size_bytes"), int) or archive["size_bytes"] <= 0:
        raise UpdateError("Manifest ZIP 大小无效")
    return skills


def read_json_file(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UpdateError(f"本地版本标记损坏: {path}") from exc
    if not isinstance(value, dict):
        raise UpdateError(f"本地版本标记不是对象: {path}")
    return value


def validate_state(state: dict[str, Any]) -> list[str]:
    if state.get("schema_version") != SCHEMA_VERSION or state.get("project") != PROJECT:
        raise UpdateError("本地版本标记的项目或格式无效")
    commit = state.get("source_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise UpdateError("本地版本标记 commit 无效")
    return validate_skill_ids(state.get("managed_skills"))


def read_local_state(target: Path) -> tuple[dict[str, Any] | None, list[str]]:
    state = read_json_file(target / RELEASE_STATE)
    if state is None:
        state = read_json_file(target / UPDATER_SKILL / RELEASE_STATE)
    return (state, validate_state(state)) if state is not None else (None, [])


def download_archive(manifest: dict[str, Any], destination: Path, allow_file_url: bool) -> None:
    archive = manifest["archive"]
    require_https(archive["url"], allow_file_url)
    request = Request(archive["url"], headers={"User-Agent": "ielts-buddy-skills-updater/1.0"})
    with urlopen(request, timeout=120) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output, length=1024 * 1024)
    if destination.stat().st_size != archive["size_bytes"]:
        raise UpdateError("ZIP 下载大小与 Manifest 不一致")
    if sha256_file(destination) != archive["sha256"]:
        raise UpdateError("ZIP SHA-256 校验失败")


def safe_destination(root: Path, relative: PurePosixPath) -> Path:
    candidate = root.joinpath(*relative.parts)
    resolved_parent = candidate.parent.resolve()
    resolved_root = root.resolve()
    if resolved_root != resolved_parent and resolved_root not in resolved_parent.parents:
        raise UpdateError(f"ZIP 路径越界: {relative}")
    return candidate


def extract_archive(archive_path: Path, staging: Path) -> Path:
    project_root = staging / PROJECT
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive.infolist():
            name = info.filename
            if not name.startswith(ARCHIVE_ROOT):
                raise UpdateError(f"ZIP 包含意外根目录: {name}")
            relative_text = name[len(ARCHIVE_ROOT):].rstrip("/")
            if not relative_text:
                continue
            relative = PurePosixPath(relative_text)
            if relative.is_absolute() or ".." in relative.parts or "\\" in relative_text:
                raise UpdateError(f"ZIP 包含非法路径: {name}")
            mode = (info.external_attr >> 16) & 0xFFFF
            if (mode & 0o170000) == 0o120000:
                raise UpdateError(f"ZIP 不允许符号链接: {name}")
            destination = safe_destination(project_root, relative)
            if info.is_dir() or name.endswith("/"):
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, destination.open("wb") as output:
                shutil.copyfileobj(source, output)
            if mode:
                os.chmod(destination, mode & 0o777)
    return project_root


def validate_extracted(project_root: Path, manifest: dict[str, Any], skill_ids: list[str]) -> dict[str, Any]:
    state = read_json_file(project_root / RELEASE_STATE)
    if state is None:
        raise UpdateError("ZIP 缺少版本标记")
    state_skills = validate_state(state)
    if state["source_commit"] != manifest["source_commit"] or state.get("version") != manifest["version"]:
        raise UpdateError("ZIP 版本标记与 Manifest 不一致")
    if state.get("preview") is not False:
        raise UpdateError("拒绝安装预览发行包")
    if state_skills != skill_ids:
        raise UpdateError("ZIP 版本标记与 Skills 清单不一致")
    repository_manifest = read_json_file(project_root / "manifest.json")
    if repository_manifest is None:
        raise UpdateError("ZIP 缺少仓库 manifest.json")
    repository_ids = sorted(item.get("id") for item in repository_manifest.get("skills", []) if isinstance(item, dict))
    if repository_manifest.get("version") != manifest["version"] or repository_ids != skill_ids:
        raise UpdateError("ZIP 仓库清单与发行版本不一致")
    for skill_id in skill_ids:
        skill_dir = project_root / "skills" / skill_id
        for relative in ("SKILL.md", "manifest.json", "agents/openai.yaml"):
            if not (skill_dir / relative).is_file():
                raise UpdateError(f"ZIP 缺少 {skill_id}/{relative}")
    return state


def default_skills_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_target(args: argparse.Namespace) -> Path:
    return Path(args.target).expanduser().resolve() if args.target else default_skills_root()


def ensure_consumer_target(target: Path) -> None:
    if not target.is_dir():
        raise UpdateError(f"Skills 根目录不存在: {target}")
    if (target / ".git").exists() or (target.parent / ".git").exists():
        raise UpdateError("目标属于 Git 维护者仓库；请使用 GitHub 发布流程")


def fetch_manifest(args: argparse.Namespace) -> tuple[dict[str, Any], list[str]]:
    manifest = download_json(args.latest_url, args.allow_file_url)
    return manifest, validate_manifest(manifest, args.allow_file_url)


def missing_skills(target: Path, skill_ids: list[str]) -> list[str]:
    return [skill_id for skill_id in skill_ids if not (target / skill_id / "SKILL.md").is_file()]


def command_check(args: argparse.Namespace) -> None:
    target = resolve_target(args)
    ensure_consumer_target(target)
    manifest, skill_ids = fetch_manifest(args)
    local, _ = read_local_state(target)
    missing = missing_skills(target, skill_ids)
    current_commit = local.get("source_commit") if local else None
    status = "current" if current_commit == manifest["source_commit"] and not missing else "update-available"
    print(json.dumps({
        "status": status,
        "currentCommit": current_commit,
        "currentVersion": local.get("version") if local else None,
        "latestCommit": manifest["source_commit"],
        "latestVersion": manifest["version"],
        "missingSkills": missing,
        "managedSkillCount": len(skill_ids),
    }, ensure_ascii=False, indent=2))


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def replace_managed(target: Path, project_root: Path, skill_ids: list[str], state: dict[str, Any]) -> None:
    backup = Path(tempfile.mkdtemp(prefix="ielts-buddy-skills-backup-"))
    moved: list[str] = []
    state_backup = backup / RELEASE_STATE
    try:
        for skill_id in skill_ids:
            source = project_root / "skills" / skill_id
            if not source.is_dir():
                raise UpdateError(f"发行包缺少 Skill 目录: {skill_id}")
            destination = target / skill_id
            if destination.exists() or destination.is_symlink():
                shutil.move(str(destination), str(backup / skill_id))
            shutil.copytree(source, destination, symlinks=False)
            moved.append(skill_id)
        local_state = target / RELEASE_STATE
        if local_state.exists() or local_state.is_symlink():
            shutil.move(str(local_state), str(state_backup))
        local_state.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception:
        for skill_id in reversed(moved):
            destination = target / skill_id
            remove_path(destination)
            old = backup / skill_id
            if old.exists() or old.is_symlink():
                shutil.move(str(old), str(destination))
        local_state = target / RELEASE_STATE
        remove_path(local_state)
        if state_backup.exists() or state_backup.is_symlink():
            shutil.move(str(state_backup), str(local_state))
        raise
    finally:
        shutil.rmtree(backup, ignore_errors=True)


def command_update(args: argparse.Namespace) -> None:
    target = resolve_target(args)
    ensure_consumer_target(target)
    manifest, skill_ids = fetch_manifest(args)
    with tempfile.TemporaryDirectory(prefix="ielts-buddy-skills-update-") as value:
        staging = Path(value)
        archive_path = staging / f"{PROJECT}.zip"
        download_archive(manifest, archive_path, args.allow_file_url)
        project_root = extract_archive(archive_path, staging)
        state = validate_extracted(project_root, manifest, skill_ids)
        local, _ = read_local_state(target)
        replace_managed(target, project_root, skill_ids, state)
    print(json.dumps({
        "status": "updated",
        "previousCommit": local.get("source_commit") if local else None,
        "sourceCommit": state["source_commit"],
        "version": state["version"],
        "managedSkillCount": len(skill_ids),
    }, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Update IELTS Buddy learner Skills from OSS")
    parser.add_argument("command", choices=("check", "update"))
    parser.add_argument("--target", help=argparse.SUPPRESS)
    parser.add_argument("--latest-url", default=DEFAULT_LATEST_URL, help=argparse.SUPPRESS)
    parser.add_argument("--allow-file-url", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        command_check(args) if args.command == "check" else command_update(args)
        return 0
    except UpdateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
