#!/usr/bin/env python3
"""Run the quality gates, mark a request ready, and package it atomically."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from design_console import ConsoleApp
from initialize_workspace import initialize_workspace


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--entrypoint", default="wireframe/index.html")
    parser.add_argument(
        "--message",
        default="品質ゲートと視覚検査を通過し、制作物の準備ができました。",
    )
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    initialize_workspace(args.workspace, skill_dir)
    app = ConsoleApp(args.workspace, skill_dir)
    try:
        request = app.update_request_status(
            args.request_id,
            "ready",
            message=args.message,
            entrypoint=args.entrypoint,
        )
        archive = app.export_request(args.request_id)
        output_level = request.get("settings", {}).get("outputLevel")
        single_file = (
            app.export_single_html(args.request_id)
            if output_level in {"structural-wireframe", "detailed-wireframe"}
            else None
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        try:
            app.update_request_status(
                args.request_id,
                "error",
                message=f"品質ゲート未通過: {error}",
            )
        except (OSError, ValueError, json.JSONDecodeError):
            pass
        print(f"FAIL {error}")
        return 1

    print(
        json.dumps(
            {
                "request": request,
                "archive": str(archive),
                "singleFile": str(single_file) if single_file else None,
                "primaryExport": str(single_file or archive),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
