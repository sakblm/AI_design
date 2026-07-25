#!/usr/bin/env python3
"""Validate content, traceability, reports, and visual evidence for a delivery."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from record_visual_check import image_dimensions  # noqa: E402
from validate_design_plan import (  # noqa: E402
    minimum_screens_for_request,
    request_output_level,
    requires_media_contract,
    validate_plan,
)


VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
CONTROL_TAGS = {"button", "a", "input", "select", "textarea"}
PLACEHOLDER_MARKERS = (
    "design exploration",
    "state the design hypothesis",
    "replace with",
    "screen placeholder",
    "画面タイトル",
    "ここに画面を実装",
    "仮テキスト",
    "lorem ipsum",
)
REPORT_REQUIREMENTS = {
    "ux-audit.md": 300,
    "design-rationale.md": 300,
    "qa-report.md": 250,
}


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


class DirectionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.directions: list[dict] = []
        self.current_direction: dict | None = None
        self.current_screen: dict | None = None
        self.template_placeholders = 0
        self.template_unresolved = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("data-template-state") == "unresolved":
            self.template_unresolved = True
        if "data-template-placeholder" in values:
            self.template_placeholders += 1

        if self.current_direction is None and "data-design-direction" in values:
            self.current_direction = {
                "id": values.get("data-design-direction") or "unnamed",
                "rootDepth": self.depth,
                "hypothesis": values.get("data-design-hypothesis") or "",
                "screens": [],
                "controls": 0,
                "captions": 0,
                "prototypeStates": 0,
                "text": [],
            }

        if self.current_direction is not None:
            if tag in CONTROL_TAGS:
                self.current_direction["controls"] += 1
            if "data-screen-caption" in values:
                self.current_direction["captions"] += 1
            if "data-prototype-state" in values:
                self.current_direction["prototypeStates"] += 1
            if self.current_screen is None and "data-wireframe-screen" in values:
                self.current_screen = {
                    "id": values.get("data-screen-id") or "",
                    "requirementIds": (
                        values.get("data-requirement-ids") or ""
                    ).split(),
                    "rootDepth": self.depth,
                    "controls": 1 if tag in CONTROL_TAGS else 0,
                    "mediaSlots": [],
                    "mediaPlaceholders": 0,
                    "mediaMissingStates": 0,
                    "text": [],
                }
            elif self.current_screen is not None and tag in CONTROL_TAGS:
                self.current_screen["controls"] += 1
            if self.current_screen is not None:
                if "data-media-slot" in values:
                    self.current_screen["mediaSlots"].append(
                        {
                            "kind": values.get("data-media-kind") or "",
                            "aspectRatio": values.get("data-aspect-ratio") or "",
                        }
                    )
                if "data-media-placeholder" in values:
                    self.current_screen["mediaPlaceholders"] += 1
                if values.get("data-media-state") == "missing":
                    self.current_screen["mediaMissingStates"] += 1

        if tag not in VOID_TAGS:
            self.depth += 1

    def handle_data(self, data: str) -> None:
        if self.current_direction is not None:
            self.current_direction["text"].append(data)
        if self.current_screen is not None:
            self.current_screen["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag not in VOID_TAGS and self.depth:
            self.depth -= 1
        if (
            self.current_screen is not None
            and self.depth == self.current_screen["rootDepth"]
        ):
            self.current_screen["text"] = clean_text(
                " ".join(self.current_screen["text"])
            )
            assert self.current_direction is not None
            self.current_direction["screens"].append(self.current_screen)
            self.current_screen = None
        if (
            self.current_direction is not None
            and self.depth == self.current_direction["rootDepth"]
        ):
            self.current_direction["text"] = clean_text(
                " ".join(self.current_direction["text"])
            )
            self.directions.append(self.current_direction)
            self.current_direction = None


def inferred_plan_path(html_path: Path) -> Path:
    return html_path.parent.parent / "exploration" / "design-plan.json"


def validate_content(
    request: dict,
    html_path: Path,
    plan: dict | None = None,
) -> list[str]:
    source = html_path.read_text(encoding="utf-8")
    parser = DirectionParser()
    parser.feed(source)
    settings = request.get("settings") or {}
    expected = int(settings.get("compareDirections", 1))
    fidelity = str(settings.get("fidelity", "mid"))
    output_level = request_output_level(request)
    interactive = bool(settings.get("interactive", False))
    required_screens = minimum_screens_for_request(request)
    errors: list[str] = []

    if parser.template_unresolved:
        errors.append("Artifact still has data-template-state=unresolved.")
    if parser.template_placeholders:
        errors.append(
            f"Artifact still has {parser.template_placeholders} template placeholder marker(s)."
        )
    lowered = source.casefold()
    found_markers = [
        marker for marker in PLACEHOLDER_MARKERS if marker in lowered
    ]
    if found_markers:
        errors.append(
            "Artifact contains starter or placeholder copy: "
            + ", ".join(found_markers)
            + "."
        )
    if re.search(r'data-design-status=["\']draft["\']', source, re.IGNORECASE):
        errors.append("Artifact data-design-status must be review-ready or visually-inspected.")
    if len(parser.directions) != expected:
        errors.append(
            f"Expected {expected} complete design directions, found {len(parser.directions)}."
        )

    plan_directions = {
        item["id"]: item for item in (plan or {}).get("directions", [])
    }
    seen_screens: set[str] = set()
    for direction in parser.directions:
        direction_id = direction["id"]
        if len(direction["hypothesis"].strip()) < 18:
            errors.append(
                f"Direction {direction_id} needs data-design-hypothesis with a concrete hypothesis."
            )
        screens = direction["screens"]
        if len(screens) < required_screens:
            errors.append(
                f"Direction {direction_id} needs at least {required_screens} screen(s) "
                f"or state(s) for outputLevel={output_level}; found {len(screens)}."
            )
        if direction["captions"] < len(screens):
            errors.append(
                f"Direction {direction_id} needs one data-screen-caption per screen."
            )
        if interactive and direction["controls"] < 1:
            errors.append(f"Direction {direction_id} has no interactive control.")
        if interactive and direction["prototypeStates"] < 1:
            errors.append(
                f"Direction {direction_id} needs a rendered data-prototype-state."
            )

        planned = plan_directions.get(direction_id)
        if plan is not None and planned is None:
            errors.append(f"Direction {direction_id} does not exist in the design plan.")
        planned_screens = {
            item["id"]: item for item in (planned or {}).get("screens", [])
        }
        for screen in screens:
            screen_id = screen["id"]
            if not screen_id:
                errors.append(f"Direction {direction_id} contains a screen without data-screen-id.")
                continue
            if screen_id in seen_screens:
                errors.append(f"Screen ID {screen_id} is duplicated.")
            seen_screens.add(screen_id)
            if len(screen["text"]) < (40 if fidelity == "low" else 80):
                errors.append(
                    f"Screen {screen_id} has insufficient realistic content density."
                )
            if not screen["requirementIds"]:
                errors.append(f"Screen {screen_id} has no data-requirement-ids.")
            if plan is not None:
                planned_screen = planned_screens.get(screen_id)
                if planned_screen is None:
                    errors.append(f"Screen {screen_id} does not exist in the design plan.")
                else:
                    planned_requirements = set(planned_screen.get("requirements", []))
                    actual_requirements = set(screen["requirementIds"])
                    if not planned_requirements.issubset(actual_requirements):
                        errors.append(
                            f"Screen {screen_id} does not trace all planned requirements."
                        )
                    if requires_media_contract(request):
                        media = planned_screen.get("mediaStructure") or {}
                        if media.get("required") is True:
                            expected_count = int(media.get("count", 1))
                            expected_kind = str(media.get("kind", ""))
                            expected_ratio = str(media.get("aspectRatio", ""))
                            matching_slots = [
                                slot
                                for slot in screen["mediaSlots"]
                                if slot["kind"] == expected_kind
                                and slot["aspectRatio"] == expected_ratio
                            ]
                            if len(matching_slots) < expected_count:
                                errors.append(
                                    f"Screen {screen_id} needs {expected_count} "
                                    f"{expected_kind} media slot(s) at {expected_ratio}; "
                                    f"found {len(matching_slots)}."
                                )
                            if (
                                output_level
                                in {"structural-wireframe", "detailed-wireframe"}
                                and screen["mediaPlaceholders"] < expected_count
                            ):
                                errors.append(
                                    f"Screen {screen_id} needs {expected_count} neutral "
                                    "data-media-placeholder skeleton(s)."
                                )
                            if (
                                media.get("showMissingState") is True
                                and screen["mediaMissingStates"] < 1
                            ):
                                errors.append(
                                    f"Screen {screen_id} needs a data-media-state=missing "
                                    "representation."
                                )

    if plan is not None:
        planned_screen_ids = {
            screen["id"]
            for direction in plan.get("directions", [])
            for screen in direction.get("screens", [])
        }
        missing = sorted(planned_screen_ids - seen_screens)
        if missing:
            errors.append(
                "Planned screens are missing from the artifact: " + ", ".join(missing) + "."
            )
    return errors


def safe_child(root: Path, relative: str) -> Path | None:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def parse_viewport(value: str) -> tuple[int, int] | None:
    match = re.fullmatch(r"(\d{2,5})x(\d{2,5})", value)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def validate_bundle(
    request: dict,
    html_path: Path,
    plan_path: Path,
) -> list[str]:
    errors: list[str] = []
    workdir = html_path.parent.parent
    if not plan_path.is_file():
        return [f"Design plan is missing: {plan_path}"]
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"Design plan is invalid JSON: {error}"]
    errors.extend(validate_plan(request, plan))
    errors.extend(validate_content(request, html_path, plan))

    reports = workdir / "reports"
    for name, minimum in REPORT_REQUIREMENTS.items():
        report = reports / name
        if not report.is_file():
            errors.append(f"Required report is missing: reports/{name}.")
            continue
        content = report.read_text(encoding="utf-8").strip()
        if len(content) < minimum:
            errors.append(f"Report reports/{name} is too incomplete.")
        if re.search(r"status:\s*draft", content, re.IGNORECASE):
            errors.append(f"Report reports/{name} still has Draft status.")

    renders = workdir / "renders"
    manifest_path = renders / "render-manifest.json"
    if not manifest_path.is_file():
        errors.append("Render manifest is missing: renders/render-manifest.json.")
        return errors
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        errors.append(f"Render manifest is invalid JSON: {error}.")
        return errors
    if manifest.get("schemaVersion") != 1:
        errors.append("Render manifest schemaVersion must be 1.")
    checks = manifest.get("checks")
    if not isinstance(checks, list):
        errors.append("Render manifest checks must be a list.")
        return errors

    expected_pairs = {
        (direction["id"], viewport)
        for direction in plan.get("directions", [])
        for viewport in request.get("settings", {}).get("viewports", [])
    }
    recorded_pairs: set[tuple[str, str]] = set()
    for index, check in enumerate(checks, start=1):
        if not isinstance(check, dict):
            errors.append(f"Render check {index} must be an object.")
            continue
        pair = (str(check.get("directionId", "")), str(check.get("viewport", "")))
        if pair in recorded_pairs:
            errors.append(
                f"Render check is duplicated for {pair[0]} at {pair[1]}."
            )
        recorded_pairs.add(pair)
        if check.get("inspected") is not True:
            errors.append(
                f"Render {pair[0]} at {pair[1]} was not marked inspected."
            )
        if len(str(check.get("notes", "")).strip()) < 12:
            errors.append(
                f"Render {pair[0]} at {pair[1]} needs concrete inspection notes."
            )
        image = safe_child(renders, str(check.get("image", "")))
        if image is None or not image.is_file():
            errors.append(
                f"Render image is missing or outside renders/: {check.get('image', '')}."
            )
            continue
        if image.stat().st_size < 128:
            errors.append(f"Render image is too small: {image.name}.")
            continue
        dimensions = image_dimensions(image)
        if dimensions is None:
            errors.append(f"Render image is not a readable PNG or JPEG: {image.name}.")
            continue
        viewport = parse_viewport(pair[1])
        if viewport is not None:
            scale = dimensions[0] / viewport[0]
            if not any(abs(scale - candidate) < 0.08 for candidate in (1, 2, 3)):
                errors.append(
                    f"Render {image.name} width does not match viewport {pair[1]} "
                    "at 1x, 2x, or 3x."
                )
            if dimensions[1] < viewport[1] * min(scale, 1):
                errors.append(
                    f"Render {image.name} is shorter than the requested viewport."
                )

    missing_pairs = sorted(expected_pairs - recorded_pairs)
    if missing_pairs:
        errors.append(
            "Required renders are missing: "
            + ", ".join(f"{direction}@{viewport}" for direction, viewport in missing_pairs)
            + "."
        )
    unexpected_pairs = sorted(recorded_pairs - expected_pairs)
    if unexpected_pairs:
        errors.append(
            "Render manifest contains unexpected checks: "
            + ", ".join(f"{direction}@{viewport}" for direction, viewport in unexpected_pairs)
            + "."
        )
    return errors


def validate(
    request_path: Path,
    html_path: Path,
    plan_path: Path | None = None,
    require_bundle: bool = False,
) -> list[str]:
    request = json.loads(request_path.read_text(encoding="utf-8"))
    if require_bundle:
        return validate_bundle(
            request,
            html_path,
            plan_path or inferred_plan_path(html_path),
        )
    plan = None
    candidate = plan_path or inferred_plan_path(html_path)
    if candidate.is_file():
        plan = json.loads(candidate.read_text(encoding="utf-8"))
    return validate_content(request, html_path, plan)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    parser.add_argument("html", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument(
        "--content-only",
        action="store_true",
        help="Skip reports and render evidence. Never use when marking ready.",
    )
    args = parser.parse_args()
    errors = validate(
        args.request,
        args.html,
        plan_path=args.plan,
        require_bundle=not args.content_only,
    )
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS quality-first delivery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
