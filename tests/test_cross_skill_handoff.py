import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class CrossSkillHandoffTest(unittest.TestCase):
    def test_method_is_bundled_and_uses_current_review_api(self):
        skill = ROOT / "skills/ielts-study-plan"
        method = (skill / "references/evidence-to-next-action/WORKFLOW.md").read_text()
        self.assertIn("evidence-to-next-action/WORKFLOW.md", (skill / "SKILL.md").read_text())
        self.assertIn("ielts_review_read_snapshot", method)
        self.assertIn("ielts_study_todos_create", method)
        self.assertNotIn("ielts_practice_read_review", method)

if __name__ == "__main__": unittest.main()
