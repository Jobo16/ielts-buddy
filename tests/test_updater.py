import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


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
            source = root / "source"
            (source / "skills/ielts-buddy").mkdir(parents=True)
            with patch.object(updater.shutil, "copytree", side_effect=OSError("copy failed")):
                with self.assertRaises(OSError):
                    updater.replace_managed(target, source, ["ielts-buddy"], {})
            self.assertEqual((existing / "SKILL.md").read_text(), "original")


if __name__ == "__main__":
    unittest.main()
