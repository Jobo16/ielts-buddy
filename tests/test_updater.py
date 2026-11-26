import importlib.util
from io import BytesIO
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request


SCRIPT = Path(__file__).resolve().parents[1] / "skills/ielts-buddy-skills-updater/scripts/update_skills.py"
SPEC = importlib.util.spec_from_file_location("ielts_buddy_update_skills", SCRIPT)
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)


class UpdaterRollbackTest(unittest.TestCase):
    def test_copy_failure_restores_existing_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target"
            existing = target / "ielts-buddy"
            existing.mkdir(parents=True)
            (existing / "SKILL.md").write_text("original")
            state = target / updater.RELEASE_STATE
            state.write_text("original state")
            source = root / "source"
            (source / "skills/ielts-buddy").mkdir(parents=True)
            with patch.object(updater.shutil, "copytree", side_effect=OSError("copy failed")):
                with self.assertRaises(OSError):
                    updater.replace_managed(target, source, ["ielts-buddy"], {})
            self.assertEqual((existing / "SKILL.md").read_text(), "original")
            self.assertEqual(state.read_text(), "original state")


class GitHubReleaseSourceTest(unittest.TestCase):
    def test_accepts_versioned_archive_for_this_repo_only(self):
        manifest = {
            "schema_version": updater.SCHEMA_VERSION,
            "project": updater.PROJECT,
            "source_commit": "a" * 40,
            "version": "0.19.0",
            "preview": False,
            "skills": [updater.UPDATER_SKILL, "ielts-buddy"],
            "archive": {
                "url": f"{updater.RELEASES_URL}/download/v0.19.0/{updater.PROJECT}.zip",
                "sha256": "b" * 64,
                "size_bytes": 1000,
            },
        }
        self.assertEqual(updater.validate_manifest(manifest, False), ["ielts-buddy", updater.UPDATER_SKILL])
        for url in (
            manifest["archive"]["url"].replace("v0.19.0", "v0.18.0"),
            manifest["archive"]["url"].replace("Jobo16", "DifferentOwner"),
            f"https://example.com/releases/download/v0.19.0/{updater.PROJECT}.zip",
        ):
            with self.subTest(url=url):
                with self.assertRaisesRegex(updater.UpdateError, "GitHub Release 路径"):
                    updater.validate_manifest({**manifest, "archive": {**manifest["archive"], "url": url}}, False)

    def test_requests_the_latest_manifest_from_github(self):
        with patch.object(updater.release_http, "open", return_value=BytesIO(b'{"preview": false}')) as open_http:
            self.assertEqual(updater.download_json(updater.DEFAULT_LATEST_URL, False), {"preview": False})
            self.assertEqual(
                open_http.call_args.args[0].full_url,
                "https://github.com/Jobo16/ielts-buddy/releases/latest/download/latest.json",
            )

    def test_reports_no_update_manifest_for_older_release(self):
        error = HTTPError(updater.DEFAULT_LATEST_URL, 404, "Not Found", {}, BytesIO(b""))
        with patch.object(updater.release_http, "open", side_effect=error):
            with self.assertRaisesRegex(updater.UpdateError, "尚未附带更新清单"):
                updater.download_json(updater.DEFAULT_LATEST_URL, False)

    def test_redirects_only_to_https_github_release_hosts(self):
        request = Request(updater.DEFAULT_LATEST_URL)
        handler = updater.ReleaseAssetRedirect()
        asset = "https://release-assets.githubusercontent.com/github-production-release-asset/latest.json"
        self.assertEqual(handler.redirect_request(request, None, 302, "Found", {}, asset).full_url, asset)
        for url in (asset.replace("https:", "http:"), "https://example.com/latest.json"):
            with self.subTest(url=url):
                with self.assertRaises(updater.UpdateError):
                    handler.redirect_request(request, None, 302, "Found", {}, url)


if __name__ == "__main__":
    unittest.main()
