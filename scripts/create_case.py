#!/usr/bin/env python3
"""Create a new offer-skill case scaffold."""

from __future__ import annotations

import argparse
import json
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path


PERSPECTIVES = {"candidate", "interviewer", "dual"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_stack(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def build_meta(args: argparse.Namespace) -> dict:
    timestamp = now_iso()
    return {
        "schema_version": "1",
        "id": f"offer.case.{args.case_slug}",
        "kind": "offer-case",
        "case_slug": args.case_slug,
        "display_name": args.display_name,
        "summary": args.summary or "",
        "perspective": args.perspective,
        "workflow_history": [],
        "target_role": {
            "title": args.role_title or "",
            "level": args.level or "",
            "company_type": args.company_type or "",
            "stack": parse_stack(args.stack),
        },
        "inputs": {
            "resume": False,
            "jd": False,
            "projects": False,
            "interview_notes": False,
            "candidate_answers": False,
        },
        "research": {
            "profile": "local-only",
            "available_profiles": ["local-only", "web-assisted", "deep-research"],
            "sources_count": 0,
            "last_updated_at": None,
            "enabled_in_v0_1": False,
            "deferred_note": "Web-assisted and deep research are planned after v0.1.",
        },
        "artifacts": {
            "project_highlight": "analyses/project_highlight.md",
            "resume_eval": "analyses/resume_eval.md",
            "mock_interview": "analyses/mock_interview.md",
            "interview_retro": "analyses/interview_retro.md",
            "competency_map": "derived/competency_map.json",
            "jd_match": "derived/jd_match.json",
            "question_bank": "derived/question_bank.json",
        },
        "lifecycle": {
            "status": "active",
            "version": "v1",
            "created_at": timestamp,
            "updated_at": timestamp,
        },
        "scope": {
            "v0_1_enabled_workflows": ["project-highlight", "resume-eval"],
            "deferred_workflows": ["mock-interview", "interview-retro"],
            "local_only": True,
        },
    }


def build_manifest(meta: dict) -> dict:
    return {
        "manifest_version": "1",
        "id": meta["id"],
        "kind": meta["kind"],
        "display_name": meta["display_name"],
        "entrypoints": {
            "project-highlight": meta["artifacts"]["project_highlight"],
            "resume-eval": meta["artifacts"]["resume_eval"],
            "mock-interview": meta["artifacts"]["mock_interview"],
            "interview-retro": meta["artifacts"]["interview_retro"],
        },
        "artifacts": [
            "meta.json",
            "manifest.json",
            "inputs/resume.md",
            "inputs/jd.md",
            "inputs/projects.md",
            "inputs/interview_notes.md",
            "inputs/candidate_answers.md",
            meta["artifacts"]["competency_map"],
            meta["artifacts"]["jd_match"],
            meta["artifacts"]["question_bank"],
        ],
        "capabilities": [
            "project-highlight",
            "resume-eval",
            "mock-interview",
            "interview-retro",
        ],
        "v0_1_enabled_capabilities": ["project-highlight", "resume-eval"],
        "deferred_capabilities": ["mock-interview", "interview-retro", "web-assisted-research"],
        "research_profiles": {
            "enabled_in_v0_1": ["local-only"],
            "deferred_after_v0_1": ["web-assisted", "deep-research"]
        },
    }


def ensure_layout(case_dir: Path) -> None:
    directories = [
        "inputs",
        "normalized",
        "derived",
        "analyses",
        "research/raw",
        "research/merged",
        "research/reviews",
        "versions",
    ]
    for directory in directories:
        (case_dir / directory).mkdir(parents=True, exist_ok=True)


def create_placeholder_inputs(case_dir: Path) -> None:
    placeholders = {
        "inputs/resume.md": "# Resume\n",
        "inputs/jd.md": "# Job Description\n",
        "inputs/projects.md": "# Projects\n",
        "inputs/interview_notes.md": "# Interview Notes\n",
        "inputs/candidate_answers.md": "# Candidate Answers\n",
    }
    for relative_path, content in placeholders.items():
        path = case_dir / relative_path
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def create_case(args: argparse.Namespace) -> Path:
    cases_root = Path(args.cases_root).expanduser().resolve()
    case_dir = cases_root / args.case_slug
    if case_dir.exists():
        raise FileExistsError(f"case already exists: {case_dir}")

    ensure_layout(case_dir)
    create_placeholder_inputs(case_dir)

    meta = build_meta(args)
    manifest = build_manifest(meta)

    (case_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (case_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return case_dir


def create_case_from_values(
    *,
    case_slug: str,
    display_name: str,
    perspective: str,
    cases_root: str = "cases",
    summary: str | None = None,
    role_title: str | None = None,
    level: str | None = None,
    company_type: str | None = None,
    stack: str | None = None,
) -> Path:
    args = Namespace(
        case_slug=case_slug,
        display_name=display_name,
        perspective=perspective,
        cases_root=cases_root,
        summary=summary,
        role_title=role_title,
        level=level,
        company_type=company_type,
        stack=stack,
    )
    return create_case(args)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new offer-skill case")
    parser.add_argument("--case-slug", required=True, help="Directory-friendly case slug")
    parser.add_argument("--display-name", required=True, help="Human-readable case name")
    parser.add_argument("--perspective", required=True, choices=sorted(PERSPECTIVES))
    parser.add_argument("--cases-root", default="cases", help="Cases directory root")
    parser.add_argument("--summary", help="Optional case summary")
    parser.add_argument("--role-title", help="Target role title")
    parser.add_argument("--level", help="Target seniority or level")
    parser.add_argument("--company-type", help="Target company type")
    parser.add_argument("--stack", help="Comma-separated target stack")
    args = parser.parse_args()

    case_dir = create_case(args)
    print(case_dir)


if __name__ == "__main__":
    main()
