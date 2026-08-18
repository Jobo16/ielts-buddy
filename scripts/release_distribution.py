#!/usr/bin/env python3
"""Build and publish commit-pinned IELTS Buddy learner Skills to OSS."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
import zipfile


PROJECT = "ielts-buddy-agent-skills"
SCHEMA_VERSION = "1.0.0"
DEFAULT_PUBLIC_BASE_URL = "https://ieltsbuddy-content.oss-cn-hangzhou.aliyuncs.com"
DEFAULT_OBJECT_PREFIX = "learner-skills"
RELEASE_STATE = ".ielts-buddy-agent-release.json"
UPDATER_SKILL = "ielts-buddy-skills-updater"
ENV_PREFIX = "USER_ASSET_OSS_"
ENV_KEYS = {
    "bucket": f"{ENV_PREFIX}BUCKET",
    "access_key_id": f"{ENV_PREFIX}ACCESS_KEY_ID",
    "access_key_secret": f"{ENV_PREFIX}ACCESS_KEY_SECRET",
    "role_arn": f"{ENV_PREFIX}ROLE_ARN",
    "sts_endpoint": f"{ENV_PREFIX}STS_ENDPOINT",
    "endpoint": f"{ENV_PREFIX}ENDPOINT",
    "region": f"{ENV_PREFIX}REGION",
}


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
        raise ReleaseError("发行包缺少内置 OSS 更新 Skill")
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
    object_prefix = args.object_prefix.strip("/")
    public_base = args.public_base_url.rstrip("/")
    release_prefix = f"{object_prefix}/releases/{commit}"
    archive_key = f"{release_prefix}/{PROJECT}.zip"
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
            "key": archive_key,
            "url": f"{public_base}/{quote(archive_key, safe='/')}",
            "stable_key": f"{object_prefix}/{PROJECT}.zip",
            "stable_url": f"{public_base}/{object_prefix}/{PROJECT}.zip",
            "sha256": digest,
            "size_bytes": archive_path.stat().st_size,
        },
        "release_manifest": {
            "key": f"{release_prefix}/manifest.json",
            "url": f"{public_base}/{release_prefix}/manifest.json",
        },
        "latest": {
            "key": f"{object_prefix}/latest.json",
            "url": f"{public_base}/{object_prefix}/latest.json",
        },
    }
    (output_dir / "manifest.json").write_bytes(json_bytes(manifest))
    (output_dir / "SHA256SUMS").write_text(f"{digest}  {archive_path.name}\n", encoding="utf-8")
    print(json.dumps({"status": "built", "output_dir": str(output_dir), **manifest}, ensure_ascii=False, indent=2))
    return output_dir


def load_local_env(repo: Path) -> None:
    path = repo / ".env"
    if not path.is_file():
        return
    allowed = set(ENV_KEYS.values()) | {f"{ENV_PREFIX}ROLE_SESSION_NAME", f"{ENV_PREFIX}SESSION_DURATION_SECONDS"}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in allowed or key in os.environ:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ[key] = value


def normalized_endpoint(value: str) -> str:
    return value if value.startswith(("https://", "http://")) else f"https://{value}"


def endpoint_host(value: str) -> str:
    hostname = urlparse(normalized_endpoint(value)).hostname
    if not hostname:
        raise ReleaseError("STS endpoint 格式无效")
    return hostname


def config_from_env() -> dict[str, str]:
    values = {name: os.environ.get(env_name, "").strip() for name, env_name in ENV_KEYS.items()}
    missing = [ENV_KEYS[name] for name, value in values.items() if not value]
    if missing:
        raise ReleaseError("缺少环境变量: " + ", ".join(missing))
    values["endpoint"] = normalized_endpoint(values["endpoint"])
    values["sts_endpoint"] = normalized_endpoint(values["sts_endpoint"])
    values["region"] = values["region"].removeprefix("oss-")
    return values


def redact(value: str) -> str:
    result = value
    for name in (ENV_KEYS["access_key_id"], ENV_KEYS["access_key_secret"]):
        secret = os.environ.get(name, "")
        if secret:
            result = result.replace(secret, "[REDACTED]")
    return result


def session_policy(bucket: str, key: str) -> str:
    return json.dumps({
        "Version": "1",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "oss:GetObject", "oss:PutObject", "oss:InitiateMultipartUpload",
                "oss:UploadPart", "oss:CompleteMultipartUpload", "oss:AbortMultipartUpload", "oss:ListParts",
            ],
            "Resource": f"acs:oss:*:*:{bucket}/{key}",
        }],
    }, separators=(",", ":"))


def assume_role(config: dict[str, str], policy: str):
    try:
        from alibabacloud_sts20150401.client import Client as StsClient
        from alibabacloud_sts20150401 import models as sts_models
        from alibabacloud_tea_openapi import models as open_api_models
    except ImportError as exc:
        raise ReleaseError("缺少 OSS 发布依赖；安装 scripts/requirements-release.txt") from exc
    duration = min(max(int(os.environ.get(f"{ENV_PREFIX}SESSION_DURATION_SECONDS", "3600")), 900), 3600)
    response = StsClient(open_api_models.Config(
        access_key_id=config["access_key_id"],
        access_key_secret=config["access_key_secret"],
        region_id=config["region"],
        endpoint=endpoint_host(config["sts_endpoint"]),
        protocol="HTTPS",
    )).assume_role(sts_models.AssumeRoleRequest(
        role_arn=config["role_arn"],
        role_session_name=os.environ.get(f"{ENV_PREFIX}ROLE_SESSION_NAME", "ieltsbuddy-learner-release"),
        duration_seconds=duration,
        policy=policy,
    ))
    credentials = response.body.credentials
    if not credentials or not credentials.security_token:
        raise ReleaseError("STS 未返回有效临时凭证")
    return credentials


def oss_client(config: dict[str, str], credentials: Any):
    try:
        import alibabacloud_oss_v2 as oss
    except ImportError as exc:
        raise ReleaseError("缺少 OSS 发布依赖；安装 scripts/requirements-release.txt") from exc
    provider = oss.credentials.StaticCredentialsProvider(
        access_key_id=credentials.access_key_id,
        access_key_secret=credentials.access_key_secret,
        security_token=credentials.security_token,
    )
    sdk_config = oss.config.load_default()
    sdk_config.credentials_provider = provider
    sdk_config.region = config["region"]
    sdk_config.endpoint = config["endpoint"]
    return oss.Client(sdk_config)


def object_sha(client: Any, oss: Any, bucket: str, key: str) -> str | None:
    if not client.is_object_exist(bucket, key):
        return None
    result = client.head_object(oss.HeadObjectRequest(bucket=bucket, key=key))
    return (getattr(result, "metadata", None) or {}).get("sha256")


def upload_file(*, client: Any, oss: Any, uploader: Any, bucket: str, key: str, path: Path, immutable: bool, source_commit: str) -> str:
    digest = sha256_file(path)
    if immutable:
        remote = object_sha(client, oss, bucket, key)
        if remote is not None:
            if remote != digest:
                raise ReleaseError(f"不可变对象已存在但校验值不同: {key}")
            return "unchanged"
    request = oss.PutObjectRequest(
        bucket=bucket,
        key=key,
        content_type=mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        cache_control="public, max-age=31536000, immutable" if immutable else "no-cache, max-age=0",
        forbid_overwrite=immutable,
        metadata={"sha256": digest, "source-commit": source_commit},
    )
    uploader.upload_file(request, str(path))
    return "uploaded"


def verify_public(manifest: dict[str, Any]) -> None:
    latest_url = manifest["latest"]["url"]
    with urlopen(Request(f"{latest_url}?commit={manifest['source_commit']}", headers={"User-Agent": "learner-release/1.0"}), timeout=30) as response:
        latest = json.loads(response.read().decode("utf-8"))
    if latest.get("source_commit") != manifest["source_commit"]:
        raise ReleaseError("公开 latest.json 与刚发布的 commit 不一致")
    for url in (manifest["archive"]["url"], manifest["archive"]["stable_url"]):
        with urlopen(Request(url, method="HEAD", headers={"User-Agent": "learner-release/1.0"}), timeout=30) as response:
            size = response.headers.get("Content-Length")
            digest = response.headers.get("x-oss-meta-sha256")
        if size and int(size) != manifest["archive"]["size_bytes"]:
            raise ReleaseError("公开 ZIP 大小与 Manifest 不一致")
        if digest != manifest["archive"]["sha256"]:
            raise ReleaseError("公开 ZIP SHA-256 与 Manifest 不一致")


def publish_release(args: argparse.Namespace) -> dict[str, Any]:
    repo = find_repo_root(args.repo)
    commit = run(["git", "rev-parse", "HEAD"], repo)
    build_dir = Path(args.build_dir).expanduser().resolve()
    manifest_path = build_dir / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"缺少有效构建产物: {manifest_path}") from exc
    if manifest.get("project") != PROJECT or manifest.get("schema_version") != SCHEMA_VERSION:
        raise ReleaseError("Manifest 项目或格式无效")
    if manifest.get("preview") or manifest.get("source_commit") != commit:
        raise ReleaseError("只能发布当前 HEAD 的正式构建")
    _, skill_ids = repository_manifest(repo)
    files = [
        (build_dir / f"{PROJECT}.zip", manifest["archive"]["key"], True),
        (manifest_path, manifest["release_manifest"]["key"], True),
        (build_dir / "SHA256SUMS", f"{args.object_prefix.strip('/')}/releases/{commit}/SHA256SUMS", True),
        (build_dir / f"{PROJECT}.zip", manifest["archive"]["stable_key"], False),
        (manifest_path, manifest["latest"]["key"], False),
    ]
    if manifest["skills"] != skill_ids:
        raise ReleaseError("构建清单与当前仓库 Skills 不一致")
    for path, _, _ in files:
        if not path.is_file():
            raise ReleaseError(f"缺少构建文件: {path}")
    plan = [{"local_file": str(path), "object_key": key, "immutable": immutable} for path, key, immutable in files]
    if args.dry_run:
        print(json.dumps({"status": "dry-run", "source_commit": commit, "objects": plan}, ensure_ascii=False, indent=2))
        return {"status": "dry-run", "source_commit": commit, "objects": plan}

    load_local_env(repo)
    config = config_from_env()
    credentials = assume_role(config, session_policy(config["bucket"], f"{args.object_prefix.strip('/')}/*"))
    client = oss_client(config, credentials)
    try:
        import alibabacloud_oss_v2 as oss
    except ImportError as exc:
        raise ReleaseError("缺少 OSS 发布依赖；安装 scripts/requirements-release.txt") from exc
    checkpoint = repo / ".local-assets" / "oss-checkpoints" / args.object_prefix.strip("/")
    checkpoint.mkdir(parents=True, exist_ok=True)
    uploader = oss.Uploader(client, parallel_num=3, enable_checkpoint=True, checkpoint_dir=str(checkpoint))
    results = []
    for path, key, immutable in files:
        results.append({
            "object_key": key,
            "status": upload_file(
                client=client, oss=oss, uploader=uploader, bucket=config["bucket"], key=key,
                path=path, immutable=immutable, source_commit=commit,
            ),
        })
    verify_public(manifest)
    result = {"status": "published", "source_commit": commit, "version": manifest["version"], "latest_url": manifest["latest"]["url"], "objects": results}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and publish IELTS Buddy learner Skills to public OSS")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="build a commit-pinned ZIP and manifest")
    build.add_argument("--repo")
    build.add_argument("--output-dir")
    build.add_argument("--public-base-url", default=DEFAULT_PUBLIC_BASE_URL)
    build.add_argument("--object-prefix", default=DEFAULT_OBJECT_PREFIX)
    build.add_argument("--preview", action="store_true")
    build.add_argument("--ci", action="store_true", help="allow a detached CI checkout")
    publish = subparsers.add_parser("publish", help="upload a validated build and update latest last")
    publish.add_argument("--repo")
    publish.add_argument("--build-dir", required=True)
    publish.add_argument("--object-prefix", default=DEFAULT_OBJECT_PREFIX)
    publish.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "build":
        build_release(args)
    else:
        publish_release(args)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReleaseError as exc:
        print(f"error: {redact(str(exc))}", file=sys.stderr)
        raise SystemExit(2)
    except Exception as exc:
        print(f"error: {redact(str(exc))}", file=sys.stderr)
        raise SystemExit(1)
