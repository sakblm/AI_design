#!/usr/bin/env python3
"""Create a ZIP delivery for an existing design request."""

from __future__ import annotations

import argparse
from pathlib import Path

from design_console import ConsoleApp
from initialize_workspace import initialize_workspace


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--request-id", required=True)
    args = parser.parse_args()
    skill_dir = Path(__file__).resolve().parent.parent
    initialize_workspace(args.workspace, skill_dir)
    archive = ConsoleApp(args.workspace, skill_dir).export_request(args.request_id)
    print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
