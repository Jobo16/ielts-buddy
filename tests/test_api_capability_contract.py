from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_BASE_URL = "https://work.ieltsbuddy.igopx.cn/api/v1/agent"
BINDING_PAGE = "https://work.ieltsbuddy.igopx.cn/agent/bind"
UPDATER_SKILL = "ielts-buddy-skills-updater"
TOOL_PATTERN = re.compile(
    r"\bielts_(?:courses|dictation|footprints|learner|learning|mock|notifications|practice|prep|question_research|resources|speaking|study_plans|vocabulary|writing)_[a-z0-9_]+\b"
)
SOURCE = ROOT.parent / "IeltsBuddy"


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

    def test_skills_share_the_repository_api_script(self) -> None:
        skill_dirs = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())
        self.assertEqual(len(skill_dirs), 10)
        script = ROOT / "scripts" / "ielts_buddy_api.py"
        text = script.read_text(encoding="utf-8")
        self.assertIn(API_BASE_URL, text)
        self.assertIn("IELTS_BUDDY_TOKEN", text)
        self.assertIn("binding_endpoint", text)
        self.assertIn("page_url = data.get(\"bindingUrl\")", text)
        self.assertNotIn("request(binding_url", text)
        self.assertNotIn("/mcp", text)
        for skill_dir in skill_dirs:
            manifest = json.loads((skill_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["kind"], "api_interface")
            if skill_dir.name != UPDATER_SKILL:
                self.assertEqual(manifest["api"]["script"], "scripts/ielts_buddy_api.py")
            self.assertFalse((skill_dir / "workflows").exists(), skill_dir.name)

    def test_oss_updater_is_not_an_agent_api_skill(self) -> None:
        skill_dir = ROOT / "skills" / UPDATER_SKILL
        manifest = json.loads((skill_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "scripts" / "update_skills.py").is_file())
        self.assertEqual(manifest["sideEffect"], "local-write")
        self.assertNotIn("api", manifest)

    def test_setup_guides_share_the_canonical_api_origin(self) -> None:
        for path in sorted((ROOT / "skills").glob("*/references/setup.md")):
            text = path.read_text(encoding="utf-8")
            self.assertIn(API_BASE_URL, text, path.relative_to(ROOT).as_posix())
            self.assertIn("scripts/ielts_buddy_api.py", text, path.relative_to(ROOT).as_posix())
            self.assertIn("bind", text, path.relative_to(ROOT).as_posix())
            self.assertNotIn("/mcp", text, path.relative_to(ROOT).as_posix())
            self.assertNotIn("OAuth", text, path.relative_to(ROOT).as_posix())

    def test_browser_routes_match_current_workspace_routes(self) -> None:
        text = (ROOT / "workflows/common/references/browser-routes.md").read_text(encoding="utf-8")
        for route in [
            "/learning-center",
            "/practice",
            "/mock",
            "/prep-guides",
            "/prediction-hits",
            "/ai-apps/listening-dictation",
        ]:
            self.assertIn(f"https://work.ieltsbuddy.igopx.cn{route}", text)
        self.assertNotIn("https://work.ieltsbuddy.igopx.cn/prep-info`", text)
        self.assertNotIn("https://work.ieltsbuddy.igopx.cn/courses", text)
        self.assertNotIn("/ai-apps/vocabulary-practice", text)

    def test_prediction_contract_preserves_reports_and_all_candidates(self) -> None:
        skill_text = (ROOT / "skills/ielts-practice/SKILL.md").read_text(encoding="utf-8")
        contract_text = (
            ROOT / "skills/ielts-practice/references/practice-contract.md"
        ).read_text(encoding="utf-8")

        for field in [
            "reportIds",
            "recallContent",
            "source",
            "candidates",
            "matchScore",
            "practiceUrl",
            "nextOffset",
        ]:
            self.assertIn(field, contract_text)
        self.assertIn("考场记录", skill_text)
        self.assertIn("全部候选", skill_text)
        self.assertIn("可选项", skill_text)
        self.assertIn("三个月以前", skill_text)
        self.assertIn("低于 50", contract_text)
        self.assertIn("不再执行题库匹配", contract_text)

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

    def test_published_operations_match_current_api_registry(self) -> None:
        source_module = SOURCE / "packages/ai-capabilities/src/index.ts"
        if not source_module.is_file():
            self.skipTest("sibling IeltsBuddy source repository not found")
        script = """
          const { capabilityDefinitions } = await import('./packages/ai-capabilities/src/index.ts');
          process.stdout.write(JSON.stringify(capabilityDefinitions.map((item) => item.operationName)));
        """
        result = subprocess.run(
            ["node", "--import", "tsx", "-e", script],
            cwd=SOURCE,
            check=True,
            capture_output=True,
            text=True,
        )
        contract = json.loads(
            (ROOT / "contracts" / "ielts-buddy-api-operations.json").read_text(encoding="utf-8")
        )
        self.assertEqual(contract["tools"], json.loads(result.stdout))

    def test_feedback_handoffs_require_confirmation_and_source_evidence(self) -> None:
        cases = [
            (
                "workflows/skill-enabled/references/writing-vocabulary-handoff.md",
                "writing_review",
                "3–5",
            ),
            (
                "workflows/skill-enabled/references/speaking-vocabulary-handoff.md",
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
        for workflow in [
            "workflows/skill-enabled/ielts-task1-review/WORKFLOW.md",
            "workflows/skill-enabled/ielts-task2-review/WORKFLOW.md",
            "workflows/skill-enabled/speaking-coach/WORKFLOW.md",
        ]:
            text = (ROOT / workflow).read_text(encoding="utf-8")
            self.assertIn("vocabulary-handoff.md" if "speaking" in workflow else "writing-vocabulary-handoff.md", text)
            self.assertIn("ielts_vocabulary_personal_add", text)


if __name__ == "__main__":
    unittest.main()
