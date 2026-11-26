#!/usr/bin/env python3
"""Build the checked archive and update manifest for a GitHub Release."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any
import zipfile


PROJECT = "ielts-buddy-agent-skills"
SCHEMA_VERSION = "1.0.0"
RELEASES_URL = "https://github.com/Jobo16/ielts-buddy/releases"
RELEASE_STATE = ".ielts-buddy-agent-release.json"
UPDATER_SKILL = "ielts-buddy-skills-updater"


class ReleaseError(RuntimeError):
    pass


def run(command: list[str], cwd: Path, *, capture: bool = True) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "command failed").strip()
        raise ReleaseError(f"{' '.join(command)}: {detail}")
    return (result.stdout or "").strip()


def find_repo_root(value: str | None) -> Path:
    start = Path(value).expanduser().resolve() if value else Path.cwd().resolve()
    for candidate in (start, *start.parents):
        manifest = candidate / "manifest.json"
        if (candidate / ".git").exists() and manifest.is_file():
            try:
                if json.loads(manifest.read_text(encoding="utf-8")).get("name") == PROJECT:
                    return candidate
            except (OSError, json.JSONDecodeError):
                continue
    raise ReleaseError("未找到 IELTS Buddy learner Skills 仓库；请传入 --repo")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def repository_manifest(repo: Path) -> tuple[str, list[str]]:
    try:
        payload = json.loads(run(["git", "show", "HEAD:manifest.json"], repo))
    except (ReleaseError, json.JSONDecodeError) as exc:
        raise ReleaseError("仓库 manifest.json 无效") from exc
    version = payload.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ReleaseError("仓库版本不是稳定语义版本")
    entries = payload.get("skills")
    if not isinstance(entries, list) or not entries:
        raise ReleaseError("仓库清单缺少 Skills")
    skill_ids = sorted(item.get("id") for item in entries if isinstance(item, dict))
    if len(skill_ids) != len(entries) or len(skill_ids) != len(set(skill_ids)):
        raise ReleaseError("仓库 Skills 清单无效")
    if UPDATER_SKILL not in skill_ids:
        raise ReleaseError("发行包缺少内置更新 Skill")
    for skill_id in skill_ids:
        if not isinstance(skill_id, str):
            raise ReleaseError(f"仓库缺少 Skill: {skill_id}")
        run(["git", "cat-file", "-e", f"HEAD:skills/{skill_id}/SKILL.md"], repo)
    return version, skill_ids


def tracked_files(repo: Path) -> list[str]:
    raw = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "-z", "HEAD"],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    paths = [item.decode("utf-8") for item in raw.split(b"\0") if item]
    if not paths:
        raise ReleaseError("当前 commit 没有可发行文件")
    for value in paths:
        path = Path(value)
        if path.is_absolute() or ".." in path.parts or value == RELEASE_STATE:
            raise ReleaseError(f"非法 Git 路径: {value}")
    return paths


def validate_repository(repo: Path, *, ci: bool) -> tuple[str, str, list[str]]:
    commit = run(["git", "rev-parse", "HEAD"], repo)
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ReleaseError("无法读取完整 Git commit")
    if run(["git", "status", "--porcelain=v1", "--untracked-files=all"], repo):
        raise ReleaseError("正式发行前工作区必须干净")
    if not ci:
        if run(["git", "branch", "--show-current"], repo) != "main":
            raise ReleaseError("正式发行只能从 main 构建")
        if run(["git", "rev-parse", "--verify", "origin/main"], repo) != commit:
            raise ReleaseError("HEAD 与 origin/main 不一致；先完成推送再发行")
    version, _ = repository_manifest(repo)
    return commit, version, tracked_files(repo)


def build_release(args: argparse.Namespace) -> Path:
    repo = find_repo_root(args.repo)
    commit, version, paths = validate_repository(repo, ci=args.ci)
    _, skill_ids = repository_manifest(repo)
    published_at = utc_now()
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else repo / ".local-assets" / "distributions" / commit
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"{PROJECT}.zip"
    run([
        "git", "archive", "--format=zip", f"--prefix={PROJECT}/",
        f"--output={archive_path}", "HEAD",
    ], repo)

    state = {
        "schema_version": SCHEMA_VERSION,
        "project": PROJECT,
        "source_commit": commit,
        "version": version,
        "published_at": published_at,
        "preview": bool(args.preview),
        "managed_skills": skill_ids,
    }
    with zipfile.ZipFile(archive_path, "a", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{PROJECT}/{RELEASE_STATE}", json_bytes(state))
        archive.writestr(f"{PROJECT}/skills/{UPDATER_SKILL}/{RELEASE_STATE}", json_bytes(state))

    digest = sha256_file(archive_path)
    archive_url = f"{RELEASES_URL}/download/v{version}/{archive_path.name}"
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "project": PROJECT,
        "source_commit": commit,
        "source_branch": "main",
        "version": version,
        "published_at": published_at,
        "preview": bool(args.preview),
        "tracked_file_count": len(paths),
        "skills": skill_ids,
        "archive": {
            "url": archive_url,
            "sha256": digest,
            "size_bytes": archive_path.stat().st_size,
        },
    }
    (output_dir / "latest.json").write_bytes(json_bytes(manifest))
    (output_dir / "SHA256SUMS").write_text(f"{digest}  {archive_path.name}\n", encoding="utf-8")
    print(json.dumps({"status": "built", "output_dir": str(output_dir), **manifest}, ensure_ascii=False, indent=2))
    return output_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    build = parser.add_subparsers(dest="command", required=True).add_parser(
        "build", help="build a commit-pinned ZIP and manifest",
    )
    build.add_argument("--repo")
    build.add_argument("--output-dir")
    build.add_argument("--preview", action="store_true")
    build.add_argument("--ci", action="store_true", help="allow a detached CI checkout")
    args = parser.parse_args()
    try:
        build_release(args)
    except ReleaseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
