import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ielts_buddy_api import derive_binding_url, load_token, save_token


class ApiClientHelpersTest(unittest.TestCase):
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
