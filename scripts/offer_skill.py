#!/usr/bin/env python3
"""Unified entrypoint for offer-skill v0.1."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import append_workflow_history, load_meta, now_iso, resolve_case_dir, save_meta
from create_case import create_case_from_values
from import_material import import_material
from run_workflow import execute_workflow


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or f"offer-case-{now_iso()[:10]}"


def load_optional_content(file_path: str | None, inline_text: str | None) -> str | None:
    if file_path:
        return Path(file_path).expanduser().read_text(encoding="utf-8")
    if inline_text:
        return inline_text
    return None


def ensure_case(args: argparse.Namespace) -> tuple[Path, bool]:
    case_slug = args.case_slug or slugify(args.display_name or f"{args.workflow}-{args.perspective}")
    cases_root = Path(args.cases_root).expanduser().resolve()
    case_dir = cases_root / case_slug
    if case_dir.exists():
        return case_dir, False

    display_name = args.display_name or f"{args.workflow} {args.perspective}"
    created_dir = create_case_from_values(
        case_slug=case_slug,
        display_name=display_name,
        perspective=args.perspective,
        cases_root=str(cases_root),
        summary=args.summary,
        role_title=args.role_title,
        level=args.level,
        company_type=args.company_type,
        stack=args.stack,
    )
    return created_dir, True


def sync_meta_overrides(case_dir: Path, args: argparse.Namespace) -> dict:
    meta = load_meta(case_dir)
    changed = False

    if args.display_name and meta.get("display_name") != args.display_name:
        meta["display_name"] = args.display_name
        changed = True
    if args.summary is not None and meta.get("summary") != args.summary:
        meta["summary"] = args.summary
        changed = True
    if args.perspective and meta.get("perspective") != args.perspective:
        meta["perspective"] = args.perspective
        changed = True

    target_role = meta.setdefault("target_role", {})
    for arg_name, key in (
        ("role_title", "title"),
        ("level", "level"),
        ("company_type", "company_type"),
    ):
        value = getattr(args, arg_name, None)
        if value and target_role.get(key) != value:
            target_role[key] = value
            changed = True

    if args.stack:
        stack = [item.strip() for item in args.stack.split(",") if item.strip()]
        if target_role.get("stack") != stack:
            target_role["stack"] = stack
            changed = True

    if changed:
        save_meta(case_dir, meta)
    return load_meta(case_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified entrypoint for offer-skill v0.1")
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--perspective", default="candidate", choices=["candidate", "interviewer", "dual"])
    parser.add_argument("--case-slug", help="Reuse an existing case or set the new case slug")
    parser.add_argument("--display-name", help="Human-readable case name")
    parser.add_argument("--cases-root", default="cases")
    parser.add_argument("--summary", help="Optional case summary")
    parser.add_argument("--role-title", help="Target role title")
    parser.add_argument("--level", help="Target seniority or level")
    parser.add_argument("--company-type", help="Target company type")
    parser.add_argument("--stack", help="Comma-separated target stack")
    parser.add_argument("--resume-file")
    parser.add_argument("--resume-text")
    parser.add_argument("--jd-file")
    parser.add_argument("--jd-text")
    parser.add_argument("--projects-file")
    parser.add_argument("--projects-text")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    args = parser.parse_args()

    case_dir, created = ensure_case(args)
    meta = sync_meta_overrides(case_dir, args)

    imported: dict[str, str] = {}
    for material_type, file_attr, text_attr in (
        ("resume", "resume_file", "resume_text"),
        ("jd", "jd_file", "jd_text"),
        ("projects", "projects_file", "projects_text"),
    ):
        content = load_optional_content(getattr(args, file_attr), getattr(args, text_attr))
        if content is not None:
            target_path = import_material(case_dir=case_dir, material_type=material_type, content=content)
            imported[material_type] = str(target_path)

    meta = load_meta(case_dir)
    try:
        output_path = execute_workflow(case_dir, meta, args.workflow)
    except ValueError as exc:
        raise SystemExit(str(exc))
    append_workflow_history(meta, args.workflow)
    save_meta(case_dir, meta)

    payload = {
        "case_created": created,
        "case_dir": str(case_dir),
        "case_slug": case_dir.name,
        "workflow": args.workflow,
        "perspective": meta.get("perspective", args.perspective),
        "imported": imported,
        "output_path": output_path,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"Case: {payload['case_dir']}")
    print(f"Workflow: {payload['workflow']}")
    print(f"Perspective: {payload['perspective']}")
    if imported:
        print("Imported:")
        for material_type, path in imported.items():
            print(f"  {material_type}: {path}")
    print(f"Output: {payload['output_path']}")


if __name__ == "__main__":
    main()
