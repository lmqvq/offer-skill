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

    def test_create_case_writes_full_capability_scope(self) -> None:
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
            meta = json.loads((case_dir / "meta.json").read_text(encoding="utf-8"))
            self.assertEqual(
                meta["scope"]["enabled_workflows"],
                ["project-highlight", "resume-eval", "mock-interview", "interview-retro"],
            )
            self.assertEqual(
                meta["scope"]["research_profiles"],
                ["local-only", "web-assisted", "deep-research"],
            )

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

    def test_run_project_highlight_workflow(self) -> None:
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

    def test_mock_interview_with_research_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cases_root = Path(tmp_dir) / "cases"
            jd_src = Path(tmp_dir) / "jd.md"
            projects_src = Path(tmp_dir) / "projects.md"
            jd_src.write_text(
                "# Backend Engineer\n"
                "- Required: Strong Python backend development\n"
                "- Required: Familiar with Redis and system design\n",
                encoding="utf-8",
            )
            projects_src.write_text(
                "# API Platform\n"
                "- Built Python APIs and optimized Redis cache layers.\n"
                "- Improved latency by 18%.\n",
                encoding="utf-8",
            )
            research_src = Path(tmp_dir) / "research.md"
            research_src.write_text(
                "Recent interview notes ask: How do you design cache consistency? "
                "How do you scale Python services under high concurrency? "
                "How do you explain Redis invalidation tradeoffs?",
                encoding="utf-8",
            )

            result = self.run_cmd(
                str(PYTHON),
                str(ROOT / "scripts" / "offer_skill.py"),
                "--workflow",
                "mock-interview",
                "--perspective",
                "candidate",
                "--display-name",
                "Mock Interview Case",
                "--cases-root",
                str(cases_root),
                "--jd-file",
                str(jd_src),
                "--projects-file",
                str(projects_src),
                "--research-profile",
                "web-assisted",
                "--research-file",
                str(research_src),
                "--json",
                cwd=ROOT.parent,
            )
            payload = json.loads(result.stdout)
            output_path = Path(payload["output_path"])
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("# Mock Interview", content)
            self.assertIn("Research profile: web-assisted", content)
            self.assertTrue((Path(payload["case_dir"]) / "research" / "merged" / "web-assisted-summary.md").exists())

    def test_interview_retro_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cases_root = Path(tmp_dir) / "cases"
            notes_src = Path(tmp_dir) / "notes.md"
            answers_src = Path(tmp_dir) / "answers.md"
            notes_src.write_text(
                "Q: 你为什么使用 Redis？\n"
                "A: 因为需要降低热点查询延迟。\n"
                "Q: 遇到缓存一致性问题怎么办？\n"
                "A: 不太清楚。\n",
                encoding="utf-8",
            )
            answers_src.write_text(
                "Q: 你为什么使用 Redis？\n"
                "A: 我们的订单接口延迟较高，所以我负责把热点查询前移到 Redis，并把平均延迟降低了 20ms。\n",
                encoding="utf-8",
            )

            result = self.run_cmd(
                str(PYTHON),
                str(ROOT / "scripts" / "offer_skill.py"),
                "--workflow",
                "interview-retro",
                "--perspective",
                "dual",
                "--display-name",
                "Retro Case",
                "--cases-root",
                str(cases_root),
                "--interview-notes-file",
                str(notes_src),
                "--candidate-answers-file",
                str(answers_src),
                "--json",
                cwd=ROOT.parent,
            )
            payload = json.loads(result.stdout)
            output_path = Path(payload["output_path"])
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("# Interview Retrospective", content)
            self.assertIn("Knowledge gaps", content)

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
