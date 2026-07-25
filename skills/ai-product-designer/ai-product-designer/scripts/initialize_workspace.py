#!/usr/bin/env python3
"""Initialize a non-destructive AI Product Designer workspace."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(payload)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def initialize_workspace(
    workspace: Path, skill_dir: Path, project_name: str | None = None
) -> dict:
    workspace = workspace.expanduser().resolve()
    skill_dir = skill_dir.resolve()
    seed = skill_dir / "assets" / "workspace-seed"
    if not seed.is_dir():
        raise FileNotFoundError(f"Workspace seed is missing: {seed}")

    workspace.mkdir(parents=True, exist_ok=True)
    for name in ("requests", "work", "exports", ".design-console/uploads"):
        (workspace / name).mkdir(parents=True, exist_ok=True)

    for relative in (
        Path("design-systems/registry.json"),
        Path("project-types/catalog.json"),
    ):
        destination = workspace / relative
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(seed / relative, destination)

    project_path = workspace / "project.json"
    if project_path.exists():
        project = json.loads(project_path.read_text(encoding="utf-8"))
    else:
        now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        project = {
            "schemaVersion": 1,
            "name": (project_name or workspace.name).strip() or "Untitled project",
            "createdAt": now,
            "updatedAt": now,
            "activeRequestId": None,
        }
        write_json_atomic(project_path, project)

    return {
        "workspace": str(workspace),
        "project": project,
        "created": {
            "project": str(project_path),
            "requests": str(workspace / "requests"),
            "work": str(workspace / "work"),
            "exports": str(workspace / "exports"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--name")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    result = initialize_workspace(args.workspace, skill_dir, args.name)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
