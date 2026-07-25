#!/usr/bin/env python3
"""Record a human/agent-inspected render in the delivery manifest."""

from __future__ import annotations

import argparse
import json
import os
import struct
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def write_json_atomic(path: Path, value: dict) -> None:
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def image_dimensions(path: Path) -> tuple[int, int] | None:
    payload = path.read_bytes()
    if payload.startswith(b"\x89PNG\r\n\x1a\n") and len(payload) >= 24:
        return struct.unpack(">II", payload[16:24])
    if payload.startswith(b"\xff\xd8"):
        offset = 2
        while offset + 9 < len(payload):
            if payload[offset] != 0xFF:
                offset += 1
                continue
            marker = payload[offset + 1]
            offset += 2
            if marker in {0xD8, 0xD9}:
                continue
            if offset + 2 > len(payload):
                break
            length = int.from_bytes(payload[offset : offset + 2], "big")
            if marker in {
                0xC0,
                0xC1,
                0xC2,
                0xC3,
                0xC5,
                0xC6,
                0xC7,
                0xC9,
                0xCA,
                0xCB,
                0xCD,
                0xCE,
                0xCF,
            } and offset + 7 < len(payload):
                height = int.from_bytes(payload[offset + 3 : offset + 5], "big")
                width = int.from_bytes(payload[offset + 5 : offset + 7], "big")
                return width, height
            if length < 2:
                break
            offset += length
    return None


def record(
    workdir: Path,
    direction_id: str,
    viewport: str,
    image: Path,
    notes: str,
) -> dict:
    workdir = workdir.resolve()
    request = json.loads((workdir / "design-request.json").read_text(encoding="utf-8"))
    plan = json.loads(
        (workdir / "exploration" / "design-plan.json").read_text(encoding="utf-8")
    )
    valid_directions = {item["id"] for item in plan.get("directions", [])}
    if direction_id not in valid_directions:
        raise ValueError(f"Unknown direction: {direction_id}")
    valid_viewports = set(request.get("settings", {}).get("viewports", []))
    if viewport not in valid_viewports:
        raise ValueError(f"Unknown viewport: {viewport}")
    if len(notes.strip()) < 12:
        raise ValueError("Inspection notes must describe a concrete visual finding.")

    renders = (workdir / "renders").resolve()
    candidate = image if image.is_absolute() else renders / image
    candidate = candidate.resolve()
    try:
        relative = candidate.relative_to(renders)
    except ValueError as error:
        raise ValueError("Render image must be inside the renders directory.") from error
    if not candidate.is_file():
        raise ValueError(f"Render image does not exist: {candidate}")
    if candidate.stat().st_size < 128:
        raise ValueError(f"Render image is too small to be valid: {candidate}")
    dimensions = image_dimensions(candidate)
    if dimensions is None:
        raise ValueError("Render image must be a readable PNG or JPEG.")

    manifest_path = renders / "render-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"schemaVersion": 1, "checks": []}
    checks = manifest.setdefault("checks", [])
    check = {
        "directionId": direction_id,
        "viewport": viewport,
        "image": relative.as_posix(),
        "width": dimensions[0],
        "height": dimensions[1],
        "inspected": True,
        "notes": notes.strip(),
        "inspectedAt": datetime.now(timezone.utc)
        .astimezone()
        .isoformat(timespec="seconds"),
    }
    checks[:] = [
        item
        for item in checks
        if not (
            item.get("directionId") == direction_id
            and item.get("viewport") == viewport
        )
    ]
    checks.append(check)
    checks.sort(key=lambda item: (item["directionId"], item["viewport"]))
    write_json_atomic(manifest_path, manifest)
    return check


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--direction", required=True)
    parser.add_argument("--viewport", required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--notes", required=True)
    args = parser.parse_args()
    try:
        result = record(
            args.workdir,
            args.direction,
            args.viewport,
            args.image,
            args.notes,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}")
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
