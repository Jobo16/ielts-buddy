import json
from io import BytesIO
from urllib.error import HTTPError
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import importlib.util
spec = importlib.util.spec_from_file_location("ielts_buddy_api", Path(__file__).resolve().parents[1] / "skills/ielts-buddy/scripts/ielts_buddy_api.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
derive_binding_url, load_token, request, save_token = module.derive_binding_url, module.load_token, module.request, module.save_token


class ApiClientHelpersTest(unittest.TestCase):
    def test_footprint_cursor_and_independent_statistics_are_preserved(self):
        body = {
            "code": 0,
            "message": "ok",
            "data": {
                "activities": [{"id": "course:1"}],
                "total": 627,
                "hasMore": True,
                "nextCursor": "next-opaque-cursor",
                "summary": {"weekActivityCount": 622},
                "dailyCounts": [{"date": "2026-09-07", "count": 620}],
                "coverage": {"sourceLimit": None, "sourceTruncated": False},
            },
        }
        with patch.object(module.http, "open") as urlopen:
            urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(body).encode()
            result = request("https://example.com/api/v1/agent", "/capabilities/ielts_footprints_list", "fixture-token",
                             {"cursor": "opaque-cursor", "kinds": ["study"], "limit": 20})
            sent = urlopen.call_args.args[0]
            self.assertEqual(json.loads(sent.data), {"cursor": "opaque-cursor", "kinds": ["study"], "limit": 20})
            self.assertEqual(result, body)

    def test_personal_practice_key_is_sent(self):
        body = {"code": 0, "message": "ok", "data": {"status": "queued"}}
        with patch.object(module.http, "open") as open_http:
            open_http.return_value.__enter__.return_value.read.return_value = json.dumps(body).encode()
            request(module.DEFAULT_BASE_URL, "/capabilities/ielts_practice_create_part", "fixture-token",
                    {"title": "Example"}, idempotency_key="practice-request-42")
            self.assertEqual(open_http.call_args.args[0].get_header("Idempotency-key"), "practice-request-42")

    def test_rejects_redirects_and_unsuccessful_json(self):
        with patch.object(module.http, "open", side_effect=HTTPError(
            "https://example.com/resource", 302, "Found", {}, BytesIO(b"")
        )) as open_http:
            with self.assertRaisesRegex(SystemExit, "重定向"):
                request(module.DEFAULT_BASE_URL, "/me", "fixture-token")
            self.assertEqual(open_http.call_count, 1)
        with patch.object(module.http, "open") as open_http:
            open_http.return_value.__enter__.return_value.read.return_value = b'{"code":40001,"data":null}'
            with self.assertRaisesRegex(SystemExit, "未返回成功"):
                request(module.DEFAULT_BASE_URL, "/me", "fixture-token")

    def test_custom_api_never_inherits_default_token_file(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            token_file = Path(directory) / "default-token"
            token_file.write_text("default-token")
            with patch.object(module, "TOKEN_FILE", token_file):
                self.assertEqual(load_token(), "default-token")
                self.assertIsNone(load_token("https://staging.example.com/api/v1/agent"))
                with self.assertRaises(SystemExit):
                    save_token("staging-token", "https://staging.example.com/api/v1/agent")
                self.assertEqual(token_file.read_text(), "default-token")

    def test_derive_binding_url_from_default_agent_url(self):
        self.assertEqual(
            derive_binding_url("https://example.com/api/v1/agent"),
            "https://example.com/api/v1/agent-bindings",
        )

    def test_derive_binding_url_without_api_version(self):
        self.assertEqual(
            derive_binding_url("https://example.com/agent"),
            "https://example.com/agent/agent-bindings",
        )

    def test_save_and_load_token_uses_configured_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            token_file = Path(tmp) / "agent-token"
            with patch.dict(os.environ, {"IELTS_BUDDY_TOKEN_FILE": str(token_file)}, clear=False):
                save_token("secret-token")
                self.assertEqual(load_token(), "secret-token")
                self.assertEqual(token_file.read_text(encoding="utf-8"), "secret-token\n")

    def test_environment_token_takes_precedence(self):
        with tempfile.TemporaryDirectory() as tmp:
            token_file = Path(tmp) / "agent-token"
            token_file.write_text("file-token\n", encoding="utf-8")
            with patch.dict(
                os.environ,
                {
                    "IELTS_BUDDY_TOKEN_FILE": str(token_file),
                    "IELTS_BUDDY_TOKEN": "environment-token",
                },
                clear=False,
            ):
                self.assertEqual(load_token(), "environment-token")


if __name__ == "__main__":
    unittest.main()
