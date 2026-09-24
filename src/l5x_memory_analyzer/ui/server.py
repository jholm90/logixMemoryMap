"""Local Flask server for the treemap UI.

Starts either pre-loaded with an L5X path, for CLI use, or empty, with the
frontend's File -> Open picker uploading to /api/load, so a desktop shortcut needs
no command prompt.

Serves the flat sizing report plus a lazy /api/node endpoint for infinite-depth
drill-down -- see `sizing/tree.py`. The frontend is vanilla JS and SVG with no CDN
dependency, because engineering workstations on OT networks are frequently
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
from l5x_memory_analyzer.parser.logic import (
    count_instructions_in_text,
    jsr_calls_in_text,
    parse_rll_routines,
)
from l5x_memory_analyzer.parser.modules import label_modules, parse_modules
from l5x_memory_analyzer.parser.tags import parse_tags
from l5x_memory_analyzer.parser.tasks import parse_tasks, program_to_task_map
from l5x_memory_analyzer.sizing.constants import MemoryModel, load_memory_model
from l5x_memory_analyzer.sizing.alarms import alarm_conditions_for_host, alarm_lookup_tables
from l5x_memory_analyzer.sizing.confidence import (
    refine_opcodes,
    rung_band,
    BANDS, KNOWN_EXACT_CALLS, PROVENANCE_BAND, SCAFFOLD_BAND,
)
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
from l5x_memory_analyzer.usage import UsageIndex, segments_of

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
    # Memo for expand_children, same key and same reasoning. Warmed at load
    # for every drillable type already on the hierarchy, so a drill is a
    # dictionary lookup rather than a recompute -- and, more to the point,
    # cannot return a different answer than the one already on screen.
    children_cache: dict = field(default_factory=dict)
    # The remaining per-document answers, all computed at load. Each was an
    # endpoint that recomputed from the XML on every call.
    rungs_cache: dict = field(default_factory=dict)
    alarms_cache: dict = field(default_factory=dict)
    xref_cache: dict = field(default_factory=dict)
    # Where each tag, member, routine, module and type member is used
    # (l5x_memory_analyzer/usage.py). Built once at load.
    usage: UsageIndex | None = None


def _usage_for_path(path: str, usage: UsageIndex) -> dict | None:
    """The usage record for one hierarchy node, by the node's path. None where
    "used" has no meaning (a group, an overhead line, a rung)."""
    if not path or path.startswith(("alarms/", "aoi_definitions/")) or path == "project_baseline":
        return None
    if path.startswith("modules/"):
        name = path[len("modules/"):].split("/")[0]
        return {**usage.module(name).as_json(), "kind": "references"}
    if path.startswith("udt_definitions/"):
        rest = path[len("udt_definitions/"):]
        name, dot, member = rest.partition(".")
        if "/" in name:
            return None
        if dot:
            if not usage.has_member(name, member):
                return None  # an overhead line of the definition, not a member
            return _member_json(usage, name, member)
        return {"count": usage.type_instances(name), "via_parent": False, "implicit": 0,
                "kind": "instances"}
    scope, slash, rest = path.partition("/")
    if not slash:
        return None
    if scope.startswith("program:") and "/" not in rest and rest and usage.is_routine(path):
        return {**usage.routine(path).as_json(), "kind": "calls"}
    if scope == "controller" or scope.startswith("program:"):
        return _tag_json(usage, path, [])
    return None


def _tag_json(usage: UsageIndex, tag_path: str, segments: list[str]) -> dict | None:
    u = usage.tag(tag_path, segments)
    return None if u is None else {**u.as_json(), "kind": "references"}


def _member_json(usage: UsageIndex, type_name: str, member: str) -> dict | None:
    # Only a declared member has a use count; a definition's overhead rows
    # (base, name pool, BOOL packing) are costs, not things logic can name.
    if not usage.has_member(type_name, member):
        return None
    u = usage.type_member(type_name, member)
    if u is None:
        return None
    return {**u.as_json(), "kind": "member", "copied_whole": usage.copied_whole(type_name)}


def _attach_usage(node: dict, usage: UsageIndex) -> None:
    rec = _usage_for_path(node.get("path") or "", usage) if not node.get("children") or \
        (node.get("path") or "").startswith(("udt_definitions/", "modules/", "controller/", "program:")) else None
    if rec is not None:
        node["uses"] = rec
    for child in node.get("children") or []:
        _attach_usage(child, usage)


def _load_state(root_source, display_name: str, from_bytes: bool) -> DocState:
    doc = load_l5x_bytes(root_source, display_name) if from_bytes else load_l5x(root_source)
    model = load_memory_model()
    data_types = {**parse_data_types(doc.root), **parse_aoi_definitions(doc.root)}
    tags = parse_tags(doc.root)
    tag_index = {t.path: (t.data_type, t.dimensions) for t in tags if not t.is_alias}

    entries, errors = build_report(doc.root, model)

    budget = _BUDGET_TABLE.lookup(doc.processor_type)

    # JSR call-tree info (Phase 5). Byte totals already avoid
    # double-counting a JSR target's cost (RoutineLogic.is_jsr_target --
    # confirmed) by simply never emitting that target routine
    # as its own SizeEntry -- correct for bytes, but it means a called
    # subroutine is otherwise INVISIBLE in the treemap, with no way to see
    # its cost is folded into the caller. This surfaces the real caller ->
    # target relationship (keyed by the SAME routine.path used as every
    # routine_logic SizeEntry's path, so the frontend can join them) purely
    # for display -- no sizing change, see parser/logic.py's
    # jsr_target_names field docstring.
    # Parsed once and reused by all three side-channels below. It used to be
    # called three times over the same document, which on a real export is a
    # third of a second each for the identical answer.
    routines = parse_rll_routines(doc.root)

    jsr_calls = {
        r.path: sorted(r.jsr_target_names)
        for r in routines
        if r.jsr_target_names
    }

    # Rung counts per routine ("routines need to have
    # indication how many rungs"). Same side-channel-dict shape as jsr_calls
    # above, keyed by the identical routine.path every routine_logic leaf
    # node's own path already carries, purely for display -- no sizing
    # change.
    rung_counts = {r.path: r.rung_count for r in routines}

    # Which mnemonics each routine contains, same side-channel shape again.
    # A routine's confidence is the band its worst instruction earns, and the
    # client could only work that out from rungs it had already opened -- so a
    # routine read "Unverified 50%" until you drilled into it and jumped to
    # "Measured" on the way back. That is a property of the browsing history,
    # not of the routine. Shipping the inventory up front makes the answer the
    # same before and after, exactly as subtree_confidence does for tag data.
    routine_instructions = {
        r.path: refine_opcodes(sorted(r.instruction_counts), r.jsr_calls)
        for r in routines
        if r.instruction_counts
    }

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
            # Real chassis/network topology, off each Module's own
            # ParentModule attribute -- purely a display nesting, no
            # sizing consequence.
            module_parents=_module_parent_labels(doc.root),
        ),
        "type_summary": type_utilization(entries),
        "jsr_calls": jsr_calls,
        "routine_instructions": routine_instructions,
        "routine_confidence": {},  # filled in below, once the rungs are priced
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
        # Accuracy, not provenance. The UI used to print a provenance tier as
        # if it were a confidence, so compiled logic -- which can never be
        # KNOWN, by CLAUDE.md's ground-truth constraint -- read as 0%. These
        # two carry the measured alternative: what the engine's error actually
        # was on files where each instruction was the only variable.
        "confidence_bands": [
            {"key": b.key, "label": b.label, "pct": b.pct,
             "bound": b.bound, "blurb": b.blurb}
            for b in BANDS
        ],
        "instruction_accuracy": getattr(model, "instruction_accuracy", None) or {},
        "provenance_band": dict(PROVENANCE_BAND),
        "scaffold_band": dict(SCAFFOLD_BAND),
        "known_exact_calls": dict(KNOWN_EXACT_CALLS),
    }

    # EVERYTHING BROWSABLE IS COMPUTED NOW, not on the first click.
    #
    # Deferring it bought a faster first paint and paid for it twice: a drill
    # could return a number the level above had not been able to work out, and
    # the same node then read differently depending on whether it had been
    # visited. Doing it here makes every answer a property of the document.
    #
    # It is affordable because both passes memoise on (data_type, dimensions),
    # so the work is per distinct TYPE, not per tag. On a 33 MB real export
    # with 5,590 entries that is 285 keys: about a tenth of a second against a
    # three-second load.
    conf_cache: dict = {}
    _attach_subtree_confidence(report_json["hierarchy"], data_types, model, conf_cache)
    usage = UsageIndex(doc.root)
    _attach_usage(report_json["hierarchy"], usage)

    children_cache: dict = {}
    for key in list(conf_cache):
        try:
            children_cache[key] = expand_children(key[0], key[1], data_types, model)
        except Exception:
            # A true leaf, or a type the sizer cannot expand. /api/node has to
            # answer for those anyway, so leave it to say so.
            pass

    # Rungs, alarm conditions and cross-references, all of which were endpoints
    # that went back to the XML on every call. Measured on a 33 MB real export:
    # rungs 0.06s for 6,550 of them, alarms 0.04s, xref 0.64s for 193 types.
    rungs_cache = _build_all_rungs(doc.root, model)

    # A routine's confidence, byte-weighted over its OWN rungs -- the identical
    # calculation the client does once a routine has been expanded.
    #
    # It used to answer two different questions depending on whether it had
    # been opened: the worst instruction anywhere in the routine (a floor)
    # before, and a byte-weighted mean over rungs after. A routine of 900 clean
    # rungs and one unmeasured instruction read 50% closed and 88% open. Both
    # rules are defensible; having both is not.
    accuracy = getattr(model, "instruction_accuracy", None) or {}
    routine_confidence = {}
    # The same rungs split by band, as fractions of the routine's rung value.
    # routine_confidence is the percent this mix averages to; the mix is what
    # lets the file-level figure say how many bytes sit in each band rather
    # than only what they average to. Derived from one pass so the two cannot
    # disagree.
    routine_band_mix = {}
    for path, rows in rungs_cache.items():
        total = sum(r["value"] for r in rows)
        if not total:
            continue
        mix: dict[str, float] = {}
        weighted = 0.0
        for r in rows:
            band = rung_band(r["band_keys"], accuracy)
            mix[band.key] = mix.get(band.key, 0.0) + r["value"]
            weighted += r["value"] * band.pct
        routine_confidence[path] = round(weighted / total, 2)
        routine_band_mix[path] = {k: v / total for k, v in mix.items()}

    alarms_cache: dict = {}
    try:
        tag_types, udt_members = alarm_lookup_tables(doc.root)
        for e in entries:
            if not e.path.startswith("alarms/"):
                continue
            host = e.path[len("alarms/"):]
            rows = alarm_conditions_for_host(doc.root, model, host, tag_types, udt_members)
            if rows:
                alarms_cache[host] = rows
    except Exception:
        alarms_cache = {}

    report_json["routine_confidence"] = routine_confidence
    report_json["routine_band_mix"] = routine_band_mix

    xref_cache: dict = {}
    for type_name in data_types:
        try:
            xref_cache[type_name] = find_usages(type_name, data_types, tag_index)
        except Exception:
            pass

    return DocState(doc=doc, model=model, data_types=data_types, tag_index=tag_index,
                     report_json=report_json, entries=entries, errors=errors,
                     confidence_cache=conf_cache, children_cache=children_cache,
                     rungs_cache=rungs_cache, alarms_cache=alarms_cache,
                     xref_cache=xref_cache, usage=usage)


def _module_parent_labels(root) -> dict[str, str]:
    """Module label -> its parent's label, for the tree's rack nesting.

    Both sides have to be LABELS, not names: a real POINT I/O card has no
    name at all (see parser/modules.py label_modules), so keying this by
    name silently dropped every one of them out of the nesting and left a
    rack of sixteen cards sitting flat beside its adapter.
    """
    modules = parse_modules(root)
    labels = label_modules(modules)
    by_name = {m.name: labels[i] for i, m in enumerate(modules) if m.name}
    return {
        labels[i]: by_name.get(m.parent_module, m.parent_module)
        for i, m in enumerate(modules)
    }


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



def _attach_subtree_confidence(node, data_types, model, cache) -> None:
    """Give every drillable node in the initial hierarchy the same whole-subtree
    confidence summary that a lazily-fetched drill child already gets.

    Without it the report's own nodes were the one place the UI had to fall back
    to a node's rolled-up `basis`, which is weakest()-of-subtree. A UDT-typed
    controller tag whose members are every one of them exact read "Unverified
    50%" at the tag level and "Exact 100%" one click in -- the same number
    changing because of where the user had been, which is exactly what computing
    this server-side was meant to stop. It was only ever wired into /api/node.

    Memoised on (data_type, dimensions), so the cost is per distinct TYPE and
    not per tag: a file with thousands of tags over a few hundred types pays for
    the types.
    """
    for child in node.get("children") or ():
        _attach_subtree_confidence(child, data_types, model, cache)
    if not node.get("has_children") or not node.get("data_type"):
        return
    # A type DEFINITION node carries its type's name as data_type too, but the
    # tier mix below describes one INSTANCE of that type. Attached to the
    # definition, it weighed a 4 KB definition as a 30 KB instance and skewed
    # every figure above it, the file-level confidence included.
    if (node.get("path") or "").startswith(("udt_definitions/", "aoi_definitions/")):
        return
    key = (node["data_type"], tuple(node.get("dimensions") or ()))
    if key not in cache:
        try:
            cache[key] = subtree_confidence(key[0], key[1], data_types, model)
        except Exception:
            # A type the sizer cannot expand is not a UI failure.
            cache[key] = None
    acc = cache[key]
    if acc:
        node["confidence"] = {**acc, "total": sum(acc.values())}


def _build_all_rungs(root, model) -> dict:
    """Every routine's rungs, priced, keyed by the routine path the hierarchy
    uses. Built once at load rather than re-walking the XML per routine."""
    weights = model.logic_instructions.weights
    out: dict[str, list[dict]] = {}
    for owner in list(root.iter("Program")) + list(root.iter("AddOnInstructionDefinition")):
        owner_name = owner.get("Name") or ""
        is_aoi = owner.tag == "AddOnInstructionDefinition"
        # An AOI's RLL routines are priced as ONE entry at
        # aoi_definitions/<AOI>/<names joined by +> (report.py), so their rungs
        # are collected under that same key -- otherwise the routine has no
        # rung-based confidence and falls back to its provenance tier.
        aoi_key = None
        if is_aoi:
            names = [r.get("Name") for r in owner.iter("Routine")
                     if (r.get("Type") or "RLL") == "RLL" and r.get("Name")] or ["Logic"]
            aoi_key = f"aoi_definitions/{owner_name}/{'+'.join(names)}"
        for routine_el in owner.iter("Routine"):
            if is_aoi and (routine_el.get("Type") or "RLL") != "RLL":
                continue
            rows = []
            for rung_el in routine_el.iter("Rung"):
                text_el = rung_el.find("Text")
                text = (text_el.text or "").strip() if text_el is not None else ""
                # Takes a LIST of rung texts, not one string -- passing a bare
                # string iterates it character by character and silently
                # returns nothing.
                counts = count_instructions_in_text([text])
                rows.append({
                    "number": int(rung_el.get("Number") or len(rows)),
                    "text": text,
                    # Priced from the SAME weight table the routine total uses,
                    # so the rungs sum to their routine rather than being a
                    # second, differently-derived number.
                    "value": sum(weights.get(m, 0) * n for m, n in counts.items()),
                    "instructions": sorted(counts),
                    # Shape-refined keys for banding only -- a parameterless
                    # JSR is a measured constant, a parameterised one is the
                    # fitted A(n)/B(n) model, and one band cannot serve both.
                    # Never used for pricing; the weight table sees the bare
                    # mnemonic either way.
                    "band_keys": refine_opcodes(
                        sorted(counts), jsr_calls_in_text([text])
                    ),
                })
            if aoi_key:
                out.setdefault(aoi_key, []).extend(rows)
            else:
                out[f"program:{owner_name}/{routine_el.get('Name') or ''}"] = rows
    return out


def _expand_cached(data_type, dimensions, state):
    """expand_children through the per-document memo warmed at load.

    A miss still computes -- a type reached by a path the hierarchy did not
    contain is legitimate -- and is then remembered, so the second visit to
    anything is free and identical to the first.
    """
    key = (data_type, tuple(dimensions or ()))
    hit = state.children_cache.get(key)
    if hit is not None:
        return hit
    children = expand_children(data_type, dimensions, state.data_types, state.model)
    state.children_cache[key] = children
    return children


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
            # report a KeyError out of the ST operator table).
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
        """Every rung of one routine, from the table built at load.

        This used to walk the whole document per call -- once per routine
        opened, on a file with hundreds of them.
        """
        state: DocState | None = app.config["state"]
        if state is None:
            return jsonify({"error": "no file loaded"}), 400
        path = request.args.get("path", "")
        if not path.startswith("program:") or "/" not in path:
            return jsonify({"error": f"not a routine path: {path!r}"}), 400
        rows = state.rungs_cache.get(path)
        if rows is None:
            return jsonify({"error": f"unknown routine path {path!r}"}), 404
        return jsonify({"path": path, "rungs": rows})

    @app.get("/api/alarms")
    def alarms():
        """The alarm conditions on one host tag, from the table built at load.

        It used to rebuild the whole document's alarm lookup tables on every
        call before answering for one host.
        """
        state: DocState | None = app.config["state"]
        if state is None:
            return jsonify({"error": "no file loaded"}), 400
        path = request.args.get("path", "")
        if not path.startswith("alarms/"):
            return jsonify({"error": f"not an alarm path: {path!r}"}), 400
        host = path[len("alarms/"):]
        rows = state.alarms_cache.get(host)
        if not rows:
            return jsonify({"error": f"no alarm conditions on {host!r}"}), 404
        return jsonify({"path": path, "conditions": rows})

    @app.get("/api/node")
    def node():
        state: DocState | None = app.config["state"]
        if state is None:
            return jsonify({"error": "no file loaded"}), 400

        tag_path = request.args.get("tag", "")
        subpath = request.args.get("path", "")

        # A "Type Definitions" pool node (path "udt_definitions/<Name>") is
        # not a tag instance -- drill into its own cost breakdown instead
        # (locals+params breakdown for a defs-pool node).
        # Always exactly one level deep, no further subpath to resolve.
        # The definition drill has two readings and they answer different
        # questions. `mode=definition` (the default) shows what the type
        # costs to EXIST -- a flat per-declared-member table rate, which
        # is why a BOOL, a DINT and a TIMER all show the same number and
        # why that reads as wrong until the mode is understood. `mode=instance`
        # shows what one instance of the type OCCUPIES, where those same
        # three members are 4, 4 and 12. Neither is more correct; showing
        # only the first made the definition view read as a broken size.
        if tag_path.startswith("udt_definitions/") and request.args.get("mode") == "instance":
            def_name = tag_path[len("udt_definitions/"):]
            if def_name not in state.data_types:
                return jsonify({"error": f"unknown type definition {def_name!r}"}), 404
            # Instance mode descends like any ordinary tag of this type --
            # the definition itself is just the starting point. Without
            # resolving the subpath, drilling one level below a definition
            # in instance mode failed outright ("no further nested path"),
            # so a UDT was browsable exactly one member deep.
            try:
                resolved_type, resolved_dims = resolve_type_at_path(
                    def_name, (), _PATH_SEGMENT_RE.findall(subpath),
                    state.data_types, state.model,
                )
                children = _expand_cached(resolved_type, resolved_dims, state)
            except NotDrillableError as exc:
                return jsonify({"error": str(exc)}), 400
            except RecursiveUdtError as exc:
                return jsonify({"error": f"recursive type reference: {exc}"}), 400
            except UnknownDataTypeError as exc:
                return jsonify({"error": f"unknown data type: {exc}"}), 400
            return jsonify({"mode": "instance", "children": [
                {
                    "uses": (_member_json(state.usage, resolved_type, c.segment[1:])
                             if state.usage and c.segment.startswith(".") else None),
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
                        "uses": (_member_json(state.usage, def_name, c.segment[1:])
                                 if state.usage and c.segment.startswith(".") else None),
                        "name": c.name,
                        "segment": c.segment,
                        "data_type": c.data_type,
                        # Dimensions travel with every drilled child so an
                        # array member renders as "Queue[24]" the way a
                        # top-level array tag already does. Child has
                        # always carried this; the payload simply dropped
                        # it, so a UDT/AOI array member was indistinguish-
                        # able from a scalar once drilled into.
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
            children = _expand_cached(resolved_type, resolved_dims, state)
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
                        "uses": (_tag_json(state.usage, tag_path, segments_of(subpath + c.segment))
                                 if state.usage else None),
                        "name": c.name,
                        "segment": c.segment,
                        "data_type": c.data_type,
                        # Dimensions travel with every drilled child so an
                        # array member renders as "Queue[24]" the way a
                        # top-level array tag already does. Child has
                        # always carried this; the payload simply dropped
                        # it, so a UDT/AOI array member was indistinguish-
                        # able from a scalar once drilled into.
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
        usages = state.xref_cache.get(target)
        if usages is None:
            usages = find_usages(target, state.data_types, state.tag_index)
            state.xref_cache[target] = usages
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

    # Waitress, not Flask's built-in server. The built-in one prints a
    # warning on every start telling you not to deploy it, and it is right:
    # it is a development server. This runs in a container as the container's
    # only job, which is deployment, so the answer is to serve it properly
    # rather than to silence a true statement. Waitress is pure Python and
    # works on Windows, where the capture machines are.
    #
    # Concurrency either way: the "2 levels deep" treemap toggle fires one
    # /api/node fetch per visible drillable tile CONCURRENTLY from the
    # browser. Served serially, "Controller Tags" on a real program becomes a
    # multi-second stall for no reason -- every one of those requests is
    # independent read-only work against the same already-parsed DocState.
    try:
        from waitress import serve as _serve
    except ImportError:
        # Still runnable from a source checkout without the dependency. The
        # warning it prints is accurate, so it is left alone.
        app.run(host=host, port=port, debug=False, threaded=True)
        return
    _serve(app, host=host, port=port, threads=8, ident=None)
