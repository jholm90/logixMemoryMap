"""Turns the flat SizeEntry report into the two shapes the UI needs:
a nested {name, value|children} tree for the treemap, and a data-type
rollup for the type-utilization pane. Pure data transforms, no Flask/HTTP
here so they're unit-testable on their own.
"""

from __future__ import annotations

from l5x_memory_analyzer.parser.datatypes import DataTypeDef
from l5x_memory_analyzer.parser.tags import CONTROLLER_SCOPE
from l5x_memory_analyzer.sizing.constants import MemoryModel
from l5x_memory_analyzer.sizing.report import SizeEntry
from l5x_memory_analyzer.sizing.tree import has_children as _has_children


def _scope_and_name(path: str) -> tuple[str, str]:
    scope, _, name = path.partition("/")
    return scope, name


def build_hierarchy(
    entries: list[SizeEntry],
    data_types: dict[str, DataTypeDef] | None = None,
    model: MemoryModel | None = None,
    tag_dimensions: dict[str, tuple[int, ...]] | None = None,
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
    NON_TAG_GROUPS = {"udt_definition": "Type Definitions", "project_baseline": "Project Overhead"}

    for e in entries:
        if e.category in NON_TAG_GROUPS:
            group_name = NON_TAG_GROUPS[e.category]
            name = e.data_type
            # udt_definition entries ARE drillable now (2026-08-26, /api/node's
            # "udt_definitions/<Name>" branch) -- locals+params/members
            # breakdown of the definition's own cost, see sizing/tree.py's
            # expand_definition_children. project_baseline has no breakdown
            # (data_types lookup would miss it entirely, correctly false).
            kids = e.category == "udt_definition" and data_types is not None and name in data_types
        else:
            scope, name = _scope_and_name(e.path)
            group_name = "Controller Tags" if scope == CONTROLLER_SCOPE else f"Program: {scope.split(':', 1)[1]}"
            dims = (tag_dimensions or {}).get(e.path, ())
            kids = (
                _has_children(e.data_type, dims, data_types, model)
                if data_types is not None and model is not None
                else False
            )

        if group_name not in groups:
            groups[group_name] = []
            group_order.append(group_name)
        groups[group_name].append(
            {
                "name": name,
                "path": e.path,
                "value": e.bytes,
                "data_type": e.data_type,
                "tier": e.tier,
                "basis": e.basis,
                "has_children": kids,
            }
        )

    children = [
        {"name": g, "path": g, "children": groups[g]}
        for g in group_order
    ]
    total_bytes = sum(e.bytes for e in entries)
    return {"name": "root", "path": "", "value": total_bytes, "children": children}


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
