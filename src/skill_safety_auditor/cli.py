from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .audit import SEVERITY_ORDER, audit_directory


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="skill-audit",
        description="Offline heuristic audit for an Agent Skill directory before installation.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Skill directory containing SKILL.md")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument(
        "--fail-on",
        choices=("moderate", "high", "block"),
        default=None,
        help="Return exit code 1 when the report reaches this risk level.",
    )
    args = parser.parse_args()

    root = Path(args.path)
    if not root.is_dir():
        print(f"skill-audit: directory not found: {root}", file=sys.stderr)
        return 2

    report = audit_directory(root)
    print(report.to_json() if args.format == "json" else report.to_markdown(), end="")

    if args.fail_on:
        threshold = args.fail_on.upper()
        if SEVERITY_ORDER[report.risk] >= SEVERITY_ORDER[threshold]:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
