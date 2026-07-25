#!/usr/bin/env python3
"""Wait for and atomically claim the next queued design request."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from design_console import ConsoleApp
from initialize_workspace import initialize_workspace


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--poll-interval", type=float, default=1.0)
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    initialize_workspace(args.workspace, skill_dir)
    app = ConsoleApp(args.workspace, skill_dir)
    deadline = time.monotonic() + max(0, args.timeout)

    while True:
        request = app.claim_next_request()
        if request:
            print(json.dumps(request, ensure_ascii=False, indent=2), flush=True)
            return 0
        if time.monotonic() >= deadline:
            print(
                json.dumps(
                    {"status": "timeout", "message": "新しい制作依頼はありません。"},
                    ensure_ascii=False,
                ),
                flush=True,
            )
            return 2
        time.sleep(max(0.2, args.poll_interval))


if __name__ == "__main__":
    raise SystemExit(main())
