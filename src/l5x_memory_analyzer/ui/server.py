"""Local Flask server for the treemap UI (Phase 2/2b).

Can start pre-loaded with an L5X path (CLI usage) or empty, with the
frontend's File->Open picker uploading a file to /api/load (desktop-shortcut
usage, James 2026-08-20 -- no command prompt needed for the launch version).
Serves the flat sizing report plus a lazy /api/node endpoint for infinite-
depth drill-down (see sizing/tree.py) -- vanilla JS/SVG frontend, no CDN
dependency, since engineering workstations on OT networks are frequently
airgapped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from flask import Flask, jsonify, request

from l5x_memory_analyzer.parser.aoi import parse_aoi_definitions
from l5x_memory_analyzer.parser.datatypes import DataTypeDef, parse_data_types
from l5x_memory_analyzer.parser.load import L5XDocument, L5XFormatError, load_l5x, load_l5x_bytes
from l5x_memory_analyzer.parser.tags import parse_tags
from l5x_memory_analyzer.sizing.constants import MemoryModel, load_memory_model
from l5x_memory_analyzer.sizing.controller_budgets import load_controller_budgets
from l5x_memory_analyzer.sizing.report import build_report
from l5x_memory_analyzer.sizing.tree import (
    NotDrillableError,
    expand_children,
    expand_definition_children,
    resolve_type_at_path,
)
from l5x_memory_analyzer.sizing.udt import RecursiveUdtError, UnknownDataTypeError
from l5x_memory_analyzer.ui.hierarchy import build_hierarchy, type_utilization

STATIC_DIR = Path(__file__).with_name("static")

_BUDGET_TABLE = load_controller_budgets()

_PATH_SEGMENT_RE = re.compile(r"\.[A-Za-z_][A-Za-z0-9_]*|\[\d+\]")


@dataclass
class DocState:
    doc: L5XDocument
    model: MemoryModel
    data_types: dict[str, DataTypeDef]
    tag_index: dict[str, tuple[str, tuple[int, ...]]]
    report_json: dict


def _load_state(root_source, display_name: str, from_bytes: bool) -> DocState:
    doc = load_l5x_bytes(root_source, display_name) if from_bytes else load_l5x(root_source)
    model = load_memory_model()
    data_types = {**parse_data_types(doc.root), **parse_aoi_definitions(doc.root)}
    tags = parse_tags(doc.root)
    tag_index = {t.path: (t.data_type, t.dimensions) for t in tags if not t.is_alias}

    entries, errors = build_report(doc.root, model)

    budget = _BUDGET_TABLE.lookup(doc.processor_type)

    report_json = {
        "loaded": True,
        "file_name": doc.path.name,
        "schema_revision": doc.schema_revision,
        "software_revision": doc.software_revision,
        "processor_type": doc.processor_type,
        "target_type": doc.target_type,
        "is_controller_export": doc.is_controller_export,
        "hierarchy": build_hierarchy(entries, data_types, model, {p: d for p, (dt, d) in tag_index.items()}),
        "type_summary": type_utilization(entries),
        "entries": [
            {
                "path": e.path,
                "category": e.category,
                "data_type": e.data_type,
                "bytes": e.bytes,
                "pct_of_total": e.pct_of_total,
                "tier": e.tier,
                "basis": e.basis,
            }
            for e in entries
        ],
        "errors": [{"path": err.path, "message": err.message} for err in errors],
        "total_bytes": sum(e.bytes for e in entries),
        "budget_bytes": budget.display_total_bytes if budget else None,
        "budget_architecture": budget.architecture if budget else None,
        "budget_confidence": budget.confidence if budget else None,
    }

    return DocState(doc=doc, model=model, data_types=data_types, tag_index=tag_index, report_json=report_json)


def create_app(l5x_path: str | Path | None = None) -> Flask:
    app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")
    app.config["state"] = _load_state(l5x_path, str(l5x_path), from_bytes=False) if l5x_path else None

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    @app.get("/api/report")
    def report():
        state: DocState | None = app.config["state"]
        if state is None:
            return jsonify({"loaded": False})
        return jsonify(state.report_json)

    @app.post("/api/load")
    def load():
        f = request.files.get("file")
        if f is None or not f.filename:
            return jsonify({"error": "no file provided"}), 400
        try:
            state = _load_state(f.read(), f.filename, from_bytes=True)
        except L5XFormatError as exc:
            return jsonify({"error": str(exc)}), 400
        app.config["state"] = state
        return jsonify(state.report_json)

    @app.get("/api/node")
    def node():
        state: DocState | None = app.config["state"]
        if state is None:
            return jsonify({"error": "no file loaded"}), 400

        tag_path = request.args.get("tag", "")
        subpath = request.args.get("path", "")

        # A "Type Definitions" pool node (path "udt_definitions/<Name>") is
        # not a tag instance -- drill into its own cost breakdown instead
        # (James, 2026-08-26: locals+params breakdown for a defs-pool node).
        # Always exactly one level deep, no further subpath to resolve.
        if tag_path.startswith("udt_definitions/"):
            def_name = tag_path[len("udt_definitions/"):]
            if def_name not in state.data_types:
                return jsonify({"error": f"unknown type definition {def_name!r}"}), 404
            if subpath:
                return jsonify({"error": "type definition breakdown has no further nested path"}), 400
            children = expand_definition_children(def_name, state.data_types, state.model)
            return jsonify({
                "children": [
                    {
                        "name": c.name,
                        "segment": c.segment,
                        "data_type": c.data_type,
                        "value": c.bytes,
                        "basis": c.basis,
                        "has_children": c.has_children,
                    }
                    for c in children
                ]
            })

        if tag_path not in state.tag_index:
            return jsonify({"error": f"unknown tag path {tag_path!r}"}), 404

        data_type, dimensions = state.tag_index[tag_path]
        segments = _PATH_SEGMENT_RE.findall(subpath)

        try:
            resolved_type, resolved_dims = resolve_type_at_path(
                data_type, dimensions, segments, state.data_types, state.model
            )
            children = expand_children(resolved_type, resolved_dims, state.data_types, state.model)
        except NotDrillableError as exc:
            return jsonify({"error": str(exc)}), 400
        except RecursiveUdtError as exc:
            return jsonify({"error": f"recursive type reference: {exc}"}), 400
        except UnknownDataTypeError as exc:
            return jsonify({"error": f"unknown data type: {exc}"}), 400

        return jsonify(
            {
                "children": [
                    {
                        "name": c.name,
                        "segment": c.segment,
                        "data_type": c.data_type,
                        "value": c.bytes,
                        "basis": c.basis,
                        "has_children": c.has_children,
                    }
                    for c in children
                ]
            }
        )

    return app


def run(l5x_path: str | Path | None, host: str = "127.0.0.1", port: int = 8765, open_browser: bool = False) -> None:
    try:
        app = create_app(l5x_path)
    except (L5XFormatError, OSError) as exc:
        raise SystemExit(f"error: {exc}") from exc

    if open_browser:
        import threading
        import webbrowser

        threading.Timer(0.75, lambda: webbrowser.open(f"http://{host}:{port}")).start()

    app.run(host=host, port=port, debug=False)
