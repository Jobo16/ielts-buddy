import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "ielts-study-plan"
WORKFLOW = SKILL / "workflows" / "evidence-to-next-action" / "WORKFLOW.md"
REFERENCE = SKILL / "references" / "cross-skill-handoffs.md"


class CrossSkillHandoffTest(unittest.TestCase):
    def test_handoff_is_routed_and_data_only(self):
        router = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        workflow = WORKFLOW.read_text(encoding="utf-8")
        reference = REFERENCE.read_text(encoding="utf-8")

        self.assertIn("workflows/evidence-to-next-action/WORKFLOW.md", router)
        self.assertIn("ielts_practice_read_review", workflow)
        self.assertIn("用户明确确认", workflow)
        self.assertIn('kind="one_time"', workflow)
        self.assertIn("不要调用 `kind=\"structured\"`", reference)
        self.assertIn("不应自动发生的写入", reference)


if __name__ == "__main__":
    unittest.main()
