#!/usr/bin/env python3
"""Call IELTS Buddy Agent API operations without an Agent API client."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://work.ieltsbuddy.igopx.cn/api/v1/agent"
TOKEN_ENV = "IELTS_BUDDY_TOKEN"
TOKEN_FILE_ENV = "IELTS_BUDDY_TOKEN_FILE"
TOKEN_FILE = Path.home() / ".config" / "ielts-buddy" / "agent-token"
TOKEN_TYPE = "user"


def main() -> int:
    parser = argparse.ArgumentParser(description="Bind an IELTS Buddy account or call REST Agent API operations.")
    parser.add_argument("command", choices=("bind", "me", "capabilities", "call"))
    parser.add_argument("operation", nargs="?", help="Operation name required by call.")
    parser.add_argument("--json", dest="payload", default="{}", help="JSON object, or '-' to read JSON from stdin.")
    parser.add_argument("--client", default=os.environ.get("IELTS_BUDDY_AGENT_NAME", "Local Agent"), help="Name shown on the binding page.")
    parser.add_argument("--base-url", default=os.environ.get("IELTS_BUDDY_API_URL", DEFAULT_BASE_URL))
    args = parser.parse_args()

    if args.command == "bind":
        bind(args.base_url, args.client)
        return 0

    token = load_token()
    if args.command == "me":
        payload = request(args.base_url, "/me", token)
    elif args.command == "capabilities":
        payload = request(args.base_url, "/capabilities", token)
    else:
        if not args.operation:
            parser.error("call requires an operation name")
        payload = request(
            args.base_url,
            f"/capabilities/{quote(args.operation, safe='')}",
            token,
            parse_payload(args.payload),
        )

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def bind(base_url: str, client_name: str) -> None:
    binding_endpoint = os.environ.get("IELTS_BUDDY_BINDING_ENDPOINT", derive_binding_url(base_url))
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
            path = save_token(status["token"])
            print(json.dumps({"status": "bound", "tokenFile": str(path)}, ensure_ascii=False))
            return
        if status.get("status") in {"expired", "used"}:
            raise SystemExit("绑定请求已失效，请重新运行 bind")
        time.sleep(interval)
    raise SystemExit("绑定请求已过期，请重新运行 bind")


def parse_payload(value: str):
    raw = sys.stdin.read() if value == "-" else value
    try:
        return json.loads(raw)
    except json.JSONDecodeError as error:
        raise SystemExit(f"请求 JSON 无效: {error}") from error


def load_token() -> str | None:
    token = os.environ.get(TOKEN_ENV, "").strip()
    if token:
        return token
    path = Path(os.environ.get(TOKEN_FILE_ENV, str(TOKEN_FILE))).expanduser()
    try:
        value = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    return value or None


def save_token(token: str) -> Path:
    path = Path(os.environ.get(TOKEN_FILE_ENV, str(TOKEN_FILE))).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(f"{token}\n", encoding="utf-8")
    path.chmod(0o600)
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


def request(base_url: str, path: str, token: str | None, payload=None):
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=body,
        headers=headers,
        method="POST" if body is not None else "GET",
    )
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace").strip()
        raise SystemExit(f"IELTS Buddy API 返回 HTTP {error.code}: {detail or 'request failed'}") from error
    except URLError as error:
        raise SystemExit(f"无法连接 IELTS Buddy API: {error.reason}") from error
    try:
        return json.loads(raw) if raw else {}
    except json.JSONDecodeError as error:
        raise SystemExit("IELTS Buddy API 返回了非 JSON 响应") from error


if __name__ == "__main__":
    raise SystemExit(main())
