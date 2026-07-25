#!/usr/bin/env python3
"""Create and claim a design request from a chat-resolved JSON intake."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from design_console import ConsoleApp
from initialize_workspace import initialize_workspace


def start_chat_request(workspace: Path, skill_dir: Path, spec: dict) -> dict:
    initialize_workspace(workspace, skill_dir)
    app = ConsoleApp(workspace, skill_dir)

    design_system_id = str(spec.get("designSystemId", "")).strip()
    design_system_spec = spec.get("designSystem") or {}
    if not design_system_id:
        source_raw = str(design_system_spec.get("sourcePath", "")).strip()
        if not source_raw:
            raise ValueError("デザインシステムのIDまたはローカルパスを指定してください。")
        source = Path(source_raw).expanduser().resolve()
        existing = next(
            (
                item
                for item in app.bootstrap()["designSystems"]
                if Path(str(item.get("sourcePath", ""))).expanduser().resolve()
                == source
            ),
            None,
        )
        if existing:
            design_system_id = existing["id"]
        else:
            registered = app.register_design_system(
                {
                    "name": design_system_spec.get("name") or source.name,
                    "sourcePath": str(source),
                    "description": design_system_spec.get("description", ""),
                    "status": design_system_spec.get("status", "active"),
                }
            )
            design_system_id = registered["id"]

    settings = spec.get("settings") or {}
    output_level = str(spec.get("outputLevel", "")).strip()
    requested_project_type = str(spec.get("projectTypeId", "")).strip()
    if not output_level and requested_project_type in {"wireframe", "ui-mockup", ""}:
        raise ValueError(
            "仕上がりを選択してください: structural-wireframe / "
            "detailed-wireframe / ui-mockup"
        )
    request = app.create_request(
        {
            "title": spec.get("title", ""),
            "prompt": spec.get("prompt", ""),
            "designSystemId": design_system_id,
            "projectTypeId": requested_project_type,
            "outputLevel": output_level,
            "viewports": settings.get("viewports", ["390x844", "1440x1000"]),
            "compareDirections": settings.get("compareDirections", 1),
            "interactive": settings.get("interactive", False),
            "allowGoogleFonts": settings.get("allowGoogleFonts", True),
            "evidencePaths": spec.get("evidencePaths", []),
        }
    )
    return app.update_request_status(
        request["id"],
        "generating",
        "Codexがチャットから制作しています。",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    skill_dir = Path(__file__).resolve().parent.parent
    request = start_chat_request(args.workspace, skill_dir, spec)
    print(json.dumps(request, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
