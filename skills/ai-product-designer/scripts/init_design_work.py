#!/usr/bin/env python3
"""Create a non-destructive design-work folder from the bundled wireframe kit."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def write_new(path: Path, content: str) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", default="Untitled design exploration")
    args = parser.parse_args()

    output = args.output.expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"Output directory is not empty: {output}")

    kit = Path(__file__).resolve().parent.parent / "assets" / "wireframe-kit"
    output.mkdir(parents=True, exist_ok=True)
    for name in ("evidence", "design-system", "exploration", "renders", "reports"):
        (output / name).mkdir()
    shutil.copytree(kit, output / "wireframe")

    write_new(
        output / "brief.md",
        f"""# {args.title}

## Status

Draft

## Evidence boundary

- Observed:
- Reported:
- Inferred:
- Unknown:

## Problem framing

- Target user:
- Situation:
- Primary job:
- Current friction:
- Desired behavior:
- Business outcome:
- Success signal:
- Constraints:
- Non-goals:
- Target viewports:
""",
    )
    for name, heading in (
        ("ux-audit.md", "UX audit"),
        ("design-rationale.md", "Design rationale"),
        ("qa-report.md", "QA report"),
    ):
        write_new(output / "reports" / name, f"# {heading}\n\nStatus: Draft\n")

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

