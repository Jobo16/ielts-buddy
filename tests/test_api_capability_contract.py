from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_BASE_URL = "https://work.ieltsbuddy.igopx.cn/api/v1/agent"
BINDING_PAGE = "https://work.ieltsbuddy.igopx.cn/agent/bind"
TOOL_PATTERN = re.compile(
    r"\bielts_(?:footprints|learner|learning|mock|practice|prep|resources|speaking|study_plans|vocabulary|writing)_[a-z0-9_]+\b"
)


class AgentApiCapabilityContractTest(unittest.TestCase):
    def test_repository_manifest_points_to_a_bundled_api_script(self) -> None:
        script = ROOT / "scripts" / "ielts_buddy_api.py"
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(script.is_file())
        text = script.read_text(encoding="utf-8")
        self.assertIn(API_BASE_URL, text)
        self.assertIn("IELTS_BUDDY_TOKEN", text)
        self.assertIn("bind", text)
        self.assertEqual(manifest["binding"]["page"], BINDING_PAGE)

    def test_each_skill_has_a_self_contained_api_script(self) -> None:
        skill_dirs = sorted((ROOT / "skills").iterdir())
        self.assertEqual(len(skill_dirs), 8)
        scripts = [ROOT / "scripts" / "ielts_buddy_api.py"]
        scripts.extend(skill_dir / "scripts" / "ielts_buddy_api.py" for skill_dir in skill_dirs)
        for script in scripts:
            skill_dir = script.parent.parent
            script = skill_dir / "scripts" / "ielts_buddy_api.py"
            self.assertTrue(script.is_file(), skill_dir.name)
            text = script.read_text(encoding="utf-8")
            self.assertIn(API_BASE_URL, text, skill_dir.name)
            self.assertIn("IELTS_BUDDY_TOKEN", text, skill_dir.name)
            self.assertIn("bind", text, skill_dir.name)
            self.assertIn("binding_endpoint", text, skill_dir.name)
            self.assertIn("page_url = data.get(\"bindingUrl\")", text, skill_dir.name)
            self.assertNotIn("request(binding_url", text, skill_dir.name)
            self.assertNotIn("path.parent.chmod", text, skill_dir.name)
            self.assertNotIn("/mcp", text, skill_dir.name)

    def test_setup_guides_share_the_canonical_api_origin(self) -> None:
        for path in sorted((ROOT / "skills").glob("*/references/setup.md")):
            text = path.read_text(encoding="utf-8")
            self.assertIn(API_BASE_URL, text, path.relative_to(ROOT).as_posix())
            self.assertIn("scripts/ielts_buddy_api.py", text, path.relative_to(ROOT).as_posix())
            self.assertIn("bind", text, path.relative_to(ROOT).as_posix())
            self.assertNotIn("/mcp", text, path.relative_to(ROOT).as_posix())
            self.assertNotIn("OAuth", text, path.relative_to(ROOT).as_posix())

    def test_markdown_references_only_published_api_operations(self) -> None:
        contract = json.loads(
            (ROOT / "contracts" / "ielts-buddy-api-operations.json").read_text(encoding="utf-8")
        )
        published = set(contract["tools"])
        references: dict[str, set[str]] = {}

        for path in sorted((ROOT / "skills").rglob("*.md")):
            names = set(TOOL_PATTERN.findall(path.read_text(encoding="utf-8")))
            unknown = names - published
            if unknown:
                references[path.relative_to(ROOT).as_posix()] = unknown

        self.assertEqual(references, {})
        self.assertIn("ielts_vocabulary_personal_import", published)
        self.assertIn("ielts_vocabulary_personal_export", published)

    def test_feedback_handoffs_require_confirmation_and_source_evidence(self) -> None:
        cases = [
            (
                "skills/ielts-writing-review/references/vocabulary-handoff.md",
                "writing_review",
                "3–5",
            ),
            (
                "skills/ielts-speaking-coach/references/vocabulary-handoff.md",
                "speaking_feedback",
                "2–4",
            ),
        ]
        for relative_path, source_type, candidate_count in cases:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("明确", text)
            self.assertIn("确认", text)
            self.assertIn(candidate_count, text)
            self.assertIn("ielts_vocabulary_personal_add", text)
            self.assertIn(f"sourceType: {source_type}", text)
            self.assertNotIn("ielts_vocabulary_add", text)

    def test_review_workflows_route_to_the_handoff_contract(self) -> None:
        writing_skill = (ROOT / "skills/ielts-writing-review/SKILL.md").read_text(encoding="utf-8")
        speaking_skill = (ROOT / "skills/ielts-speaking-coach/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/vocabulary-handoff.md", writing_skill)
        self.assertIn("references/vocabulary-handoff.md", speaking_skill)

        for workflow in [
            "skills/ielts-writing-review/workflows/ielts-task1-review/WORKFLOW.md",
            "skills/ielts-writing-review/workflows/ielts-task2-review/WORKFLOW.md",
            "skills/ielts-speaking-coach/workflows/speaking-coach/WORKFLOW.md",
        ]:
            text = (ROOT / workflow).read_text(encoding="utf-8")
            self.assertIn("vocabulary-handoff.md", text)
            self.assertIn("ielts_vocabulary_personal_add", text)


if __name__ == "__main__":
    unittest.main()
