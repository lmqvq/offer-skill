#!/usr/bin/env python3
"""Run offer-skill workflows against case materials."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    append_workflow_history,
    artifact_path,
    input_path,
    load_meta,
    read_text,
    resolve_case_dir,
    save_meta,
    write_json,
    write_text,
)
from material_parser import (
    parse_candidate_answers_text,
    parse_interview_notes_text,
    parse_jd_text,
    parse_projects_text,
    parse_resume_text,
)
from research_engine import build_research_bundle
from workflow_engine import (
    build_competency_map,
    build_question_bank,
    build_research_question_bank,
    evaluate_interview_rounds,
    evaluate_jd_match,
    merge_question_banks,
    render_interview_retro,
    render_mock_interview,
    render_project_highlight,
    render_resume_eval,
)


SUPPORTED_WORKFLOWS = {"project-highlight", "resume-eval", "mock-interview", "interview-retro"}
RESEARCH_PROFILES = {"local-only", "web-assisted", "deep-research"}


def require_text(case_dir: Path, material_type: str) -> str:
    path = input_path(case_dir, material_type)
    if not path.exists():
        raise FileNotFoundError(f"required input missing: {path}")
    return read_text(path)


def maybe_resume(case_dir: Path) -> dict:
    if input_path(case_dir, "resume").exists():
        text = require_text(case_dir, "resume")
        if text.strip():
            return parse_resume_text(text)
    return {
        "source_type": "resume",
        "candidate_profile": {},
        "education": [],
        "work_experience": [],
        "projects": [],
        "skills": [],
        "claims": [],
        "raw_sections": {},
    }


def maybe_projects(case_dir: Path) -> dict:
    if input_path(case_dir, "projects").exists():
        text = require_text(case_dir, "projects")
        if text.strip():
            return parse_projects_text(text)
    return {"source_type": "projects", "projects": []}


def maybe_jd(case_dir: Path) -> dict | None:
    if input_path(case_dir, "jd").exists():
        text = require_text(case_dir, "jd")
        if text.strip():
            return parse_jd_text(text)
    return None


def maybe_candidate_answers(case_dir: Path) -> dict | None:
    if input_path(case_dir, "candidate_answers").exists():
        text = require_text(case_dir, "candidate_answers")
        if text.strip():
            return parse_candidate_answers_text(text)
    return None


def maybe_research_bundle(case_dir: Path, meta: dict, research_profile: str, research_query: str | None, research_text: str | None) -> dict | None:
    meta.setdefault("research", {})
    meta["research"]["profile"] = research_profile
    if research_profile == "local-only" and not research_text:
        meta["research"]["sources_count"] = 0
        return None
    bundle = build_research_bundle(
        case_dir=case_dir,
        profile=research_profile,
        role_title=meta.get("target_role", {}).get("title", ""),
        stack=meta.get("target_role", {}).get("stack", []),
        explicit_query=research_query,
        research_text=research_text,
    )
    meta["research"]["sources_count"] = bundle.get("source_count", 0)
    meta["research"]["last_updated_at"] = meta.get("lifecycle", {}).get("updated_at")
    return bundle


def run_resume_eval(case_dir: Path, meta: dict) -> str:
    resume = maybe_resume(case_dir)
    projects = maybe_projects(case_dir)
    jd = maybe_jd(case_dir)
    if jd is None:
        raise ValueError("resume-eval requires JD input")

    write_json(case_dir / "normalized" / "resume.json", resume)
    write_json(case_dir / "normalized" / "projects.json", projects)
    write_json(case_dir / "normalized" / "jd.json", jd)

    competency_map = build_competency_map(resume, projects)
    write_json(artifact_path(case_dir, meta, "competency_map"), competency_map)

    jd_match = evaluate_jd_match(resume, jd, projects)
    write_json(artifact_path(case_dir, meta, "jd_match"), jd_match)

    question_bank = build_question_bank(jd_match, projects)
    write_json(artifact_path(case_dir, meta, "question_bank"), question_bank)

    analysis = render_resume_eval(meta, resume, jd, jd_match, question_bank)
    output_path = artifact_path(case_dir, meta, "resume_eval")
    write_text(output_path, analysis)
    return str(output_path)


def run_project_highlight(case_dir: Path, meta: dict) -> str:
    projects = maybe_projects(case_dir)
    if not projects.get("projects"):
        raise ValueError("project-highlight requires project input")
    resume = maybe_resume(case_dir)

    write_json(case_dir / "normalized" / "projects.json", projects)
    write_json(case_dir / "normalized" / "resume.json", resume)

    competency_map = build_competency_map(resume, projects)
    write_json(artifact_path(case_dir, meta, "competency_map"), competency_map)

    question_bank = build_question_bank({"weak_matches": [], "gaps": []}, projects)
    write_json(artifact_path(case_dir, meta, "question_bank"), question_bank)

    analysis = render_project_highlight(meta, projects, competency_map, question_bank)
    output_path = artifact_path(case_dir, meta, "project_highlight")
    write_text(output_path, analysis)
    return str(output_path)


def run_mock_interview(case_dir: Path, meta: dict, research_profile: str, research_query: str | None, research_text: str | None) -> str:
    jd = maybe_jd(case_dir)
    if jd is None:
        raise ValueError("mock-interview requires JD input")
    resume = maybe_resume(case_dir)
    projects = maybe_projects(case_dir)

    write_json(case_dir / "normalized" / "resume.json", resume)
    write_json(case_dir / "normalized" / "projects.json", projects)
    write_json(case_dir / "normalized" / "jd.json", jd)

    competency_map = build_competency_map(resume, projects)
    write_json(artifact_path(case_dir, meta, "competency_map"), competency_map)
    jd_match = evaluate_jd_match(resume, jd, projects)
    write_json(artifact_path(case_dir, meta, "jd_match"), jd_match)

    local_question_bank = build_question_bank(jd_match, projects)
    research_bundle = maybe_research_bundle(case_dir, meta, research_profile, research_query, research_text)
    research_question_bank = build_research_question_bank(research_bundle) if research_bundle else {"questions": []}
    question_bank = merge_question_banks(local_question_bank, research_question_bank)
    write_json(artifact_path(case_dir, meta, "question_bank"), question_bank)

    analysis = render_mock_interview(meta, jd_match, question_bank, research_bundle)
    output_path = artifact_path(case_dir, meta, "mock_interview")
    write_text(output_path, analysis)
    return str(output_path)


def run_interview_retro(case_dir: Path, meta: dict, research_profile: str, research_query: str | None, research_text: str | None) -> str:
    if not input_path(case_dir, "interview_notes").exists() or not require_text(case_dir, "interview_notes").strip():
        raise ValueError("interview-retro requires interview notes input")

    interview_notes = parse_interview_notes_text(require_text(case_dir, "interview_notes"))
    candidate_answers = maybe_candidate_answers(case_dir)
    jd = maybe_jd(case_dir)
    resume = maybe_resume(case_dir)
    projects = maybe_projects(case_dir)
    jd_match = evaluate_jd_match(resume, jd, projects) if jd else None

    write_json(case_dir / "normalized" / "interview_notes.json", interview_notes)
    if candidate_answers:
        write_json(case_dir / "normalized" / "candidate_answers.json", candidate_answers)
    if jd:
        write_json(case_dir / "normalized" / "jd.json", jd)
    write_json(case_dir / "normalized" / "resume.json", resume)
    write_json(case_dir / "normalized" / "projects.json", projects)
    if jd_match:
        write_json(artifact_path(case_dir, meta, "jd_match"), jd_match)

    research_bundle = maybe_research_bundle(case_dir, meta, research_profile, research_query, research_text)
    retro_eval = evaluate_interview_rounds(interview_notes, candidate_answers)
    analysis = render_interview_retro(meta, retro_eval, jd_match, research_bundle)
    output_path = artifact_path(case_dir, meta, "interview_retro")
    write_text(output_path, analysis)
    return str(output_path)


def execute_workflow(
    case_dir: Path,
    meta: dict,
    workflow: str,
    research_profile: str = "local-only",
    research_query: str | None = None,
    research_text: str | None = None,
) -> str:
    if workflow not in SUPPORTED_WORKFLOWS:
        raise ValueError(f"unsupported workflow: {workflow}")
    if research_profile not in RESEARCH_PROFILES:
        raise ValueError(f"unsupported research profile: {research_profile}")
    if workflow == "resume-eval":
        return run_resume_eval(case_dir, meta)
    if workflow == "project-highlight":
        return run_project_highlight(case_dir, meta)
    if workflow == "mock-interview":
        return run_mock_interview(case_dir, meta, research_profile, research_query, research_text)
    return run_interview_retro(case_dir, meta, research_profile, research_query, research_text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an offer-skill workflow for a case")
    parser.add_argument("--case-slug", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--cases-root", default="cases")
    parser.add_argument("--research-profile", default="local-only", choices=sorted(RESEARCH_PROFILES))
    parser.add_argument("--research-query")
    parser.add_argument("--research-file")
    parser.add_argument("--research-text")
    args = parser.parse_args()

    case_dir = resolve_case_dir(args.cases_root, args.case_slug)
    meta = load_meta(case_dir)
    research_text = args.research_text
    if args.research_file:
        research_text = read_text(Path(args.research_file).expanduser())

    try:
        output = execute_workflow(case_dir, meta, args.workflow, args.research_profile, args.research_query, research_text)
    except ValueError as exc:
        raise SystemExit(str(exc))

    append_workflow_history(meta, args.workflow)
    save_meta(case_dir, meta)
    print(output)


if __name__ == "__main__":
    main()
