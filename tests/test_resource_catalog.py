import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / "workflows" / "common" / "learning-resource-recommender"
CATALOG = WORKFLOW_DIR / "references" / "resources.json"
SCRIPT = ROOT / "scripts" / "workflows" / "learning-resource-recommender" / "extract_learning_resource_catalog.py"


class ResourceCatalogTest(unittest.TestCase):
    def test_catalog_is_structured_and_general_audience(self):
        value = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(value["schemaVersion"], 1)
        self.assertGreaterEqual(len(value["resources"]), 10)
        required = {
            "id", "title", "url", "provider", "description", "skills", "levels",
            "access", "official", "transcript", "exercises", "regionNotes",
        }
        text = CATALOG.read_text(encoding="utf-8").lower()
        for forbidden in ("adult content platform", "literotica.com", "audio.love", "freek.to", "nunflix.org"):
            self.assertNotIn(forbidden, text)
        for resource in value["resources"]:
            self.assertTrue(required.issubset(resource))
            self.assertTrue(resource["url"].startswith("https://"))

    def test_filter_returns_ranked_level_matches(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--skill", "listening", "--level", "B2", "--limit", "4"],
            cwd=WORKFLOW_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["count"], 4)
        self.assertTrue(all("listening" in item["skills"] for item in payload["items"]))
        self.assertTrue(payload["items"][0]["official"])


if __name__ == "__main__":
    unittest.main()
