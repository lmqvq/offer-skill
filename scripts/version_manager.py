#!/usr/bin/env python3
"""Back up and restore offer-skill cases."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


TRACKED_PATHS = [
    "meta.json",
    "manifest.json",
    "inputs",
    "normalized",
    "derived",
    "analyses",
    "research",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_case_dir(cases_root: str, case_slug: str) -> Path:
    case_dir = Path(cases_root).expanduser().resolve() / case_slug
    if not case_dir.exists():
        raise FileNotFoundError(f"case not found: {case_dir}")
    return case_dir


def load_meta(case_dir: Path) -> dict:
    meta_path = case_dir / "meta.json"
    return json.loads(meta_path.read_text(encoding="utf-8"))


def write_meta(case_dir: Path, meta: dict) -> None:
    (case_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def copy_path(src: Path, dst: Path) -> None:
    if src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def backup(case_dir: Path) -> str:
    meta = load_meta(case_dir)
    version = meta.get("lifecycle", {}).get("version", "v1")
    snapshot_dir = case_dir / "versions" / version
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    for relative in TRACKED_PATHS:
        src = case_dir / relative
        if src.exists():
            copy_path(src, snapshot_dir / relative)

    return version


def list_versions(case_dir: Path) -> list[str]:
    versions_dir = case_dir / "versions"
    if not versions_dir.exists():
        return []
    return sorted(entry.name for entry in versions_dir.iterdir() if entry.is_dir())


def rollback(case_dir: Path, version: str) -> None:
    snapshot_dir = case_dir / "versions" / version
    if not snapshot_dir.exists():
        raise FileNotFoundError(f"version not found: {snapshot_dir}")

    current_meta = load_meta(case_dir)
    current_version = current_meta.get("lifecycle", {}).get("version", "v1")
    pre_restore = case_dir / "versions" / f"{current_version}_before_restore"
    pre_restore.mkdir(parents=True, exist_ok=True)

    for relative in TRACKED_PATHS:
        src = case_dir / relative
        if src.exists():
            copy_path(src, pre_restore / relative)

    for relative in TRACKED_PATHS:
        dst = case_dir / relative
        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()

    for relative in TRACKED_PATHS:
        src = snapshot_dir / relative
        if src.exists():
            copy_path(src, case_dir / relative)

    restored_meta = load_meta(case_dir)
    restored_meta.setdefault("lifecycle", {})
    restored_meta["lifecycle"]["version"] = f"{version}_restored"
    restored_meta["lifecycle"]["updated_at"] = now_iso()
    restored_meta["rollback_from"] = current_version
    write_meta(case_dir, restored_meta)


def main() -> None:
    parser = argparse.ArgumentParser(description="Back up or restore offer-skill cases")
    parser.add_argument("--action", required=True, choices=["backup", "list", "rollback"])
    parser.add_argument("--case-slug", required=True)
    parser.add_argument("--cases-root", default="cases")
    parser.add_argument("--version", help="Version to restore for rollback")
    args = parser.parse_args()

    case_dir = resolve_case_dir(args.cases_root, args.case_slug)

    if args.action == "backup":
        print(backup(case_dir))
        return

    if args.action == "list":
        for version in list_versions(case_dir):
            print(version)
        return

    if not args.version:
        raise SystemExit("--version is required for rollback")
    rollback(case_dir, args.version)
    print(args.version)


if __name__ == "__main__":
    main()
