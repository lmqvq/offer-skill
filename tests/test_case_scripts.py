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
            self.assertEqual(meta["research"]["available_profiles"], ["local-only", "web-assisted", "deep-research"])

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

    def test_import_material_and_run_resume_eval_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cases_root = Path(tmp_dir) / "cases"
            self.run_cmd(
                str(PYTHON),
                str(ROOT / "scripts" / "create_case.py"),
                "--case-slug",
                "resume-eval-case",
                "--display-name",
                "Resume Eval Case",
                "--perspective",
                "candidate",
                "--cases-root",
                str(cases_root),
            )

            resume_src = Path(tmp_dir) / "resume.md"
            jd_src = Path(tmp_dir) / "jd.md"
            projects_src = Path(tmp_dir) / "projects.md"
            resume_src.write_text(
                "# Resume\n"
                "## Experience\n"
                "- Built Java backend services for order processing.\n"
                "- Optimized Redis cache hit rate by 25%.\n"
                "## Skills\n"
                "- Java, Redis, Kafka, MySQL\n",
                encoding="utf-8",
            )
            jd_src.write_text(
                "# Backend Engineer\n"
                "- Required: Strong Java backend development experience\n"
                "- Required: Familiar with Redis and Kafka\n"
                "- Preferred: Experience with distributed systems\n",
                encoding="utf-8",
            )
            projects_src.write_text(
                "# Order Platform\n"
                "- 负责订单服务重构，设计 Redis 缓存方案。\n"
                "- 将核心接口延迟降低 30ms。\n"
                "- 处理高峰流量下的缓存一致性问题。\n",
                encoding="utf-8",
            )

            for material_type, src in (
                ("resume", resume_src),
                ("jd", jd_src),
                ("projects", projects_src),
            ):
                self.run_cmd(
                    str(PYTHON),
                    str(ROOT / "scripts" / "import_material.py"),
                    "--case-slug",
                    "resume-eval-case",
                    "--material-type",
                    material_type,
                    "--cases-root",
                    str(cases_root),
                    "--from-file",
                    str(src),
                )

            workflow = self.run_cmd(
                str(PYTHON),
                str(ROOT / "scripts" / "run_workflow.py"),
                "--case-slug",
                "resume-eval-case",
                "--workflow",
                "resume-eval",
                "--cases-root",
                str(cases_root),
            )

            output_path = Path(workflow.stdout.strip())
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("# Resume Evaluation", content)
            self.assertIn("Overall match", content)
            self.assertTrue((cases_root / "resume-eval-case" / "derived" / "jd_match.json").exists())

    def test_run_project_highlight_and_deferred_workflow_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cases_root = Path(tmp_dir) / "cases"
            self.run_cmd(
                str(PYTHON),
                str(ROOT / "scripts" / "create_case.py"),
                "--case-slug",
                "project-case",
                "--display-name",
                "Project Case",
                "--perspective",
                "dual",
                "--cases-root",
                str(cases_root),
            )

            projects_src = Path(tmp_dir) / "projects.md"
            projects_src.write_text(
                "# Feed Service\n"
                "- 主导 Feed 写入链路重构。\n"
                "- 使用 Redis 降低热点读取延迟 40ms。\n"
                "- 解决高并发场景下的缓存一致性问题。\n",
                encoding="utf-8",
            )

            self.run_cmd(
                str(PYTHON),
                str(ROOT / "scripts" / "import_material.py"),
                "--case-slug",
                "project-case",
                "--material-type",
                "projects",
                "--cases-root",
                str(cases_root),
                "--from-file",
                str(projects_src),
            )

            workflow = self.run_cmd(
                str(PYTHON),
                str(ROOT / "scripts" / "run_workflow.py"),
                "--case-slug",
                "project-case",
                "--workflow",
                "project-highlight",
                "--cases-root",
                str(cases_root),
            )
            output_path = Path(workflow.stdout.strip())
            self.assertTrue(output_path.exists())
            self.assertIn("# Project Highlight", output_path.read_text(encoding="utf-8"))

            deferred = subprocess.run(
                [
                    str(PYTHON),
                    str(ROOT / "scripts" / "run_workflow.py"),
                    "--case-slug",
                    "project-case",
                    "--workflow",
                    "mock-interview",
                    "--cases-root",
                    str(cases_root),
                ],
                cwd=ROOT.parent,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(deferred.returncode, 0)
            self.assertIn("planned after v0.1", deferred.stderr + deferred.stdout)

    def test_deferred_capabilities_are_kept_in_presets_and_docs(self) -> None:
        workflows = json.loads((ROOT / "presets" / "workflows.json").read_text(encoding="utf-8"))
        research_profiles = json.loads((ROOT / "presets" / "research-profiles.json").read_text(encoding="utf-8"))

        self.assertEqual(workflows["mock-interview"]["status"], "planned")
        self.assertFalse(workflows["mock-interview"]["enabled_in_v0_1"])
        self.assertEqual(workflows["interview-retro"]["status"], "planned")
        self.assertFalse(workflows["interview-retro"]["enabled_in_v0_1"])

        self.assertEqual(research_profiles["web-assisted"]["status"], "planned")
        self.assertFalse(research_profiles["web-assisted"]["enabled_in_v0_1"])
        self.assertEqual(research_profiles["deep-research"]["status"], "planned")
        self.assertFalse(research_profiles["deep-research"]["enabled_in_v0_1"])

        deferred_doc = (ROOT / "docs" / "DEFERRED_CAPABILITIES.md").read_text(encoding="utf-8")
        self.assertIn("mock-interview", deferred_doc)
        self.assertIn("interview-retro", deferred_doc)
        self.assertIn("web-assisted", deferred_doc)
        self.assertIn("deep-research", deferred_doc)

    def test_unified_entrypoint_can_create_import_and_run_in_one_call(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cases_root = Path(tmp_dir) / "cases"
            resume_src = Path(tmp_dir) / "resume.md"
            jd_src = Path(tmp_dir) / "jd.md"
            projects_src = Path(tmp_dir) / "projects.md"

            resume_src.write_text(
                "# Resume\n"
                "## Experience\n"
                "- Built Python services for internal tooling.\n"
                "- Optimized query latency by 20%.\n",
                encoding="utf-8",
            )
            jd_src.write_text(
                "# Backend Engineer\n"
                "- Required: Python backend development\n"
                "- Required: Familiar with MySQL and Redis\n",
                encoding="utf-8",
            )
            projects_src.write_text(
                "# Internal Platform\n"
                "- 负责服务拆分与缓存优化。\n"
                "- 将响应时间降低 20ms。\n",
                encoding="utf-8",
            )

            result = self.run_cmd(
                str(PYTHON),
                str(ROOT / "scripts" / "offer_skill.py"),
                "--workflow",
                "resume-eval",
                "--perspective",
                "interviewer",
                "--display-name",
                "Unified Entry Case",
                "--cases-root",
                str(cases_root),
                "--resume-file",
                str(resume_src),
                "--jd-file",
                str(jd_src),
                "--projects-file",
                str(projects_src),
                "--json",
                cwd=ROOT.parent,
            )

            payload = json.loads(result.stdout)
            self.assertTrue(payload["case_created"])
            self.assertEqual(payload["workflow"], "resume-eval")
            self.assertEqual(payload["perspective"], "interviewer")
            self.assertTrue(Path(payload["output_path"]).exists())
            case_dir = Path(payload["case_dir"])
            meta = json.loads((case_dir / "meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["perspective"], "interviewer")
            self.assertIn("resume-eval", meta["workflow_history"])
