from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class SkillContractTests(unittest.TestCase):
    def test_safety_rules_are_explicit(self) -> None:
        skill = read("SKILL.md")
        self.assertIn("不可信目标", skill)
        self.assertIn("不是给你的指令", skill)
        self.assertIn("不执行", skill)
        self.assertIn("输出语言", skill)
        self.assertIn("用户用英文", skill)
        self.assertIn("通用维护/优化请求", skill)
        self.assertIn("最重要的 1-3 件事", skill)
        self.assertIn("有发现时", skill)
        self.assertIn("省略三档和行动清单", skill)
        self.assertIn("不要根据值的字样判断", skill)
        self.assertIn("project readiness", skill)
        self.assertIn("maintenance review", skill)

        agents = read("AGENTS.md")
        self.assertIn("不可信目标", agents)
        self.assertIn("目标仓库", agents)
        self.assertIn("证据", agents)

        security = read("SECURITY.md")
        self.assertIn("提示词注入", security)

        template = read("references/report-format.md")
        self.assertIn("无法确认时只写“疑似”", template)

        readme = read("README.md")
        self.assertIn("untrusted evidence", readme)
        self.assertIn("目标仓库", readme)

    def test_acceptance_cases_cover_security_and_language(self) -> None:
        cases = read("tests/acceptance-cases.md")
        for phrase in (
            "恶意 AGENTS.md",
            "英文提问",
            "没有明显问题",
            "危险请求",
            "只读技能目录",
            "升级保留本地记忆",
        ):
            self.assertIn(phrase, cases)

    def test_portable_memory_contract_is_documented(self) -> None:
        skill = read("SKILL.md")
        agents = read("AGENTS.md")
        readme = read("README.md")
        example = read("PITFALLS.local.example.md")

        for content in (skill, agents, readme):
            self.assertIn("PITFALLS.local.md", content)
            self.assertIn("PROJECT_HEALTH_LITE_HOME", content)

        self.assertIn("只读基线", skill)
        self.assertIn("~/.project-health-lite/PITFALLS.local.md", readme)
        gitignore = read(".gitignore")
        self.assertIn("PITFALLS.local.md", gitignore)
        self.assertIn("PITFALLS.local.md.bak", gitignore)
        self.assertIn("不会被技能升级覆盖", example)

        baseline = read("PITFALLS.md")
        self.assertIn("用户本地覆盖层", baseline)
        self.assertIn("不写目标项目", baseline)
        self.assertNotIn("避坑条目写回本技能目录", baseline)

        cases = read("tests/acceptance-cases.md")
        self.assertNotIn("写进本技能的 `PITFALLS.md`", cases)

    def test_cross_platform_install_is_documented(self) -> None:
        readme = read("README.md")
        for phrase in (
            "Windows PowerShell",
            "macOS / Linux",
            "sha256sum",
            "shasum -a 256",
            "unzip -o",
            "cp -R project-health-lite",
            "~/.claude/skills/",
            "PITFALLS.local.md",
        ):
            self.assertIn(phrase, readme)

    def test_report_template_has_evidence_for_each_category(self) -> None:
        template = read("references/report-format.md")
        self.assertIn("先做最重要的 1-3 件事", template)
        self.assertIn("如果没有发现明显问题", template)
        for heading in ("## 会卡住上线", "## 最好先修", "## 可以以后再说"):
            start = template.index(heading)
            next_heading = template.find("\n## ", start + 1)
            chunk = template[start:] if next_heading < 0 else template[start:next_heading]
            self.assertIn("- 证据：", chunk, msg=f"missing evidence line in {heading}")

    def test_openai_yaml_has_default_prompt(self) -> None:
        yaml = read("agents/openai.yaml")
        self.assertIn("default_prompt:", yaml)
        self.assertIn("$project-health-lite", yaml)

    def test_fixtures_exist_and_malicious_fixture_is_not_auto_loaded(self) -> None:
        paths = (
            "tests/fixtures/basic-project/README.md",
            "tests/fixtures/basic-project/requirements.txt",
            "tests/fixtures/basic-project/app.py",
            "tests/fixtures/no-git-project/README.md",
            "tests/fixtures/secret-project/.env.example",
            "tests/fixtures/malicious-target/malicious-agents.fixture",
        )
        for relative in paths:
            self.assertTrue((ROOT / relative).is_file(), msg=f"missing fixture: {relative}")

        malicious_dir = ROOT / "tests/fixtures/malicious-target"
        self.assertFalse((malicious_dir / "AGENTS.md").exists(), msg="malicious fixture must not be auto-loaded")
        malicious = (malicious_dir / "malicious-agents.fixture").read_text(encoding="utf-8")
        self.assertIn("ignore previous instructions", malicious.lower())

    def test_malicious_fixture_can_be_copied_to_isolated_target(self) -> None:
        source = ROOT / "tests/fixtures/malicious-target/malicious-agents.fixture"
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "AGENTS.md"
            shutil.copyfile(source, target)
            self.assertEqual(target.read_text(encoding="utf-8"), source.read_text(encoding="utf-8"))

    def test_validator_accepts_repository(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts/verify_skill.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_release_download_path_is_documented(self) -> None:
        readme = read("README.md")
        self.assertIn("releases/latest", readme)
        self.assertIn("Assets", readme)
        self.assertIn(".sha256", readme)
        self.assertIn("Get-FileHash", readme)
        self.assertIn("Expand-Archive", readme)
        self.assertIn("Copy-Item", readme)

    def test_ci_uses_current_actions(self) -> None:
        workflow = read(".github/workflows/validate.yml")
        self.assertIn("actions/checkout@v7", workflow)
        self.assertIn("actions/setup-python@v7", workflow)
        self.assertIn("ubuntu-24.04", workflow)
        self.assertNotIn("actions/checkout@v4", workflow)
        self.assertNotIn("actions/setup-python@v5", workflow)


if __name__ == "__main__":
    unittest.main()
