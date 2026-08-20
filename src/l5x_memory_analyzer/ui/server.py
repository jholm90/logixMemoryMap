"""Local Flask server for the treemap UI (Phase 2, OQ-STACK resolution).

Loads one L5X file at startup, serves its sizing report as JSON, and serves
the static frontend (vanilla JS/SVG treemap -- no CDN dependency, since
engineering workstations on OT networks are frequently airgapped).
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify

from l5x_memory_analyzer.parser.load import L5XFormatError, load_l5x
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report
from l5x_memory_analyzer.ui.hierarchy import build_hierarchy, type_utilization

STATIC_DIR = Path(__file__).with_name("static")

CONTROLLER_MEMORY_BUDGET_BYTES = 4 * 1024 * 1024  # 4MB -- see OQ re: selectable budgets, Phase 6


def create_app(l5x_path: str | Path) -> Flask:
    app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")

    doc = load_l5x(l5x_path)
    model = load_memory_model()
    entries, errors = build_report(doc.root, model)

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    @app.get("/api/report")
    def report():
        return jsonify(
            {
                "file_name": doc.path.name,
                "schema_revision": doc.schema_revision,
                "software_revision": doc.software_revision,
                "hierarchy": build_hierarchy(entries),
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
                "budget_bytes": CONTROLLER_MEMORY_BUDGET_BYTES,
            }
        )

    return app


def run(l5x_path: str | Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    try:
        app = create_app(l5x_path)
    except (L5XFormatError, OSError) as exc:
        raise SystemExit(f"error: {exc}") from exc
    app.run(host=host, port=port, debug=False)
