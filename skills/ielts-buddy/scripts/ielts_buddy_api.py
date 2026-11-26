#!/usr/bin/env python3
"""Call IELTS Buddy Agent API operations without an Agent API client."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


DEFAULT_BASE_URL = "https://work.ieltsbuddy.igopx.cn/api/v1/agent"
TOKEN_ENV = "IELTS_BUDDY_TOKEN"
TOKEN_FILE_ENV = "IELTS_BUDDY_TOKEN_FILE"
TOKEN_FILE = Path.home() / ".config" / "ielts-buddy" / "agent-token"
TOKEN_TYPE = "user"
PERSONAL_PRACTICE_OPERATION = "ielts_practice_create_part"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


http = build_opener(NoRedirect())


def main() -> int:
    parser = argparse.ArgumentParser(description="Bind an IELTS Buddy account or call REST Agent API operations.")
    parser.add_argument("command", choices=("bind", "me", "capabilities", "describe", "call"))
    parser.add_argument("operation", nargs="?", help="Operation name for describe or call.")
    parser.add_argument("--json", dest="payload", default="{}", help="JSON object, or '-' to read JSON from stdin.")
    parser.add_argument("--client", default=os.environ.get("IELTS_BUDDY_AGENT_NAME", "Local Agent"), help="Name shown on the binding page.")
    parser.add_argument("--base-url", default=os.environ.get("IELTS_BUDDY_API_URL", DEFAULT_BASE_URL))
    parser.add_argument("--idempotency-key", help="Request key for ielts_practice_create_part. Reuse it only to retry the same exercise.")
    args = parser.parse_args()
    if args.command in {"call", "describe"} and not args.operation:
        parser.error(f"{args.command} requires an operation name")
    if args.idempotency_key is not None and (
        args.command != "call" or args.operation != PERSONAL_PRACTICE_OPERATION
        or re.fullmatch(r"[!-~]{1,128}", args.idempotency_key) is None
    ):
        parser.error("--idempotency-key requires a personal-practice call and 1–128 visible ASCII characters")
    api_origin(args.base_url)

    if args.command == "bind":
        bind(args.base_url, args.client)
        return 0

    if args.command == "me":
        payload = request(args.base_url, "/me", load_token(args.base_url))
    elif args.command == "capabilities":
        payload = request(args.base_url, "/capabilities", None)
    elif args.command == "describe":
        payload = request(args.base_url, f"/capabilities/{quote(args.operation, safe='')}", None)
    else:
        payload = request(
            args.base_url,
            f"/capabilities/{quote(args.operation, safe='')}",
            load_token(args.base_url),
            parse_payload(args.payload),
            idempotency_key=args.idempotency_key,
        )

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def bind(base_url: str, client_name: str) -> None:
    if token_path(base_url) is None:
        raise SystemExit(f"自定义 API 地址绑定前须指定独立的 {TOKEN_FILE_ENV}")
    binding_endpoint = os.environ.get("IELTS_BUDDY_BINDING_ENDPOINT", derive_binding_url(base_url))
    if api_origin(binding_endpoint) != api_origin(base_url):
        raise SystemExit("绑定接口必须与 API 使用同一 origin")
    response = request(binding_endpoint, "", None, {"clientName": client_name, "tokenType": TOKEN_TYPE})
    data = response.get("data", response)
    binding_id = data.get("bindingId")
    secret = data.get("secret")
    page_url = data.get("bindingUrl")
    if not isinstance(binding_id, str) or not isinstance(secret, str) or not isinstance(page_url, str):
        raise SystemExit("绑定服务返回了无效响应")

    print("请打开下面的链接确认绑定当前 IELTS Buddy 账号：")
    print(page_url)
    print("确认后这里会自动继续，不要关闭当前任务。")

    expires_at = parse_time(data.get("expiresAt")) or (time.time() + 600)
    interval = max(1, int(data.get("pollIntervalSeconds", 2)))
    while time.time() < expires_at:
        response = request(binding_endpoint, f"/{quote(binding_id, safe='')}/exchange", None, {"secret": secret})
        status = response.get("data", response)
        if status.get("status") == "bound" and isinstance(status.get("token"), str):
            path = save_token(status["token"], base_url)
            print(json.dumps({"status": "bound", "tokenFile": str(path)}, ensure_ascii=False))
            return
        if status.get("status") in {"expired", "used"}:
            raise SystemExit("绑定请求已失效，请重新运行 bind")
        time.sleep(interval)
    raise SystemExit("绑定请求已过期，请重新运行 bind")


def parse_payload(value: str):
    raw = sys.stdin.read() if value == "-" else value
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as error:
        raise SystemExit(f"请求 JSON 无效: {error}") from error
    if not isinstance(parsed, dict):
        raise SystemExit("请求 JSON 必须是对象")
    return parsed


def api_origin(url: str):
    parsed = urlsplit(url)
    loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"} or (
        parsed.hostname is not None and parsed.hostname.endswith(".localhost")
    )
    if (not parsed.hostname or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment or not (parsed.scheme == "https" or (parsed.scheme == "http" and loopback))):
        raise SystemExit("API 地址必须使用 HTTPS，本机环回开发地址可使用 HTTP")
    return parsed.scheme, parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80)


def token_path(base_url: str) -> Path | None:
    configured = os.environ.get(TOKEN_FILE_ENV)
    if configured:
        return Path(configured).expanduser()
    return TOKEN_FILE if api_origin(base_url) == api_origin(DEFAULT_BASE_URL) else None


def load_token(base_url: str = DEFAULT_BASE_URL) -> str | None:
    token = os.environ.get(TOKEN_ENV, "").strip()
    if token:
        return token
    path = token_path(base_url)
    if path is None:
        return None
    try:
        value = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    return value or None


def save_token(token: str, base_url: str = DEFAULT_BASE_URL) -> Path:
    path = token_path(base_url)
    if path is None:
        raise SystemExit(f"须为自定义 API 地址指定 {TOKEN_FILE_ENV}")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(f"{token}\n")
            handle.close()
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    return path


def derive_binding_url(base_url: str) -> str:
    marker = "/api/v1/"
    if marker in base_url:
        return f"{base_url.split(marker, 1)[0]}{marker}agent-bindings"
    return f"{base_url.rstrip('/')}/agent-bindings"


def parse_time(value) -> float | None:
    if not isinstance(value, str):
        return None
    try:
        from datetime import datetime
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def request(base_url: str, path: str, token: str | None, payload=None, *, idempotency_key: str | None = None):
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=body,
        headers=headers,
        method="POST" if body is not None else "GET",
    )
    try:
        with http.open(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as error:
        if 300 <= error.code < 400:
            raise SystemExit(f"IELTS Buddy API 返回重定向 HTTP {error.code}，请核对 API 地址") from error
        detail = error.read().decode("utf-8", errors="replace").strip()
        raise SystemExit(f"IELTS Buddy API 返回 HTTP {error.code}: {detail or 'request failed'}") from error
    except URLError as error:
        raise SystemExit(f"无法连接 IELTS Buddy API: {error.reason}") from error
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as error:
        raise SystemExit("IELTS Buddy API 返回了非 JSON 响应") from error
    if not isinstance(result, dict) or result.get("code") != 0 or "data" not in result:
        raise SystemExit("IELTS Buddy API 未返回成功结果")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
