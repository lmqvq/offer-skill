from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)


class OfferSkillScriptsTest(unittest.TestCase):
    def run_cmd(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(args),
            cwd=cwd or ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

    def test_create_case_writes_expected_layout_and_scope_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cases_root = Path(tmp_dir) / "cases"
            result = self.run_cmd(
                str(PYTHON),
                str(ROOT / "scripts" / "create_case.py"),
                "--case-slug",
                "backend-java-social",
                "--display-name",
                "Backend Java Social",
                "--perspective",
                "candidate",
                "--cases-root",
                str(cases_root),
                "--role-title",
                "Backend Engineer",
                "--stack",
                "Java,Redis,MQ",
            )

            case_dir = Path(result.stdout.strip())
            self.assertTrue((case_dir / "meta.json").exists())
            self.assertTrue((case_dir / "manifest.json").exists())
            self.assertTrue((case_dir / "inputs" / "resume.md").exists())
            self.assertTrue((case_dir / "research" / "raw").exists())

            meta = json.loads((case_dir / "meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["perspective"], "candidate")
            self.assertEqual(meta["scope"]["v0_1_enabled_workflows"], ["project-highlight", "resume-eval"])
            self.assertEqual(meta["scope"]["deferred_workflows"], ["mock-interview", "interview-retro"])
            self.assertTrue(meta["scope"]["local_only"])

    def test_version_manager_backup_and_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cases_root = Path(tmp_dir) / "cases"
            self.run_cmd(
                str(PYTHON),
                str(ROOT / "scripts" / "create_case.py"),
                "--case-slug",
                "resume-case",
                "--display-name",
                "Resume Case",
                "--perspective",
                "dual",
                "--cases-root",
                str(cases_root),
            )

            case_dir = cases_root / "resume-case"
            meta_path = case_dir / "meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["lifecycle"]["version"] = "v1"
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

            backup = self.run_cmd(
                str(PYTHON),
                str(ROOT / "scripts" / "version_manager.py"),
                "--action",
                "backup",
                "--case-slug",
                "resume-case",
                "--cases-root",
                str(cases_root),
            )
            self.assertEqual(backup.stdout.strip(), "v1")

            analysis_path = case_dir / "analyses" / "resume_eval.md"
            analysis_path.write_text("new content\n", encoding="utf-8")

            rollback = self.run_cmd(
                str(PYTHON),
                str(ROOT / "scripts" / "version_manager.py"),
                "--action",
                "rollback",
                "--case-slug",
                "resume-case",
                "--cases-root",
                str(cases_root),
                "--version",
                "v1",
            )
            self.assertEqual(rollback.stdout.strip(), "v1")
            restored_meta = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertTrue(restored_meta["lifecycle"]["version"].startswith("v1"))

