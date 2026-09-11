"""Turns the flat SizeEntry report into the two shapes the UI needs:
a nested {name, value|children} tree for the treemap, and a data-type
rollup for the type-utilization pane. Pure data transforms, no Flask/HTTP
here so they're unit-testable on their own.
"""

from __future__ import annotations

from l5x_memory_analyzer.parser.datatypes import DataTypeDef
from l5x_memory_analyzer.parser.tags import CONTROLLER_SCOPE
from l5x_memory_analyzer.sizing.constants import MemoryModel
from l5x_memory_analyzer.sizing.tree import expand_definition_children
from l5x_memory_analyzer.sizing.report import SizeEntry
from l5x_memory_analyzer.sizing.tree import has_children as _has_children


def _scope_and_name(path: str) -> tuple[str, str]:
    scope, _, name = path.partition("/")
    return scope, name


UDT_GROUP_NAME = "User-Defined Data Types"
AOI_GROUP_NAME = "Add-On Instructions"



def _aoi_definition_containers(
    definition_node: dict,
    data_types: dict[str, DataTypeDef] | None,
    model: MemoryModel | None,
) -> list[dict]:
    """Split an AOI's one-time definition cost into Overhead and Tags.

    An AOI reads as three things to the person looking at it -- what the
    definition costs to exist, what its parameters and local tags cost,
    and what its routines cost -- and the flat member list buried the
    first two together. The caller adds the Routines container, because
    those costs are separate SizeEntries that already exist rather than
    part of the definition figure.

    Deliberately does NOT invent rows on an AOI INSTANCE. A definition's
    overhead and routines are one-time costs charged once at the
    definition; repeating them under each instance would make the tree
    stop summing to the controller total, which is the one property the
    whole treemap depends on.

    Falls back to the single flat node whenever the split cannot be
    computed, so a caller without data_types/model still gets a tree.
    """
    name = definition_node.get("name")
    path = definition_node.get("path") or ""
    if not (data_types and model) or name not in data_types:
        return [{**definition_node, "name": "Definition"}]
    if not data_types[name].is_aoi:
        return [{**definition_node, "name": "Definition"}]
    try:
        children = expand_definition_children(name, data_types, model)
    except Exception:
        return [{**definition_node, "name": "Definition"}]

    overhead = [c for c in children if c.data_type == "OVERHEAD"]
    tags = [c for c in children if c.data_type != "OVERHEAD"]

    def wrap(child) -> dict:
        return {
            "name": child.name, "path": f"{path}{child.segment}",
            "value": child.bytes, "data_type": child.data_type,
            "basis": child.basis,
        }

    containers = []
    if overhead:
        containers.append({
            "name": "Overhead", "path": f"{path}/Overhead",
            "value": sum(c.bytes for c in overhead),
            "children": [wrap(c) for c in overhead],
        })
    if tags:
        containers.append({
            "name": "Tags", "path": f"{path}/Tags",
            "value": sum(c.bytes for c in tags),
            "children": [wrap(c) for c in tags],
        })
    return containers or [{**definition_node, "name": "Definition"}]

def build_hierarchy(
    entries: list[SizeEntry],
    data_types: dict[str, DataTypeDef] | None = None,
    model: MemoryModel | None = None,
    tag_dimensions: dict[str, tuple[int, ...]] | None = None,
    program_to_task: dict[str, str] | None = None,
    aoi_names: set[str] | frozenset[str] | None = None,
) -> dict:
    """Root -> {"Controller Tags", "Program: <name>", ...} -> leaf tag nodes.

    Grouping is derived from SizeEntry.path (`<scope>/<tag name>`, see
    parser/tags.py Tag.path) rather than adding new fields, since the scope
    is already fully recoverable from it. data_types/model/tag_dimensions are
    optional so existing callers that only need the flat rollup (no
    drill-down) don't have to supply them -- has_children just defaults
    false without them. tag_dimensions matters because SizeEntry itself only
    carries a tag's base data_type, not its array dimensions -- without the
    real dimensions a 5000-element DINT array tag would wrongly look like a
    plain scalar DINT (not drillable) rather than an array (drillable).
    """
    groups: dict[str, list[dict]] = {}
    group_order: list[str] = []
    # routine_logic entries (2026-08-27, Phase 5 "Program -> Routine"
    # nesting) are kept OUT of a program's flat tag list and collected
    # here instead, keyed by that program's own group_name -- each
    # program's Routines get their own "Routines" subgroup rather than
    # sitting as flat siblings next to that program's tags, so a program
    # with both tags and logic doesn't visually conflate "data I own" with
    # "logic that runs in me". Task-level grouping (Task -> Program) is
    # NOT done here -- the parser has zero awareness of Controller/Tasks
    # (see docs/OPEN_QUESTIONS.md's per-Task-overhead item), so there is
    # no real task->program mapping to group by yet, not an oversight.
    # Rung-level lists are deliberately never built -- too granular to be
    # visually useful (see docs/TASKS.md Phase 5's own parenthetical).
    routine_groups: dict[str, list[dict]] = {}

    # udt_definition (path "udt_definitions/<Name>") and project_baseline
    # (path "project_baseline", no "/" at all) don't fit the <scope>/<name>
    # tag-path convention every other category follows -- routing them
    # through the Controller-Tags/Program-scope split below crashed with an
    # IndexError (2026-08-23 fix: found while wiring in the new
    # project_baseline entry, but udt_definition had the exact same latent
    # bug already -- any real file with a UDT definition would have crashed
    # the live UI). Both get their own dedicated top-level group instead,
    # never drillable (has_children always false -- neither has a nested
    # structure to descend into).
    NON_TAG_GROUPS = {
        "udt_definition": UDT_GROUP_NAME,
        "project_baseline": "Project Overhead",
        # task_program_shell (2026-08-27, OQ-TASKOVERHEAD wiring): a single
        # once-per-file entry, path "task_program_shell" with no "/" --
        # same non-tag-path shape as project_baseline above, same fix.
        "task_program_shell": "Project Overhead",
        # module_io (2026-08-27, OQ-MODULEIO wiring): path is "modules/
        # <name>", which DOES contain "/" -- but "modules" isn't a real
        # Program/Controller-Tags scope, so the split below would still
        # try scope.split(':', 1)[1] and crash the same way. Own top-level
        # group instead, same fix shape as the others above.
        "module_io": "I/O Modules",
        # alarm_condition (2026-09-04): alarms get their own tree section,
        # the same way axes do. Path is
        # "alarms/<host tag>", which contains "/" but whose first segment
        # is not a Program/Controller scope -- so without this entry the
        # split below would have produced a bogus "Program: " group from
        # scope.split(':', 1), the identical latent bug already fixed twice
        # for udt_definition and module_io. Alarms are worth their own root
        # group on merit too: they were the single largest unpriced item in
        # the model when they were found (3,463 conditions missed on one
        # real file), and one condition costs 500 bytes plus its associated
        # tags, so an alarm-heavy program can hide megabytes that otherwise
        # appear scattered across the tags they hang off.
        "alarm_condition": "Alarm Conditions",
    }

    # Axis/motion tags (2026-08-28, "the UI treeview needs to have
    # the Axis (CIP_Drive, Virtual, etc) broken out at the root level").
    # These are ordinary Controller/Program-scoped tags in the L5X (same
    # category/path shape as any other tag), just typed as one of the
    # predefined motion structures -- so unlike the NON_TAG_GROUPS above
    # (which key off e.category), this keys off e.data_type and pulls
    # matching tags OUT of "Controller Tags"/"Program: X" into their own
    # root group instead, regardless of scope. Real predefined motion
    # types this project already models (memory_model.yaml
    # predefined_structures) -- MOTION_GROUP and COORDINATE_SYSTEM
    # included alongside the AXIS_* types themselves since they're part
    # of the same motion-configuration subsystem, not separate axes.
    AXIS_DATA_TYPES = {
        "AXIS_CIP_DRIVE", "AXIS_SERVO", "AXIS_VIRTUAL",
        "COORDINATE_SYSTEM", "MOTION_GROUP",
    }
    AXIS_GROUP_NAME = "Axis Definitions"

    for e in entries:
        if e.category in NON_TAG_GROUPS:
            group_name = NON_TAG_GROUPS[e.category]
            # Alarm entries carry the host tag in the path and a
            # "<n> condition(s)" summary in data_type, so the tree label has
            # to come from the path -- using data_type would render every
            # row as an indistinguishable count.
            name = e.path.partition("/")[2] if e.category == "alarm_condition" else e.data_type
            # udt_definition entries ARE drillable now (2026-08-26, /api/node's
            # "udt_definitions/<Name>" branch) -- locals+params/members
            # breakdown of the definition's own cost, see sizing/tree.py's
            # expand_definition_children. project_baseline has no breakdown
            # (data_types lookup would miss it entirely, correctly false).
            kids = e.category == "udt_definition" and data_types is not None and name in data_types
            # A UDT and an Add-On Instruction are different things to a user
            # even though both are priced as "udt_definition" here. Split
            # them so "User-Defined Data Types" means what it says and AOIs
            # are findable as AOIs.
            if name in (aoi_names or ()):
                group_name = AOI_GROUP_NAME
        elif e.path.startswith("aoi_definitions/"):
            # AOI-internal logic. It belongs UNDER its own AOI rather than
            # loose in the definitions pool -- a routine called "Logic" tells
            # you nothing without the AOI it came from.
            group_name = AOI_GROUP_NAME
            parts = e.path.split("/")
            name = f"{parts[1]}/{parts[2]}" if len(parts) > 2 else parts[-1]
            kids = False
        else:
            scope, name = _scope_and_name(e.path)
            group_name = (
                AXIS_GROUP_NAME if e.data_type in AXIS_DATA_TYPES
                else "Controller Tags" if scope == CONTROLLER_SCOPE
                else f"Program: {scope.split(':', 1)[1]}"
            )
            dims = (tag_dimensions or {}).get(e.path, ())
            kids = (
                _has_children(e.data_type, dims, data_types, model)
                if data_types is not None and model is not None
                else False
            )

        if group_name not in groups:
            groups[group_name] = []
            group_order.append(group_name)

        leaf = {
            "name": name,
            "path": e.path,
            "value": e.bytes,
            "data_type": e.data_type,
            "tier": e.tier,
            "basis": e.basis,
            "has_children": kids,
            # Emitted so the UI can label an array as "Tag[64]" rather than
            # "Tag" -- the dimensions were already resolved here, they were
            # just never passed on.
            "dimensions": list(dims) if dims else [],
        }
        if e.category == "routine_logic":
            routine_groups.setdefault(group_name, []).append(leaf)
        else:
            groups[group_name].append(leaf)

    children = []
    for g in group_order:
        kids = list(groups[g])
        routines = routine_groups.get(g)
        # A program's tags go in their own "Program Tags" container, the same
        # way its routines already do. Without it the single "Routines" tile
        # sits among dozens of loose tag tiles and is easy to lose; with both
        # containers a program reads as "here are the routines, here are the
        # tags". Only applied where there is actually something to contain --
        # a non-program group (Controller Tags, Modules) keeps its flat shape.
        if g == AOI_GROUP_NAME and routines:
            # An AOI's internal routines belong UNDER that AOI, not in a
            # sibling folder: a routine called "Logic" is meaningless without
            # the AOI it came from. Routine names arrive as "<AOI>/<Routine>".
            by_aoi: dict[str, list[dict]] = {}
            for r in routines:
                owner, _, rname = str(r["name"]).partition("/")
                if rname:
                    r = {**r, "name": rname}
                by_aoi.setdefault(owner, []).append(r)
            attached = []
            for k in kids:
                own = by_aoi.pop(k["name"], None)
                if own:
                    attached.append({
                        "name": k["name"], "path": k["path"],
                        "children": _aoi_definition_containers(k, data_types, model)
                        + [{
                            "name": "Routines", "path": f"{k['path']}/Routines",
                            "value": sum(r.get("value", 0) for r in own),
                            "children": own,
                        }],
                    })
                else:
                    attached.append({
                        "name": k["name"], "path": k["path"],
                        "children": _aoi_definition_containers(k, data_types, model),
                    } if _aoi_definition_containers(k, data_types, model) else k)
            # An AOI with routines but no priced definition still shows up.
            for owner, own in by_aoi.items():
                attached.append({
                    "name": owner, "path": f"aoi_definitions/{owner}", "children": own,
                })
            kids = attached
        elif g.startswith("Program: "):
            # Only a real program gets the Tags/Routines split -- the other
            # groups (Controller Tags, Modules) have no such two-part shape.
            if routines and kids:
                tags_total = sum(k["value"] for k in kids if "value" in k)
                kids = [{
                    "name": "Program Tags", "path": f"{g}/Program Tags",
                    "value": tags_total, "children": kids,
                }]
            if routines:
                routines_total = sum(r["value"] for r in routines)
                kids.append({
                    "name": "Routines", "path": f"{g}/Routines", "value": routines_total,
                    "children": routines,
                })
        elif routines:
            routines_total = sum(r["value"] for r in routines)
            kids.append({
                "name": "Routines", "path": f"{g}/Routines", "value": routines_total,
                "children": routines,
            })
        children.append({"name": g, "path": g, "children": kids})

    if program_to_task:
        children = _nest_programs_under_tasks(children, program_to_task)

    total_bytes = sum(e.bytes for e in entries)
    return {"name": "root", "path": "", "value": total_bytes, "children": children}


def _nest_programs_under_tasks(children: list[dict], program_to_task: dict[str, str]) -> list[dict]:
    """Re-groups top-level "Program: X" children under a "Task: Y" parent
    where X's owning Task is known (real, L5X-stated Controller/Tasks/
    ScheduledProgram relationship -- see parser/tasks.py -- not a fitted
    formula, so no byte-cost question is involved: a Task's displayed
    total is just the sum of its already-correct Programs). "Controller
    Tags"/"Type Definitions"/"Project Overhead" and any program with no
    known Task (real gap in the source L5X, or program_to_task simply not
    supplied) are left as top-level siblings, unchanged -- this pass only
    ever adds a layer, never drops or renames anything.
    """
    result: list[dict] = []
    task_groups: dict[str, list[dict]] = {}
    task_order: list[str] = []

    for child in children:
        name = child["name"]
        if name.startswith("Program: "):
            program_name = name[len("Program: "):]
            task_name = program_to_task.get(program_name)
            if task_name:
                if task_name not in task_groups:
                    task_groups[task_name] = []
                    task_order.append(task_name)
                task_groups[task_name].append(child)
                continue
            # No owning Task. In real Logix that means the program is
            # UNSCHEDULED -- the controller fault handler / power-up
            # handler live here, as do programs a developer has parked out
            # of the scan. 2026-09-05: the controller error-handling
            # task/program must be included in the size calculation and
            # visible in the web UI.
            #
            # It was never missed in the SIZING -- report.py counts every
            # <Program> element for the shell decomposition whether or not
            # a Task schedules it, and its tags/routines size normally --
            # but the tree rendered it as a plain "Program: X" sibling,
            # indistinguishable from a scheduled one. An unscheduled
            # program still consumes controller memory while never
            # executing, which is exactly the kind of thing this tool
            # exists to surface, so it now says so.
            child = {**child, "name": f"{name} (unscheduled)", "unscheduled": True}
        result.append(child)

    for task_name in task_order:
        programs = task_groups[task_name]
        task_total = sum(sum(c["value"] for c in p["children"]) for p in programs)
        result.append({
            "name": f"Task: {task_name}", "path": f"Task: {task_name}", "value": task_total,
            "children": programs,
        })
    return result


def type_utilization(entries: list[SizeEntry]) -> list[dict]:
    """Data-type -> total bytes / % of total, across the whole project (not
    just top-level categories) -- the WinDirStat 'file type' pane analog.
    """
    totals: dict[str, int] = {}
    for e in entries:
        totals[e.data_type] = totals.get(e.data_type, 0) + e.bytes

    grand_total = sum(totals.values())
    rows = [
        {
            "data_type": dt,
            "bytes": b,
            "pct_of_total": (b / grand_total * 100) if grand_total else 0.0,
        }
        for dt, b in totals.items()
    ]
    return sorted(rows, key=lambda r: r["bytes"], reverse=True)
