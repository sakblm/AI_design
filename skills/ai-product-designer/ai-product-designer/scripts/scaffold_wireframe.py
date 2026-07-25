#!/usr/bin/env python3
"""Create a request-specific unresolved review board from a validated design plan."""

from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

from validate_design_plan import validate_plan


def escaped(value: object) -> str:
    return html.escape(str(value), quote=True)


def replace_allowed(index_path: Path) -> bool:
    if not index_path.exists():
        return True
    existing = index_path.read_text(encoding="utf-8")
    return 'data-template-state="unresolved"' in existing


def render(request: dict, plan: dict) -> str:
    title = escaped(request.get("title", "Design proposal"))
    prompt = escaped(request.get("prompt", ""))
    directions = plan["directions"]
    requirement_map = {
        item["id"]: item["statement"] for item in plan.get("requirements", [])
    }
    nav = "\n".join(
        f'      <a href="#{escaped(direction["id"])}">{escaped(direction["name"])}</a>'
        for direction in directions
    )
    sections: list[str] = []
    for index, direction in enumerate(directions, start=1):
        solves = "\n".join(
            f"          <li>{escaped(requirement_map.get(item, item))}</li>"
            for item in direction["solves"]
        )
        screens: list[str] = []
        for screen_index, screen in enumerate(direction["screens"], start=1):
            requirement_ids = " ".join(screen["requirements"])
            media = screen.get("mediaStructure") or {}
            media_hint = ""
            if media.get("required") is True:
                slot_count = int(media.get("count", 1))
                media_slots = "\n".join(
                    f"""              <div
                class="media-placeholder"
                data-media-slot
                data-media-placeholder
                data-media-kind="{escaped(media.get("kind", "image"))}"
                data-aspect-ratio="{escaped(media.get("aspectRatio", "4:3"))}"
                aria-label="{escaped(media.get("role", "画像枠"))} {slot_index + 1}"
              >
                {escaped(media.get("kind", "image"))} {slot_index + 1}
                / {escaped(media.get("aspectRatio", "4:3"))}
              </div>"""
                    for slot_index in range(slot_count)
                )
                missing_hint = (
                    '<p data-media-state="missing">画像なし状態も実装する</p>'
                    if media.get("showMissingState") is True
                    else ""
                )
                media_hint = f"""
{media_slots}
              {missing_hint}"""
            screens.append(
                f"""        <figure class="screen-note">
          <div
            class="device"
            data-wireframe-screen
            data-screen-id="{escaped(screen["id"])}"
            data-requirement-ids="{escaped(requirement_ids)}"
            data-template-placeholder="screen-content"
          >
            <div class="screen-placeholder">
              <div>
                <strong>{escaped(screen["name"])}</strong>
                <p>ここに画面を実装：{escaped(screen["userDecision"])}</p>
                {media_hint}
              </div>
            </div>
          </div>
          <figcaption class="screen-caption" data-screen-caption>
            <strong>{screen_index:02d}. {escaped(screen["name"])}</strong><br>
            {escaped(screen["userDecision"])} / State: {escaped(screen["state"])}
          </figcaption>
        </figure>"""
            )
        risk_text = " / ".join(str(item) for item in direction["risks"])
        sections.append(
            f"""    <section
      class="design-direction"
      id="{escaped(direction["id"])}"
      data-design-direction="{escaped(direction["id"])}"
      data-design-hypothesis="{escaped(direction["hypothesis"])}"
    >
      <div class="direction-heading">
        <p class="direction-id">Direction {index:02d}</p>
        <h2>{escaped(direction["name"])}</h2>
        <p class="direction-hypothesis">{escaped(direction["hypothesis"])}</p>
        <ul class="solves-list" aria-label="この方向が解決する要件">
{solves}
        </ul>
      </div>
      <div class="screen-row">
{chr(10).join(screens)}
      </div>
      <div class="direction-tradeoffs">
        <article>
          <h3>設計戦略</h3>
          <p>{escaped(direction["strategy"])}</p>
        </article>
        <article>
          <h3>リスク</h3>
          <p>{escaped(risk_text)}</p>
        </article>
      </div>
    </section>"""
        )
    return f"""<!doctype html>
<html lang="ja" data-design-status="draft">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="./styles.css">
    <script src="./app.js" defer></script>
  </head>
  <body data-template-state="unresolved">
    <header class="artifact-header">
      <p class="artifact-label">AI Product Designer / design proposal</p>
      <h1>{title}</h1>
      <p>{prompt}</p>
    </header>
    <nav class="direction-index" aria-label="提案方向">
{nav}
    </nav>
    <main class="review-board">
{chr(10).join(sections)}
    </main>
  </body>
</html>
"""


def scaffold(request_path: Path, plan_path: Path, output: Path) -> Path:
    request = json.loads(request_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    errors = validate_plan(request, plan)
    if errors:
        raise ValueError("\n".join(errors))

    output = output.resolve()
    index_path = output / "index.html"
    if not replace_allowed(index_path):
        raise FileExistsError(
            f"Refusing to replace a resolved wireframe: {index_path}"
        )
    kit = Path(__file__).resolve().parent.parent / "assets" / "wireframe-kit"
    output.mkdir(parents=True, exist_ok=True)
    for name in ("styles.css", "app.js"):
        shutil.copy2(kit / name, output / name)
    index_path.write_text(render(request, plan), encoding="utf-8")
    return index_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        path = scaffold(args.request, args.plan, args.output)
    except (ValueError, FileExistsError) as error:
        print(f"FAIL {error}")
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
