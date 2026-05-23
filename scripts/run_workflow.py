#!/usr/bin/env python3
"""Run offer-skill v0.1 workflows against local case materials."""

from __future__ import annotations

import argparse

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
from material_parser import parse_jd_text, parse_projects_text, parse_resume_text
from workflow_engine import (
    build_competency_map,
    build_question_bank,
    evaluate_jd_match,
    render_project_highlight,
    render_resume_eval,
)


SUPPORTED_V0_1 = {"project-highlight", "resume-eval"}
DEFERRED = {
    "mock-interview": "mock-interview is planned after v0.1 and is intentionally not executed yet.",
    "interview-retro": "interview-retro is planned after v0.1 and is intentionally not executed yet.",
}


def require_text(case_dir, material_type: str) -> str:
    path = input_path(case_dir, material_type)
    if not path.exists():
        raise FileNotFoundError(f"required input missing: {path}")
    return read_text(path)


def run_resume_eval(case_dir, meta: dict) -> str:
    resume = parse_resume_text(require_text(case_dir, "resume"))
    write_json(case_dir / "normalized" / "resume.json", resume)

    projects_text = require_text(case_dir, "projects") if input_path(case_dir, "projects").exists() else ""
    projects = parse_projects_text(projects_text) if projects_text.strip() else {"source_type": "projects", "projects": []}
    write_json(case_dir / "normalized" / "projects.json", projects)

    jd = parse_jd_text(require_text(case_dir, "jd"))
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


def run_project_highlight(case_dir, meta: dict) -> str:
    projects = parse_projects_text(require_text(case_dir, "projects"))
    write_json(case_dir / "normalized" / "projects.json", projects)

    resume_text = require_text(case_dir, "resume") if input_path(case_dir, "resume").exists() else ""
    resume = parse_resume_text(resume_text) if resume_text.strip() else {
        "source_type": "resume",
        "candidate_profile": {},
        "education": [],
        "work_experience": [],
        "projects": [],
        "skills": [],
        "claims": [],
        "raw_sections": {},
    }
    write_json(case_dir / "normalized" / "resume.json", resume)

    competency_map = build_competency_map(resume, projects)
    write_json(artifact_path(case_dir, meta, "competency_map"), competency_map)

    question_bank = build_question_bank({"weak_matches": [], "gaps": []}, projects)
    write_json(artifact_path(case_dir, meta, "question_bank"), question_bank)

    analysis = render_project_highlight(meta, projects, competency_map, question_bank)
    output_path = artifact_path(case_dir, meta, "project_highlight")
    write_text(output_path, analysis)
    return str(output_path)


def execute_workflow(case_dir, meta: dict, workflow: str) -> str:
    if workflow in DEFERRED:
        raise ValueError(DEFERRED[workflow])
    if workflow not in SUPPORTED_V0_1:
        raise ValueError(f"unsupported workflow: {workflow}")
    if workflow == "resume-eval":
        return run_resume_eval(case_dir, meta)
    return run_project_highlight(case_dir, meta)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an offer-skill workflow for a case")
    parser.add_argument("--case-slug", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--cases-root", default="cases")
    args = parser.parse_args()

    case_dir = resolve_case_dir(args.cases_root, args.case_slug)
    meta = load_meta(case_dir)
    try:
        output = execute_workflow(case_dir, meta, args.workflow)
    except ValueError as exc:
        raise SystemExit(str(exc))

    append_workflow_history(meta, args.workflow)
    save_meta(case_dir, meta)
    print(output)


if __name__ == "__main__":
    main()
