#!/usr/bin/env python3
"""Validate the evidence-to-screen design plan used by quality-first generation."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_FIDELITY = {"low", "mid", "high"}
VALID_MEDIA_KINDS = {"image", "gallery", "avatar", "map", "video"}
MEDIA_EVIDENCE_PATTERN = re.compile(
    r"画像|写真|サムネイル|ギャラリー|アバター|地図|動画|image|photo|thumbnail|gallery|avatar|map|video",
    re.IGNORECASE,
)
OUTPUT_LEVEL_SCREEN_MINIMUM = {
    "structural-wireframe": 1,
    "detailed-wireframe": 2,
    "ui-mockup": 3,
}
PLACEHOLDER_MARKERS = (
    "todo",
    "tbd",
    "placeholder",
    "replace with",
    "state the",
    "ここに",
    "仮テキスト",
    "未定義",
)


def minimum_screens(fidelity: str) -> int:
    return {"low": 1, "mid": 2, "high": 3}.get(fidelity, 2)


def request_output_level(request: dict) -> str:
    settings = request.get("settings") or {}
    configured = str(settings.get("outputLevel", "")).strip()
    if configured in OUTPUT_LEVEL_SCREEN_MINIMUM:
        return configured
    project_type = str((request.get("projectType") or {}).get("id", "")).strip()
    fidelity = str(settings.get("fidelity", "mid")).strip()
    if project_type == "ui-mockup" or fidelity == "high":
        return "ui-mockup"
    if fidelity == "low":
        return "structural-wireframe"
    return "detailed-wireframe"


def minimum_screens_for_request(request: dict) -> int:
    return OUTPUT_LEVEL_SCREEN_MINIMUM[request_output_level(request)]


def requires_media_contract(request: dict) -> bool:
    return request_output_level(request) in OUTPUT_LEVEL_SCREEN_MINIMUM


def nonempty(value: Any, minimum: int = 1) -> bool:
    return isinstance(value, str) and len(value.strip()) >= minimum


def contains_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.casefold()
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def normalized(value: str) -> str:
    return re.sub(r"[\W_]+", "", value.casefold(), flags=re.UNICODE)


def validate_plan(request: dict, plan: dict) -> list[str]:
    errors: list[str] = []
    settings = request.get("settings") or {}
    output_level = request_output_level(request)
    expected_directions = int(settings.get("compareDirections", 1))
    required_screens = minimum_screens_for_request(request)

    if plan.get("schemaVersion") != 1:
        errors.append("Design plan schemaVersion must be 1.")
    for key, label in (
        ("problemStatement", "problemStatement"),
        ("primaryUserDecision", "primaryUserDecision"),
    ):
        value = plan.get(key)
        if not nonempty(value, 12):
            errors.append(f"Design plan {label} must contain a concrete statement.")
        elif contains_placeholder(value):
            errors.append(f"Design plan {label} contains placeholder copy.")

    evidence = plan.get("evidenceSummary")
    request_evidence = request.get("evidencePaths") or []
    if request_evidence and (not isinstance(evidence, list) or not evidence):
        errors.append("Design plan must summarize supplied evidence.")
    if evidence is None:
        evidence = []
    if not isinstance(evidence, list):
        errors.append("Design plan evidenceSummary must be a list.")
        evidence = []

    evidence_ids: set[str] = set()
    for index, item in enumerate(evidence, start=1):
        if not isinstance(item, dict):
            errors.append(f"Evidence item {index} must be an object.")
            continue
        evidence_id = str(item.get("id", "")).strip()
        if not re.fullmatch(r"E[1-9][0-9]*", evidence_id):
            errors.append(f"Evidence item {index} needs an ID such as E1.")
        elif evidence_id in evidence_ids:
            errors.append(f"Evidence ID {evidence_id} is duplicated.")
        evidence_ids.add(evidence_id)
        if not nonempty(item.get("source"), 2):
            errors.append(f"Evidence {evidence_id or index} needs a source.")
        if not nonempty(item.get("observation"), 12):
            errors.append(f"Evidence {evidence_id or index} needs a concrete observation.")
        if item.get("confidence") not in VALID_CONFIDENCE:
            errors.append(
                f"Evidence {evidence_id or index} confidence must be high, medium, or low."
            )

    requirements = plan.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        errors.append("Design plan must contain at least one requirement.")
        requirements = []
    requirement_ids: set[str] = set()
    for index, item in enumerate(requirements, start=1):
        if not isinstance(item, dict):
            errors.append(f"Requirement {index} must be an object.")
            continue
        requirement_id = str(item.get("id", "")).strip()
        if not re.fullmatch(r"R[1-9][0-9]*", requirement_id):
            errors.append(f"Requirement {index} needs an ID such as R1.")
        elif requirement_id in requirement_ids:
            errors.append(f"Requirement ID {requirement_id} is duplicated.")
        requirement_ids.add(requirement_id)
        statement = item.get("statement")
        if not nonempty(statement, 12):
            errors.append(f"Requirement {requirement_id or index} needs a testable statement.")
        elif contains_placeholder(statement):
            errors.append(f"Requirement {requirement_id or index} contains placeholder copy.")
        sources = item.get("sources") or []
        if evidence_ids and (
            not isinstance(sources, list)
            or not sources
            or any(source not in evidence_ids for source in sources)
        ):
            errors.append(
                f"Requirement {requirement_id or index} must reference valid evidence IDs."
            )

    directions = plan.get("directions")
    if not isinstance(directions, list):
        errors.append("Design plan directions must be a list.")
        directions = []
    if len(directions) != expected_directions:
        errors.append(
            f"Expected {expected_directions} design directions, found {len(directions)}."
        )

    direction_ids: set[str] = set()
    screen_ids: set[str] = set()
    strategies: set[str] = set()
    covered_requirements: set[str] = set()
    media_required_screens = 0
    for index, direction in enumerate(directions, start=1):
        if not isinstance(direction, dict):
            errors.append(f"Direction {index} must be an object.")
            continue
        direction_id = str(direction.get("id", "")).strip()
        if not re.fullmatch(r"direction-[a-z0-9-]+", direction_id):
            errors.append(
                f"Direction {index} needs a stable ID such as direction-a."
            )
        elif direction_id in direction_ids:
            errors.append(f"Direction ID {direction_id} is duplicated.")
        direction_ids.add(direction_id)

        for key, minimum, label in (
            ("name", 4, "name"),
            ("hypothesis", 18, "hypothesis"),
            ("strategy", 18, "strategy"),
        ):
            value = direction.get(key)
            if not nonempty(value, minimum):
                errors.append(
                    f"Direction {direction_id or index} needs a concrete {label}."
                )
            elif contains_placeholder(value):
                errors.append(
                    f"Direction {direction_id or index} {label} contains placeholder copy."
                )
        strategy = normalized(str(direction.get("strategy", "")))
        if strategy:
            if strategy in strategies:
                errors.append(
                    f"Direction {direction_id or index} repeats another direction's strategy."
                )
            strategies.add(strategy)

        solves = direction.get("solves")
        if (
            not isinstance(solves, list)
            or not solves
            or any(item not in requirement_ids for item in solves)
        ):
            errors.append(
                f"Direction {direction_id or index} must solve valid requirement IDs."
            )
        else:
            covered_requirements.update(solves)
        risks = direction.get("risks")
        if not isinstance(risks, list) or not any(nonempty(item, 8) for item in risks):
            errors.append(f"Direction {direction_id or index} needs a concrete risk.")

        screens = direction.get("screens")
        if not isinstance(screens, list):
            errors.append(f"Direction {direction_id or index} screens must be a list.")
            screens = []
        if len(screens) < required_screens:
            errors.append(
                f"Direction {direction_id or index} needs at least {required_screens} "
                f"screen(s) or state(s) for outputLevel={output_level}."
            )
        for screen_index, screen in enumerate(screens, start=1):
            if not isinstance(screen, dict):
                errors.append(
                    f"Direction {direction_id or index} screen {screen_index} must be an object."
                )
                continue
            screen_id = str(screen.get("id", "")).strip()
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", screen_id):
                errors.append(
                    f"Direction {direction_id or index} screen {screen_index} needs a stable ID."
                )
            elif screen_id in screen_ids:
                errors.append(f"Screen ID {screen_id} is duplicated.")
            screen_ids.add(screen_id)
            if not nonempty(screen.get("name"), 3):
                errors.append(f"Screen {screen_id or screen_index} needs a name.")
            decision = screen.get("userDecision")
            if not nonempty(decision, 12):
                errors.append(
                    f"Screen {screen_id or screen_index} needs a concrete userDecision."
                )
            elif contains_placeholder(decision):
                errors.append(
                    f"Screen {screen_id or screen_index} userDecision contains placeholder copy."
                )
            if not nonempty(screen.get("state"), 3):
                errors.append(f"Screen {screen_id or screen_index} needs a state.")
            screen_requirements = screen.get("requirements")
            if (
                not isinstance(screen_requirements, list)
                or not screen_requirements
                or any(item not in requirement_ids for item in screen_requirements)
            ):
                errors.append(
                    f"Screen {screen_id or screen_index} must reference valid requirement IDs."
                )
            if requires_media_contract(request):
                media = screen.get("mediaStructure")
                if not isinstance(media, dict):
                    errors.append(
                        f"Screen {screen_id or screen_index} needs a mediaStructure decision."
                    )
                elif not isinstance(media.get("required"), bool):
                    errors.append(
                        f"Screen {screen_id or screen_index} mediaStructure.required "
                        "must be true or false."
                    )
                elif media["required"]:
                    media_required_screens += 1
                    if not nonempty(media.get("role"), 8):
                        errors.append(
                            f"Screen {screen_id or screen_index} mediaStructure needs "
                            "a concrete role."
                        )
                    if media.get("kind") not in VALID_MEDIA_KINDS:
                        errors.append(
                            f"Screen {screen_id or screen_index} mediaStructure.kind "
                            "must be image, gallery, avatar, map, or video."
                        )
                    count = media.get("count")
                    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 12:
                        errors.append(
                            f"Screen {screen_id or screen_index} mediaStructure.count "
                            "must be an integer from 1 to 12."
                        )
                    ratio = str(media.get("aspectRatio", "")).strip()
                    if not re.fullmatch(r"[1-9][0-9]*:[1-9][0-9]*", ratio):
                        errors.append(
                            f"Screen {screen_id or screen_index} mediaStructure.aspectRatio "
                            "must use a ratio such as 4:3 or 1:1."
                        )
                    if not isinstance(media.get("showMissingState"), bool):
                        errors.append(
                            f"Screen {screen_id or screen_index} "
                            "mediaStructure.showMissingState must be true or false."
                        )
                elif not nonempty(media.get("reason"), 8):
                    errors.append(
                        f"Screen {screen_id or screen_index} needs a concrete reason "
                        "when mediaStructure.required is false."
                    )

    if requires_media_contract(request):
        evidence_mentions_media = any(
            isinstance(item, dict)
            and MEDIA_EVIDENCE_PATTERN.search(
                " ".join(
                    str(item.get(key, ""))
                    for key in ("source", "observation")
                )
            )
            for item in evidence
        )
        if evidence_mentions_media and media_required_screens == 0:
            decision = plan.get("mediaDecision")
            deliberate_removal = (
                isinstance(decision, dict)
                and decision.get("removeObservedMedia") is True
                and nonempty(decision.get("reason"), 18)
            )
            if not deliberate_removal:
                errors.append(
                    "Supplied evidence contains media structure, but no screen preserves it. "
                    "Add a required mediaStructure or a concrete mediaDecision explaining "
                    "why observed media is removed."
                )

    missing_coverage = sorted(requirement_ids - covered_requirements)
    if missing_coverage:
        errors.append(
            "Requirements are not covered by any direction: "
            + ", ".join(missing_coverage)
            + "."
        )

    recommendation = str(plan.get("recommendedDirection", "")).strip()
    if recommendation not in direction_ids:
        errors.append("recommendedDirection must reference an existing direction ID.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    errors = validate_plan(request, plan)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS design plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
