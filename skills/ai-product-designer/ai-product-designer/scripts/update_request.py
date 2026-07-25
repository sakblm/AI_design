#!/usr/bin/env python3
"""Update a design request status after Codex generation or revision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from design_console import ConsoleApp, VALID_REQUEST_STATUS
from initialize_workspace import initialize_workspace


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--status", choices=sorted(VALID_REQUEST_STATUS), required=True)
    parser.add_argument("--message", default="")
    parser.add_argument("--entrypoint")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    initialize_workspace(args.workspace, skill_dir)
    app = ConsoleApp(args.workspace, skill_dir)
    request = app.update_request_status(
        args.request_id,
        args.status,
        message=args.message,
        entrypoint=args.entrypoint,
    )
    print(json.dumps(request, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
