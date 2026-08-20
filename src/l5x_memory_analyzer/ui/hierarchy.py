"""Turns the flat SizeEntry report into the two shapes the UI needs:
a nested {name, value|children} tree for the treemap, and a data-type
rollup for the type-utilization pane. Pure data transforms, no Flask/HTTP
here so they're unit-testable on their own.
"""

from __future__ import annotations

from l5x_memory_analyzer.parser.tags import CONTROLLER_SCOPE
from l5x_memory_analyzer.sizing.report import SizeEntry


def _scope_and_name(path: str) -> tuple[str, str]:
    scope, _, name = path.partition("/")
    return scope, name


def build_hierarchy(entries: list[SizeEntry]) -> dict:
    """Root -> {"Controller Tags", "Program: <name>", ...} -> leaf tag nodes.

    Grouping is derived from SizeEntry.path (`<scope>/<tag name>`, see
    parser/tags.py Tag.path) rather than adding new fields, since the scope
    is already fully recoverable from it.
    """
    groups: dict[str, list[dict]] = {}
    group_order: list[str] = []

    for e in entries:
        scope, name = _scope_and_name(e.path)
        group_name = "Controller Tags" if scope == CONTROLLER_SCOPE else f"Program: {scope.split(':', 1)[1]}"
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
