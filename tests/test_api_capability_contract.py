import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "IeltsBuddy"

class AgentApiCapabilityContractTest(unittest.TestCase):
    def test_installable_skills_have_their_own_entry_and_scripts(self):
        manifest = json.loads((ROOT / "manifest.json").read_text())
        for entry in manifest["skills"]:
            skill = ROOT / entry["path"]
            self.assertTrue((skill / "SKILL.md").is_file())
            self.assertTrue((skill / "agents/openai.yaml").is_file())
        self.assertTrue((ROOT / "skills/ielts-buddy/scripts/ielts_buddy_api.py").is_file())
        self.assertTrue((ROOT / "skills/ielts-buddy-skills-updater/scripts/update_skills.py").is_file())

    def test_current_public_contract_matches_main_source_when_available(self):
        if not (SOURCE / "packages/ai-capabilities/src/index.ts").is_file():
            self.skipTest("main source not checked out")
        script = """const {listCapabilityApiDocumentation}=await import('./packages/ai-capabilities/src/index.ts');process.stdout.write(JSON.stringify(listCapabilityApiDocumentation().map(x=>({id:x.id,operationName:x.operationName,auth:x.auth,scopes:x.scopes,sideEffect:x.sideEffect,requestSchema:x.requestSchema}))));"""
        result = subprocess.run(["node", "--import", "tsx", "-e", script], cwd=SOURCE, capture_output=True, text=True, check=True)
        contract = json.loads((ROOT / "contracts/agent-api-public.json").read_text())
        self.assertEqual(contract["capabilities"], json.loads(result.stdout))

    def test_single_skill_layout_has_no_repository_parent_dependencies(self):
        for skill in (ROOT / "skills").iterdir():
            if not skill.is_dir(): continue
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / skill.name
                import shutil
                shutil.copytree(skill, target)
                self.assertTrue((target / "SKILL.md").is_file())
                for relative in ("references/api-access.md", "scripts/simple_docx.py"):
                    if (skill / relative).exists(): self.assertTrue((target / relative).is_file())

if __name__ == "__main__": unittest.main()
