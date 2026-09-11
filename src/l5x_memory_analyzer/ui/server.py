"""Local Flask server for the treemap UI (Phase 2/2b).

Can start pre-loaded with an L5X path (CLI usage) or empty, with the
frontend's File->Open picker uploading a file to /api/load (desktop-shortcut
usage, 2026-08-20: -- no command prompt needed for the launch version).
Serves the flat sizing report plus a lazy /api/node endpoint for infinite-
depth drill-down (see sizing/tree.py) -- vanilla JS/SVG frontend, no CDN
dependency, since engineering workstations on OT networks are frequently
airgapped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from flask import Flask, Response, jsonify, request

from l5x_memory_analyzer.parser.aoi import parse_aoi_definitions
from l5x_memory_analyzer.parser.datatypes import DataTypeDef, parse_data_types
from l5x_memory_analyzer.parser.load import L5XDocument, L5XFormatError, load_l5x, load_l5x_bytes
from l5x_memory_analyzer.parser.logic import count_instructions_in_text, parse_rll_routines
from l5x_memory_analyzer.parser.tags import parse_tags
from l5x_memory_analyzer.parser.tasks import parse_tasks, program_to_task_map
from l5x_memory_analyzer.sizing.constants import MemoryModel, load_memory_model
from l5x_memory_analyzer.sizing.controller_budgets import load_controller_budgets
from l5x_memory_analyzer.sizing.xref import find_usages
from l5x_memory_analyzer.sizing.export import write_csv, write_xlsx
from l5x_memory_analyzer.sizing.report import SizeEntry, SizeError, build_report
from l5x_memory_analyzer.sizing.tree import (
    NotDrillableError,
    expand_children,
    expand_definition_children,
    subtree_confidence,
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
    entries: list[SizeEntry]
    errors: list[SizeError]
    # Memo for _child_confidence, keyed (data_type, dimensions). Per
    # document, so it is discarded with the document rather than leaking
    # one file's types into the next.
    confidence_cache: dict = field(default_factory=dict)


def _load_state(root_source, display_name: str, from_bytes: bool) -> DocState:
    doc = load_l5x_bytes(root_source, display_name) if from_bytes else load_l5x(root_source)
    model = load_memory_model()
    data_types = {**parse_data_types(doc.root), **parse_aoi_definitions(doc.root)}
    tags = parse_tags(doc.root)
    tag_index = {t.path: (t.data_type, t.dimensions) for t in tags if not t.is_alias}

    entries, errors = build_report(doc.root, model)

    budget = _BUDGET_TABLE.lookup(doc.processor_type)

    # JSR call-tree info (2026-08-27, Phase 5). Byte totals already avoid
    # double-counting a JSR target's cost (RoutineLogic.is_jsr_target --
    # confirmed 2026-08-22) by simply never emitting that target routine
    # as its own SizeEntry -- correct for bytes, but it means a called
    # subroutine is otherwise INVISIBLE in the treemap, with no way to see
    # its cost is folded into the caller. This surfaces the real caller ->
    # target relationship (keyed by the SAME routine.path used as every
    # routine_logic SizeEntry's path, so the frontend can join them) purely
    # for display -- no sizing change, see parser/logic.py's
    # jsr_target_names field docstring.
    jsr_calls = {
        r.path: sorted(r.jsr_target_names)
        for r in parse_rll_routines(doc.root)
        if r.jsr_target_names
    }

    # Rung counts per routine (2026-08-27, "routines need to have
    # indication how many rungs"). Same side-channel-dict shape as jsr_calls
    # above, keyed by the identical routine.path every routine_logic leaf
    # node's own path already carries, purely for display -- no sizing
    # change.
    rung_counts = {r.path: r.rung_count for r in parse_rll_routines(doc.root)}

    report_json = {
        "loaded": True,
        "file_name": doc.path.name,
        "schema_revision": doc.schema_revision,
        "software_revision": doc.software_revision,
        "processor_type": doc.processor_type,
        "target_type": doc.target_type,
        "is_controller_export": doc.is_controller_export,
        "is_safety_project": doc.is_safety_project,
        "safety_level": doc.safety_level,
        # Declared UDT/AOI names, so the UI can tell a type it can
        # cross-reference from an atomic it cannot.
        "type_names": sorted(data_types),
        "aoi_names": sorted(n for n, d in data_types.items() if d.is_aoi),
        "hierarchy": build_hierarchy(
            entries, data_types, model, {p: d for p, (dt, d) in tag_index.items()},
            program_to_task_map(doc.root),
            aoi_names=set(parse_aoi_definitions(doc.root)),
        ),
        "type_summary": type_utilization(entries),
        "jsr_calls": jsr_calls,
        "rung_counts": rung_counts,
        # Schedule type per task, for the treeview's task description line.
        # Read straight off the L5X, never inferred.
        "task_info": {
            t.name: {
                "type": t.task_type,
                "rate": t.rate,
                "priority": t.priority,
                "is_safety": t.is_safety,
            }
            for t in parse_tasks(doc.root)
        },
        # Program-scoped tag count per program, so a program tile can say how
        # many tags it holds alongside its routine count.
        "program_tag_counts": _program_tag_counts(entries),
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

    return DocState(doc=doc, model=model, data_types=data_types, tag_index=tag_index,
                     report_json=report_json, entries=entries, errors=errors)


def _program_tag_counts(entries) -> dict[str, int]:
    """Program name -> number of program-scoped tags in it."""
    counts: dict[str, int] = {}
    for e in entries:
        if e.category != "program_tag":
            continue
        # Real path shape is "program:<Program>/<Tag>" -- confirmed against a
        # real export rather than assumed.
        if not e.path.startswith("program:") or "/" not in e.path:
            continue
        program = e.path[len("program:"):].split("/", 1)[0]
        counts[program] = counts.get(program, 0) + 1
    return counts



def _child_confidence(child, state):
    """Subtree confidence mix for one drill child, memoised per type+dims.

    Only drillable children need it -- a leaf's own basis and bytes
    already say everything there is to say. Memoised because a wide UDT
    repeats the same member types, and an array repeats one element type
    many times over.
    """
    if not child.has_children:
        return None
    key = (child.data_type, child.dimensions)
    cache = state.confidence_cache
    if key not in cache:
        try:
            acc = subtree_confidence(
                child.data_type, child.dimensions, state.data_types, state.model
            )
        except Exception:
            # A type the sizer cannot expand is not a UI failure; fall
            # back to the child's own rolled-up basis.
            acc = None
        cache[key] = acc
    acc = cache[key]
    if acc is None:
        return None
    return {**acc, "total": sum(acc.values())}

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
        except Exception as exc:  # noqa: BLE001 -- see below
            # Any other failure is a BUG in the sizing engine, not bad input,
            # and it must still come back as JSON. Flask's default is an HTML
            # traceback page, which the browser cannot parse as JSON, so the
            # fetch handler threw before it could report anything and the UI
            # sat on "Loading <file>..." forever with no error shown (real
            # report 2026-09-09, a KeyError out of the ST operator table).
            # The traceback still goes to the server log for diagnosis; the
            # user gets a message naming the failure instead of a hang.
            app.logger.exception("Failed to size %s", f.filename)
            return jsonify({
                "error": (
                    f"Could not size {f.filename}: {type(exc).__name__}: {exc}. "
                    f"This is a bug in the analyzer, not a problem with the file. "
                    f"The full traceback is in the server console."
                ),
            }), 500
        app.config["state"] = state
        return jsonify(state.report_json)

    @app.get("/api/export.csv")
    def export_csv():
        state: DocState | None = app.config["state"]
        if state is None:
            return jsonify({"error": "no file loaded"}), 400
        csv_text = write_csv(state.entries, state.errors)
        download_name = Path(state.doc.path.name).stem + "_report.csv"
        return Response(
            csv_text, mimetype="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
        )

    @app.get("/api/export.xlsx")
    def export_xlsx():
        state: DocState | None = app.config["state"]
        if state is None:
            return jsonify({"error": "no file loaded"}), 400
        try:
            data = write_xlsx(state.entries, state.errors)
        except ImportError as exc:
            return jsonify({"error": str(exc)}), 501
        download_name = Path(state.doc.path.name).stem + "_report.xlsx"
        return Response(
            data, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
        )

    @app.get("/api/rungs")
    def rungs():
        """Every rung of one routine, so the treemap can drill below routine
        level. Deliberately its own endpoint rather than part of the report
        payload: a large program has tens of thousands of rungs and shipping
        all of their text on every load would dwarf the rest of the JSON."""
        state: DocState | None = app.config["state"]
        if state is None:
            return jsonify({"error": "no file loaded"}), 400
        # Routine leaf paths are "program:<Program>/<Routine>" (real shape,
        # read off a real export). Rung TEXT is not retained by
        # parse_rll_routines -- it keeps counts only -- so this goes back to
        # the XML for the one routine being opened rather than making every
        # parse carry every rung's source.
        path = request.args.get("path", "")
        if not path.startswith("program:") or "/" not in path:
            return jsonify({"error": f"not a routine path: {path!r}"}), 400
        program_name, routine_name = path[len("program:"):].split("/", 1)

        weights = state.model.logic_instructions.weights
        for owner in list(state.doc.root.iter("Program")) + list(
            state.doc.root.iter("AddOnInstructionDefinition")
        ):
            if (owner.get("Name") or "") != program_name:
                continue
            for routine_el in owner.iter("Routine"):
                if (routine_el.get("Name") or "") != routine_name:
                    continue
                out = []
                for rung_el in routine_el.iter("Rung"):
                    text_el = rung_el.find("Text")
                    text = (text_el.text or "").strip() if text_el is not None else ""
                    # Takes a LIST of rung texts, not one string -- passing a
                    # bare string iterates it character by character and
                    # silently returns nothing.
                    counts = count_instructions_in_text([text])
                    out.append({
                        "number": int(rung_el.get("Number") or len(out)),
                        "text": text,
                        # Priced from the SAME weight table the routine total
                        # uses, so the rungs sum to their routine rather than
                        # being a second, differently-derived number.
                        "value": sum(weights.get(m, 0) * n for m, n in counts.items()),
                        "instructions": sorted(counts),
                    })
                return jsonify({"path": path, "rungs": out})
        return jsonify({"error": f"unknown routine path {path!r}"}), 404

    @app.get("/api/node")
    def node():
        state: DocState | None = app.config["state"]
        if state is None:
            return jsonify({"error": "no file loaded"}), 400

        tag_path = request.args.get("tag", "")
        subpath = request.args.get("path", "")

        # A "Type Definitions" pool node (path "udt_definitions/<Name>") is
        # not a tag instance -- drill into its own cost breakdown instead
        # (2026-08-26, locals+params breakdown for a defs-pool node).
        # Always exactly one level deep, no further subpath to resolve.
        # The definition drill has two readings and they answer different
        # questions. `mode=definition` (the default) shows what the type
        # costs to EXIST -- a flat per-declared-member table rate, which
        # is why a BOOL, a DINT and a TIMER all show the same number and
        # why that looks wrong until you know what it is. `mode=instance`
        # shows what one instance of the type OCCUPIES, where those same
        # three members are 4, 4 and 12. Neither is more correct; showing
        # only the first made the definition view read as a broken size.
        if tag_path.startswith("udt_definitions/") and request.args.get("mode") == "instance":
            def_name = tag_path[len("udt_definitions/"):]
            if def_name not in state.data_types:
                return jsonify({"error": f"unknown type definition {def_name!r}"}), 404
            children = expand_children(def_name, (), state.data_types, state.model)
            return jsonify({"mode": "instance", "children": [
                {
                    "name": c.name, "segment": c.segment, "data_type": c.data_type,
                    "dimensions": list(c.dimensions), "value": c.bytes,
                    "basis": c.basis, "has_children": c.has_children,
                    "alias_of": c.alias_of, "alias_bit": c.alias_bit,
                    "confidence": _child_confidence(c, state),
                }
                for c in children
            ]})

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
                        # Dimensions travel with every drilled child so an
                        # array member renders as "Queue[24]" the way a
                        # top-level array tag already does. Child has
                        # always carried this; the payload simply dropped
                        # it, so a UDT/AOI array member was indistinguish-
                        # able from a scalar once you drilled into it.
                        "dimensions": list(c.dimensions),
                        "value": c.bytes,
                        "basis": c.basis,
                        "has_children": c.has_children,
                        "alias_of": c.alias_of,
                        "alias_bit": c.alias_bit,
                        # Whole-subtree confidence mix, so the client's
                        # rollup does not change depending on which
                        # children it happens to have fetched.
                        "confidence": _child_confidence(c, state),
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
                        # Dimensions travel with every drilled child so an
                        # array member renders as "Queue[24]" the way a
                        # top-level array tag already does. Child has
                        # always carried this; the payload simply dropped
                        # it, so a UDT/AOI array member was indistinguish-
                        # able from a scalar once you drilled into it.
                        "dimensions": list(c.dimensions),
                        "value": c.bytes,
                        "basis": c.basis,
                        "has_children": c.has_children,
                        "alias_of": c.alias_of,
                        "alias_bit": c.alias_bit,
                        # Whole-subtree confidence mix, so the client's
                        # rollup does not change depending on which
                        # children it happens to have fetched.
                        "confidence": _child_confidence(c, state),
                    }
                    for c in children
                ]
            }
        )


    @app.get("/api/xref")
    def api_xref():
        """Every navigable path that reaches a given UDT/AOI type.

        Deliberately its own endpoint rather than part of /api/report: on
        a wide controller this walks every tag through the member graph,
        and most sessions never open the tab. The client asks only when
        the tab is opened and shows progress while it waits.
        """
        state: DocState | None = app.config["state"]
        if state is None:
            return jsonify({"error": "no file loaded"}), 400
        target = request.args.get("type", "")
        if target not in state.data_types:
            return jsonify({"error": f"unknown type {target!r}"}), 404
        usages = find_usages(target, state.data_types, state.tag_index)
        return jsonify({
            "type": target,
            "count": len(usages),
            "usages": [
                {
                    "path": u.path, "tag_path": u.tag_path,
                    "member_path": u.member_path, "scope": u.scope,
                    "via": u.via, "direct": u.direct,
                }
                for u in usages
            ],
        })

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

    # threaded=True: the "2 levels deep" treemap toggle (2026-08-27)
    # fires one /api/node fetch per visible drillable tile CONCURRENTLY
    # from the browser -- against Flask's default single-threaded dev
    # server those just queue up serially, which is fine for a handful of
    # tiles but turns "Controller Tags" on a real program (hundreds of
    # tags) into a multi-second stall for no reason, since each request is
    # independent read-only work against the same already-parsed in-memory
    # DocState.
    app.run(host=host, port=port, debug=False, threaded=True)
