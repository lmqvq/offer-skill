#!/usr/bin/env python3
"""Shared helpers for offer-skill case operations."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


KNOWN_INPUTS = {
    "resume": "resume.md",
    "jd": "jd.md",
    "projects": "projects.md",
    "interview_notes": "interview_notes.md",
    "candidate_answers": "candidate_answers.md",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_case_dir(cases_root: str, case_slug: str) -> Path:
    case_dir = Path(cases_root).expanduser().resolve() / case_slug
    if not case_dir.exists():
        raise FileNotFoundError(f"case not found: {case_dir}")
    return case_dir


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_meta(case_dir: Path) -> dict:
    return load_json(case_dir / "meta.json")


def save_meta(case_dir: Path, meta: dict) -> None:
    meta.setdefault("lifecycle", {})
    meta["lifecycle"]["updated_at"] = now_iso()
    write_json(case_dir / "meta.json", meta)


def append_workflow_history(meta: dict, workflow: str) -> None:
    history = meta.setdefault("workflow_history", [])
    if workflow not in history:
        history.append(workflow)


def mark_input_present(meta: dict, material_type: str) -> None:
    meta.setdefault("inputs", {})
    if material_type in meta["inputs"]:
        meta["inputs"][material_type] = True


def input_path(case_dir: Path, material_type: str) -> Path:
    if material_type not in KNOWN_INPUTS:
        raise KeyError(f"unsupported material type: {material_type}")
    return case_dir / "inputs" / KNOWN_INPUTS[material_type]


def artifact_path(case_dir: Path, meta: dict, artifact_name: str) -> Path:
    relative = meta.get("artifacts", {}).get(artifact_name)
    if not relative:
        raise KeyError(f"unknown artifact: {artifact_name}")
    return case_dir / relative
