#!/usr/bin/env python3
"""Run the local AI Product Designer console and its filesystem API."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs, quote, unquote, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from create_single_file_html import create_single_file_html


SKIP_DIRECTORIES = {".git", ".svn", ".hg", "node_modules", "dist", "build", "__pycache__"}
MAX_INVENTORY_FILES = 5000
MAX_REFERENCE_FILE_BYTES = 50 * 1024 * 1024
VALID_FIDELITIES = {"n/a", "low", "mid", "high"}
OUTPUT_LEVEL_MAP = {
    "structural-wireframe": ("wireframe", "low"),
    "detailed-wireframe": ("wireframe", "mid"),
    "ui-mockup": ("ui-mockup", "high"),
}
OUTPUT_LEVEL_BY_CONFIGURATION = {
    value: key for key, value in OUTPUT_LEVEL_MAP.items()
}
VALID_STATUS = {"active", "evaluation", "deprecated"}
VALID_REQUEST_STATUS = {"queued", "generating", "ready", "error"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(payload)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def slugify(value: str) -> str:
    ascii_slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if ascii_slug:
        return ascii_slug[:64]
    return "design-system"


def unique_id(preferred: str, existing: set[str]) -> str:
    base = slugify(preferred)
    candidate = base
    suffix = 2
    while candidate in existing:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def inventory_path(source: Path) -> dict:
    extensions: Counter[str] = Counter()
    sample_files: list[str] = []
    count = 0
    roots = [source] if source.is_file() else source.rglob("*")
    for candidate in roots:
        if source.is_dir() and any(part in SKIP_DIRECTORIES for part in candidate.parts):
            continue
        if not candidate.is_file():
            continue
        count += 1
        extension = candidate.suffix.lower() or "[no extension]"
        extensions[extension] += 1
        if len(sample_files) < 30:
            try:
                sample_files.append(str(candidate.relative_to(source)))
            except ValueError:
                sample_files.append(candidate.name)
        if count >= MAX_INVENTORY_FILES:
            break
    return {
        "fileCount": count,
        "truncated": count >= MAX_INVENTORY_FILES,
        "extensions": dict(extensions.most_common()),
        "sampleFiles": sample_files,
    }


class ConsoleApp:
    def __init__(self, workspace: Path, skill_dir: Path):
        self.workspace = workspace.resolve()
        self.skill_dir = skill_dir.resolve()
        self.static_dir = self.skill_dir / "assets" / "design-console"
        self.wireframe_kit = self.skill_dir / "assets" / "wireframe-kit"
        self.registry_path = self.workspace / "design-systems" / "registry.json"
        self.catalog_path = self.workspace / "project-types" / "catalog.json"
        self.requests_dir = self.workspace / "requests"
        self.work_dir = self.workspace / "work"
        self.exports_dir = self.workspace / "exports"
        self.uploads_dir = self.workspace / ".design-console" / "uploads"
        self.project_path = self.workspace / "project.json"

    def bootstrap(self) -> dict:
        registry = read_json(self.registry_path)
        catalog = read_json(self.catalog_path)
        requests = []
        if self.requests_dir.exists():
            for item in sorted(self.requests_dir.glob("*.json"), reverse=True)[:12]:
                try:
                    request = read_json(item)
                    self._ensure_request_locations(request, item)
                    requests.append(request)
                except (OSError, json.JSONDecodeError):
                    continue
        project = self._project()
        return {
            "workspace": {
                "path": str(self.workspace),
                "name": project.get("name", self.workspace.name),
                "activeRequestId": project.get("activeRequestId"),
                "lastDesignSystemId": project.get("lastDesignSystemId"),
            },
            "designSystems": registry.get("items", []),
            "projectTypes": catalog.get("items", []),
            "requests": requests,
        }

    def _project(self) -> dict:
        if self.project_path.exists():
            try:
                return read_json(self.project_path)
            except (OSError, json.JSONDecodeError):
                pass
        return {"name": self.workspace.name, "activeRequestId": None}

    def _ensure_request_locations(self, request: dict, request_path: Path | None = None) -> None:
        request_id = str(request.get("id", "")).strip()
        if not request_id:
            return
        locations = request.setdefault("locations", {})
        locations.setdefault("request", f"requests/{request_path.name if request_path else request_id + '.json'}")
        locations.setdefault("workspace", f"work/{request_id}")
        if request.get("status") == "ready" and not request.get("result", {}).get(
            "entrypoint"
        ):
            for entrypoint in ("wireframe/index.html", "output/index.html"):
                if (self.work_dir / request_id / entrypoint).is_file():
                    request["result"] = {
                        "entrypoint": entrypoint,
                        "previewUrl": f"/preview/{request_id}/{entrypoint}",
                        "downloadUrl": f"/api/requests/{request_id}/export",
                    }
                    break

    def register_design_system(self, payload: dict) -> dict:
        name = str(payload.get("name", "")).strip()
        source_raw = str(payload.get("sourcePath", "")).strip()
        description = str(payload.get("description", "")).strip()
        status = str(payload.get("status", "active")).strip()
        if not name:
            raise ValueError("デザインシステム名を入力してください。")
        if not source_raw:
            raise ValueError("ローカルフォルダまたはファイルのパスを入力してください。")
        if status not in VALID_STATUS:
            raise ValueError("無効なステータスです。")
        source = Path(source_raw).expanduser().resolve()
        if not source.exists():
            raise ValueError(f"参照先が見つかりません: {source}")

        registry = read_json(self.registry_path)
        items = registry.setdefault("items", [])
        existing_ids = {str(item.get("id")) for item in items}
        design_system_id = unique_id(str(payload.get("id") or name), existing_ids)
        now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        record = {
            "id": design_system_id,
            "name": name,
            "sourcePath": str(source),
            "status": status,
            "description": description,
            "createdAt": now,
            "updatedAt": now,
            "inventory": inventory_path(source),
        }
        items.append(record)
        write_json_atomic(self.registry_path, registry)
        return record

    def store_reference_file(self, batch: str, relative_path: str, payload: bytes) -> dict:
        if not re.fullmatch(r"[a-zA-Z0-9-]{1,64}", batch):
            raise ValueError("資料アップロードの識別子が不正です。")
        normalized = PurePosixPath(str(relative_path).replace("\\", "/"))
        if normalized.is_absolute() or not normalized.parts or any(
            part in {"", ".", ".."} for part in normalized.parts
        ):
            raise ValueError("資料の相対パスが不正です。")
        target = (self.uploads_dir / batch / Path(*normalized.parts)).resolve()
        try:
            target.relative_to(self.uploads_dir.resolve())
        except ValueError as error:
            raise ValueError("資料の保存先が不正です。") from error
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("wb", dir=target.parent, delete=False) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        os.replace(temp_path, target)
        return {
            "name": target.name,
            "path": target.relative_to(self.workspace).as_posix(),
            "size": len(payload),
        }

    def create_request(self, payload: dict) -> dict:
        title = str(payload.get("title", "")).strip()
        design_system_id = str(payload.get("designSystemId", "")).strip()
        project_type_id = str(payload.get("projectTypeId", "")).strip()
        prompt = str(payload.get("prompt", "")).strip()
        fidelity = str(payload.get("fidelity", "mid")).strip()
        output_level = str(payload.get("outputLevel", "")).strip()
        if output_level:
            mapped = OUTPUT_LEVEL_MAP.get(output_level)
            if mapped is None:
                raise ValueError("仕上がりレベルが不正です。")
            mapped_project_type, mapped_fidelity = mapped
            if project_type_id and project_type_id != mapped_project_type:
                raise ValueError("制作タイプと仕上がりレベルが一致していません。")
            project_type_id = mapped_project_type
            fidelity = mapped_fidelity
        viewports = payload.get("viewports", [])
        compare_directions = int(payload.get("compareDirections", 3))
        uploaded_evidence_paths = payload.get("uploadedEvidencePaths", [])

        if not title:
            raise ValueError("案件名を入力してください。")
        if not prompt:
            raise ValueError("何を作るか入力してください。")
        if fidelity not in VALID_FIDELITIES:
            raise ValueError("無効なfidelityです。")
        if not isinstance(viewports, list) or not viewports:
            raise ValueError("対象画面サイズを1つ以上指定してください。")
        if compare_directions < 1 or compare_directions > 5:
            raise ValueError("比較案数は1〜5で指定してください。")
        if not isinstance(uploaded_evidence_paths, list):
            raise ValueError("アップロード資料の指定が不正です。")

        registry = read_json(self.registry_path)
        catalog = read_json(self.catalog_path)
        design_system = next(
            (item for item in registry.get("items", []) if item.get("id") == design_system_id),
            None,
        )
        project_type = next(
            (item for item in catalog.get("items", []) if item.get("id") == project_type_id),
            None,
        )
        if not design_system:
            raise ValueError("登録済みデザインシステムを選択してください。")
        if not project_type:
            raise ValueError("制作タイプを選択してください。")
        if project_type.get("availability") == "planned":
            raise ValueError(f"{project_type['name']}は現在準備中です。")
        allowed_fidelity = set(project_type.get("fidelity", []))
        if fidelity not in allowed_fidelity:
            raise ValueError(f"{project_type['name']}ではfidelity={fidelity}を選択できません。")
        if not output_level:
            output_level = OUTPUT_LEVEL_BY_CONFIGURATION.get(
                (project_type_id, fidelity), "n/a"
            )

        now = datetime.now(timezone.utc).astimezone()
        request_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{slugify(title)}"
        request = {
            "schemaVersion": 5,
            "id": request_id,
            "title": title,
            "status": "queued",
            "createdAt": now.isoformat(timespec="seconds"),
            "updatedAt": now.isoformat(timespec="seconds"),
            "designSystem": {
                "id": design_system["id"],
                "name": design_system["name"],
                "sourcePath": design_system["sourcePath"],
            },
            "projectType": {
                "id": project_type["id"],
                "name": project_type["name"],
                "artifact": project_type["artifact"],
                "availability": project_type.get("availability", "beta"),
            },
            "settings": {
                "outputLevel": output_level,
                "fidelity": fidelity,
                "viewports": [str(item).strip() for item in viewports if str(item).strip()],
                "compareDirections": compare_directions,
                "interactive": bool(payload.get("interactive", False)),
                "allowGoogleFonts": bool(payload.get("allowGoogleFonts", False)),
                "qualityProfile": "quality-first-v0.5-media-structure",
            },
            "prompt": prompt,
            "evidencePaths": [
                str(item).strip()
                for item in payload.get("evidencePaths", [])
                if str(item).strip()
            ],
            "locations": {
                "request": f"requests/{request_id}.json",
                "workspace": f"work/{request_id}",
            },
        }

        self.requests_dir.mkdir(parents=True, exist_ok=True)
        request_path = self.requests_dir / f"{request_id}.json"
        if request_path.exists():
            raise FileExistsError(f"案件設定がすでに存在します: {request_path}")
        write_json_atomic(request_path, request)

        workspace_path = self.work_dir / request_id
        self._create_work_area(
            workspace_path,
            request,
            request_path,
            [str(item).strip() for item in uploaded_evidence_paths if str(item).strip()],
        )
        write_json_atomic(request_path, request)
        self._set_active_request(request_id, design_system["id"])
        return request

    def _create_work_area(
        self,
        output: Path,
        request: dict,
        request_path: Path,
        uploaded_evidence_paths: list[str] | None = None,
    ) -> None:
        if output.exists():
            raise FileExistsError(f"制作ワークスペースがすでに存在します: {output}")
        output.mkdir(parents=True)
        for name in ("evidence", "design-system", "exploration", "renders", "reports"):
            (output / name).mkdir()
        if request["projectType"]["artifact"] in {"html", "html-spec"}:
            shutil.copytree(self.wireframe_kit, output / "wireframe")
        else:
            (output / "output").mkdir()
        copied_evidence = self._copy_uploaded_evidence(
            output / "evidence", uploaded_evidence_paths or []
        )
        request["evidencePaths"].extend(copied_evidence)
        write_json_atomic(output / "design-request.json", request)
        write_json_atomic(
            output / "status.json",
            {
                "requestId": request["id"],
                "status": request["status"],
                "updatedAt": request["updatedAt"],
                "message": "Codexの制作開始を待っています。",
            },
        )
        source_note = {
            "designSystemId": request["designSystem"]["id"],
            "name": request["designSystem"]["name"],
            "sourcePath": request["designSystem"]["sourcePath"],
            "copyPolicy": "reference-only",
        }
        write_json_atomic(output / "design-system" / "source.json", source_note)
        brief = (
            f"# {request['title']}\n\n"
            "Status: Queued\n\n"
            f"- Design system: {request['designSystem']['name']}\n"
            f"- Project type: {request['projectType']['name']}\n"
            f"- Output level: {request['settings']['outputLevel']}\n"
            f"- Internal fidelity: {request['settings']['fidelity']}\n"
            f"- Viewports: {', '.join(request['settings']['viewports'])}\n\n"
            "## Request\n\n"
            f"{request['prompt']}\n"
        )
        (output / "brief.md").write_text(brief, encoding="utf-8")

    def _request_path(self, request_id: str) -> Path:
        if not re.fullmatch(r"[a-zA-Z0-9-]{1,160}", request_id):
            raise ValueError("案件IDが不正です。")
        return self.requests_dir / f"{request_id}.json"

    def _load_request(self, request_id: str) -> tuple[dict, Path]:
        path = self._request_path(request_id)
        if not path.is_file():
            raise ValueError(f"案件が見つかりません: {request_id}")
        request = read_json(path)
        self._ensure_request_locations(request, path)
        return request, path

    def _set_active_request(
        self, request_id: str, design_system_id: str | None = None
    ) -> None:
        project = self._project()
        project.setdefault("schemaVersion", 1)
        project.setdefault("name", self.workspace.name)
        project.setdefault(
            "createdAt",
            datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        )
        project["activeRequestId"] = request_id
        if design_system_id:
            project["lastDesignSystemId"] = design_system_id
        project["updatedAt"] = (
            datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        )
        write_json_atomic(self.project_path, project)

    def _sync_request(self, request: dict, message: str = "") -> None:
        now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        request["updatedAt"] = now
        request_path = self._request_path(request["id"])
        write_json_atomic(request_path, request)
        workspace_path = self.work_dir / request["id"]
        write_json_atomic(workspace_path / "design-request.json", request)
        status_payload = {
            "requestId": request["id"],
            "status": request["status"],
            "updatedAt": now,
            "message": message or request.get("statusMessage", ""),
            "result": request.get("result"),
        }
        write_json_atomic(workspace_path / "status.json", status_payload)

    def claim_next_request(self) -> dict | None:
        if not self.requests_dir.exists():
            return None
        for path in sorted(self.requests_dir.glob("*.json")):
            try:
                request = read_json(path)
            except (OSError, json.JSONDecodeError):
                continue
            if request.get("status") != "queued":
                continue
            request["status"] = "generating"
            request["claimedAt"] = (
                datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
            )
            request["statusMessage"] = "Codexが制作しています。"
            self._sync_request(request, request["statusMessage"])
            self._set_active_request(request["id"])
            return request
        return None

    def update_request_status(
        self,
        request_id: str,
        status: str,
        message: str = "",
        entrypoint: str | None = None,
    ) -> dict:
        if status not in VALID_REQUEST_STATUS:
            raise ValueError("案件ステータスが不正です。")
        request, _ = self._load_request(request_id)
        if status == "ready" and not entrypoint:
            entrypoint = request.get("result", {}).get("entrypoint")
            if not entrypoint:
                raise ValueError("readyにするにはプレビューの相対パスが必要です。")
        request["status"] = status
        request["statusMessage"] = message
        if entrypoint:
            normalized = PurePosixPath(entrypoint.replace("\\", "/"))
            if normalized.is_absolute() or any(
                part in {"", ".", ".."} for part in normalized.parts
            ):
                raise ValueError("プレビューの相対パスが不正です。")
            candidate = (self.work_dir / request_id / Path(*normalized.parts)).resolve()
            try:
                candidate.relative_to((self.work_dir / request_id).resolve())
            except ValueError as error:
                raise ValueError("プレビューの保存先が不正です。") from error
            if status == "ready" and not candidate.is_file():
                raise ValueError(f"プレビューが見つかりません: {entrypoint}")
            request["result"] = {
                "entrypoint": normalized.as_posix(),
                "previewUrl": f"/preview/{request_id}/{normalized.as_posix()}",
                "downloadUrl": f"/api/requests/{request_id}/export",
            }
        if status == "ready":
            if request.get("projectType", {}).get("id") == "wireframe":
                self._assert_wireframe_ready(
                    request,
                    self.work_dir
                    / request_id
                    / request["result"]["entrypoint"],
                )
            request["completedAt"] = (
                datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
            )
        self._sync_request(request, message)
        self._set_active_request(request_id)
        return request

    def _assert_wireframe_ready(self, request: dict, html_path: Path) -> None:
        validator = self.skill_dir / "scripts" / "validate_delivery.py"
        request_path = self._request_path(request["id"])
        quality = subprocess.run(
            [sys.executable, str(validator), str(request_path), str(html_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if quality.returncode:
            detail = (quality.stdout or quality.stderr).strip()
            raise ValueError(f"品質ゲートを通過していません。\n{detail}")

        node = shutil.which("node")
        if not node:
            raise ValueError("品質ゲートに必要なNode.jsが見つかりません。")
        static_validator = self.skill_dir / "scripts" / "validate_wireframe.mjs"
        command = [node, str(static_validator), str(html_path)]
        if request.get("settings", {}).get("allowGoogleFonts"):
            command.append("--allow-google-fonts")
        static = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        if static.returncode:
            detail = (static.stdout or static.stderr).strip()
            raise ValueError(f"HTML静的検査を通過していません。\n{detail}")

    def preview_entrypoint(self, request_id: str) -> str:
        request, _ = self._load_request(request_id)
        entrypoint = request.get("result", {}).get("entrypoint")
        if not entrypoint:
            raise ValueError("プレビューはまだ準備できていません。")
        return str(entrypoint)

    def export_request(self, request_id: str) -> Path:
        request, _ = self._load_request(request_id)
        source = self.work_dir / request_id
        if not source.is_dir():
            raise ValueError(f"制作フォルダが見つかりません: {request_id}")
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        destination = self.exports_dir / f"{request_id}.zip"
        with tempfile.NamedTemporaryFile(
            "wb", dir=self.exports_dir, delete=False
        ) as handle:
            temp_path = Path(handle.name)
        try:
            with zipfile.ZipFile(
                temp_path, "w", compression=zipfile.ZIP_DEFLATED
            ) as archive:
                for candidate in sorted(source.rglob("*")):
                    if candidate.is_file():
                        archive.write(
                            candidate,
                            Path(request_id) / candidate.relative_to(source),
                        )
            os.replace(temp_path, destination)
        finally:
            if temp_path.exists():
                temp_path.unlink()
        request.setdefault("result", {})["exportPath"] = destination.relative_to(
            self.workspace
        ).as_posix()
        self._sync_request(request, request.get("statusMessage", ""))
        return destination

    def export_single_html(self, request_id: str) -> Path:
        request, _ = self._load_request(request_id)
        source = self.work_dir / request_id
        entrypoint_relative = str(
            request.get("result", {}).get("entrypoint", "wireframe/index.html")
        )
        entrypoint = (source / entrypoint_relative).resolve()
        try:
            entrypoint.relative_to(source.resolve())
        except ValueError as error:
            raise ValueError("HTML entrypoint is outside the request workspace.") from error
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        destination = self.exports_dir / f"{request_id}.html"
        create_single_file_html(entrypoint, destination, source)
        request.setdefault("result", {})["singleFileExportPath"] = (
            destination.relative_to(self.workspace).as_posix()
        )
        self._sync_request(request, request.get("statusMessage", ""))
        return destination

    def _copy_uploaded_evidence(self, output: Path, paths: list[str]) -> list[str]:
        copied: list[str] = []
        uploads_root = self.uploads_dir.resolve()
        for value in paths:
            source = (self.workspace / value).resolve()
            try:
                upload_relative = source.relative_to(uploads_root)
            except ValueError as error:
                raise ValueError("アップロード資料の保存先が不正です。") from error
            if not source.is_file():
                raise ValueError(f"アップロード資料が見つかりません: {value}")
            destination = output / upload_relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied.append(destination.relative_to(self.workspace).as_posix())
        return copied


def make_handler(app: ConsoleApp):
    class Handler(BaseHTTPRequestHandler):
        server_version = "AIProductDesignerConsole/0.3"

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/api/bootstrap":
                self.send_json(HTTPStatus.OK, app.bootstrap())
                return
            export_match = re.fullmatch(
                r"/api/requests/([a-zA-Z0-9-]{1,160})/export", parsed.path
            )
            if export_match:
                try:
                    archive = app.export_request(export_match.group(1))
                    self.send_file(
                        archive,
                        "application/zip",
                        download_name=archive.name,
                    )
                except ValueError as error:
                    self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                return
            preview_match = re.fullmatch(
                r"/preview/([a-zA-Z0-9-]{1,160})(?:/(.*))?", parsed.path
            )
            if preview_match:
                try:
                    request_id = preview_match.group(1)
                    relative = unquote(preview_match.group(2) or "")
                    if not relative:
                        entrypoint = app.preview_entrypoint(request_id)
                        self.send_response(HTTPStatus.FOUND)
                        self.send_header(
                            "Location",
                            f"/preview/{request_id}/{quote(entrypoint)}",
                        )
                        self.end_headers()
                        return
                    self.serve_work_file(request_id, relative)
                except ValueError as error:
                    self.send_json(HTTPStatus.NOT_FOUND, {"error": str(error)})
                return
            self.serve_static(parsed.path)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            try:
                if parsed.path == "/api/reference-files":
                    query = parse_qs(parsed.query)
                    result = app.store_reference_file(
                        query.get("batch", [""])[0],
                        query.get("path", [""])[0],
                        self.read_binary_body(MAX_REFERENCE_FILE_BYTES),
                    )
                    self.send_json(HTTPStatus.CREATED, result)
                    return
                payload = self.read_json_body()
                if parsed.path == "/api/design-systems":
                    result = app.register_design_system(payload)
                    self.send_json(HTTPStatus.CREATED, {"item": result})
                    return
                if parsed.path == "/api/requests":
                    result = app.create_request(payload)
                    self.send_json(HTTPStatus.CREATED, {"request": result})
                    return
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "APIが見つかりません。"})
            except (ValueError, FileExistsError, json.JSONDecodeError) as error:
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
            except OSError as error:
                self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})

        def read_json_body(self) -> dict:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 1_000_000:
                raise ValueError("リクエストが大きすぎます。")
            raw = self.rfile.read(content_length)
            value = json.loads(raw.decode("utf-8") or "{}")
            if not isinstance(value, dict):
                raise ValueError("JSON objectを送信してください。")
            return value

        def read_binary_body(self, maximum: int) -> bytes:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0:
                raise ValueError("空の資料はアップロードできません。")
            if content_length > maximum:
                raise ValueError("資料は1ファイル50MB以下にしてください。")
            return self.rfile.read(content_length)

        def serve_static(self, request_path: str) -> None:
            relative = "index.html" if request_path in {"", "/"} else unquote(request_path.lstrip("/"))
            candidate = (app.static_dir / relative).resolve()
            try:
                candidate.relative_to(app.static_dir)
            except ValueError:
                self.send_error(HTTPStatus.FORBIDDEN)
                return
            if not candidate.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            mime_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
            payload = candidate.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", f"{mime_type}; charset=utf-8" if mime_type.startswith("text/") else mime_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def serve_work_file(self, request_id: str, relative: str) -> None:
            root = (app.work_dir / request_id).resolve()
            candidate = (root / relative).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                self.send_error(HTTPStatus.FORBIDDEN)
                return
            if not candidate.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            mime_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
            self.send_file(candidate, mime_type)

        def send_file(
            self, path: Path, mime_type: str, download_name: str | None = None
        ) -> None:
            payload = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header(
                "Content-Type",
                f"{mime_type}; charset=utf-8"
                if mime_type.startswith("text/")
                else mime_type,
            )
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            if download_name:
                self.send_header(
                    "Content-Disposition", f'attachment; filename="{download_name}"'
                )
            self.end_headers()
            self.wfile.write(payload)

        def send_json(self, status: HTTPStatus, value: dict) -> None:
            payload = json.dumps(value, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format_string: str, *args) -> None:
            if self.path.startswith("/api/bootstrap"):
                return
            print(f"[design-console] {format_string % args}")

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4180)
    parser.add_argument("--list-design-systems", action="store_true")
    parser.add_argument("--register-source")
    parser.add_argument("--register-name")
    parser.add_argument("--register-description", default="")
    parser.add_argument("--register-status", choices=sorted(VALID_STATUS), default="active")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    from initialize_workspace import initialize_workspace

    initialize_workspace(args.workspace, skill_dir)
    app = ConsoleApp(args.workspace, skill_dir)
    for required in (app.registry_path, app.catalog_path):
        if not required.exists():
            raise SystemExit(f"Required file is missing: {required}")
    if args.list_design_systems:
        for item in app.bootstrap()["designSystems"]:
            print(f"{item['id']}\t{item['name']}\t{item['status']}\t{item['sourcePath']}")
        return 0
    if args.register_source:
        if not args.register_name:
            raise SystemExit("--register-name is required with --register-source")
        record = app.register_design_system(
            {
                "name": args.register_name,
                "sourcePath": args.register_source,
                "description": args.register_description,
                "status": args.register_status,
            }
        )
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0
    if not (app.static_dir / "index.html").exists():
        raise SystemExit(f"Required file is missing: {app.static_dir / 'index.html'}")
    server = ThreadingHTTPServer((args.host, args.port), make_handler(app))
    actual_port = server.server_address[1]
    print(f"AI Product Designer Console: http://{args.host}:{actual_port}/", flush=True)
    print(f"Workspace: {app.workspace}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
