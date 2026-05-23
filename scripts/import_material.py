#!/usr/bin/env python3
"""Import local material into an offer-skill case."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import KNOWN_INPUTS, input_path, load_meta, mark_input_present, resolve_case_dir, save_meta, write_text


def load_material(args: argparse.Namespace) -> str:
    if args.from_file:
        return Path(args.from_file).expanduser().read_text(encoding="utf-8")
    if args.text:
        return args.text
    raise SystemExit("Provide --from-file or --text")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a local material file into an offer-skill case")
    parser.add_argument("--case-slug", required=True)
    parser.add_argument("--material-type", required=True, choices=sorted(KNOWN_INPUTS))
    parser.add_argument("--cases-root", default="cases")
    parser.add_argument("--from-file", help="Path to a local text or markdown file")
    parser.add_argument("--text", help="Inline text content")
    args = parser.parse_args()

    case_dir = resolve_case_dir(args.cases_root, args.case_slug)
    content = load_material(args)
    target_path = input_path(case_dir, args.material_type)
    write_text(target_path, content)

    meta = load_meta(case_dir)
    mark_input_present(meta, args.material_type)
    save_meta(case_dir, meta)
    print(target_path)


if __name__ == "__main__":
    main()
