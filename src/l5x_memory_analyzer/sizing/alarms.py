"""Cost of tag-based alarm conditions. Exact, not fitted.

Solved 2026-09-05 from the 37-file `alarmcond_*` batch, which reproduces
with ZERO residual on every captured point:

    total = file_base                      (800, once, if any alarm exists)
          + per_condition * n_alarms       (500 each)
          + per associated tag, by the resolved type of what it points AT
            (BOOL 88, DINT/REAL 92, STRING 256)

Everything else about an alarm is FREE, measured not assumed: HMIGroup
(absent, 4 or 16 characters), alarm Name length (8/16/32/40), Severity,
OnDelay, Latched and AckRequired all read byte-identical to the control.
Alarm cost depends only on how many alarms there are and what their
associated tags point at.

Why it mattered: 3,463 of these across the real corpus, 200-600 in every
real program, all previously priced at zero. Pricing them dropped
real-program mean |error| from 3.29% to 0.63% -- and forced the composite
AOI/JSR surcharge to be refitted from 52/21 down to 22/3, because those
rates had been silently standing in for alarm cost all along.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from l5x_memory_analyzer.parser.alarms import AlarmCondition, parse_alarm_conditions


def _resolve_assoc_type(
    ref: str, tag_types: dict[str, str], udt_members: dict[str, dict[str, str]]
) -> str | None:
    """Data type an AssocTagN reference points at, following UDT members.

    Real references look like `Alarms_Edger1[0].Number` -- an array element
    of a UDT, then a member of it -- so a lookup that only handled bare tag
    names would resolve almost nothing on a real file.
    """
    parts = ref.split(".")
    current = tag_types.get(parts[0].split("[")[0])
    for part in parts[1:]:
        if current is None:
            return None
        current = udt_members.get(current, {}).get(part.split("[")[0])
    return current


def size_alarm_conditions(
    root: ET.Element,
    model,
    tag_types: dict[str, str],
    udt_members: dict[str, dict[str, str]],
) -> tuple[list[tuple[str, str, str, int, str]], list[AlarmCondition]]:
    """(entries, conditions). One entry per alarmed HOST TAG, not per alarm:
    a real file has hundreds of alarms on a handful of arrays, and hundreds
    of one-line entries would bury every other row in the report."""
    conditions = parse_alarm_conditions(root)
    if not conditions:
        return [], []

    cfg = model.alarm_conditions
    by_host: dict[str, list[AlarmCondition]] = {}
    for c in conditions:
        by_host.setdefault(c.host_tag, []).append(c)

    entries: list[tuple[str, str, str, int, str]] = []
    # The file-wide base is charged once, on the first host tag by name, so
    # it lands somewhere real in the drill-down rather than in a phantom row.
    remaining_base = cfg.file_base
    for host in sorted(by_host):
        alarms = by_host[host]
        total = remaining_base + sum(
            _condition_cost(c, cfg, tag_types, udt_members) for c in alarms
        )
        remaining_base = 0
        entries.append((
            f"alarms/{host}", "alarm_condition",
            f"{len(alarms)} condition(s)", total, cfg.confidence,
        ))
    return entries, conditions


def _condition_cost(c: AlarmCondition, cfg, tag_types, udt_members) -> int:
    """What one alarm condition costs: the flat per-condition rate plus
    whatever each of its associated tags resolves to."""
    total = cfg.per_condition
    for ref in c.assoc_tags:
        total += cfg.assoc_tag_cost(_resolve_assoc_type(ref, tag_types, udt_members))
    return total


def alarm_lookup_tables(root: ET.Element) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    """The two resolution tables alarm sizing needs, built from the file.

    report.py builds these inline because it already has the parsed tags
    and data types to hand; anything else that needs to price alarms (the
    UI's per-condition drill) would otherwise have to duplicate exactly
    how it does it, which is how two code paths start disagreeing about a
    number.
    """
    from l5x_memory_analyzer.parser.datatypes import parse_data_types
    from l5x_memory_analyzer.parser.tags import parse_tags

    tag_types = {t.name: t.data_type for t in parse_tags(root) if t.data_type}
    udt_members = {
        name: {mem.name: mem.data_type for mem in defn.members}
        for name, defn in parse_data_types(root).items()
    }
    return tag_types, udt_members


def alarm_conditions_for_host(
    root: ET.Element,
    model,
    host: str,
    tag_types: dict[str, str] | None = None,
    udt_members: dict[str, dict[str, str]] | None = None,
) -> list[dict]:
    """Every individual alarm condition on one host tag, priced.

    The report deliberately charges alarms one entry per HOST TAG -- a real
    file has hundreds of alarms on a handful of arrays, and hundreds of
    one-line rows would bury every other item in it. That is right for the
    report and wrong for the tree, where "200 conditions" rendered as a
    single undifferentiated block. These rows sum to exactly that entry:
    same per-condition rate, same associated-tag resolution, plus the
    once-per-file base where the report charges it (the alphabetically
    first host).
    """
    conditions = parse_alarm_conditions(root)
    if not conditions:
        return []
    if tag_types is None or udt_members is None:
        tag_types, udt_members = alarm_lookup_tables(root)

    cfg = model.alarm_conditions
    by_host: dict[str, list[AlarmCondition]] = {}
    for c in conditions:
        by_host.setdefault(c.host_tag, []).append(c)
    if host not in by_host:
        return []

    rows: list[dict] = []
    if host == sorted(by_host)[0] and cfg.file_base:
        rows.append({
            "name": "Alarm subsystem base",
            "bytes": cfg.file_base,
            "detail": "charged once per file, not per alarm",
            "condition_type": "",
            "severity": "",
        })
    for c in by_host[host]:
        # A real Input reads "[0]" or ".Fault" -- relative to the host tag,
        # which is the node above this one. Qualified here so the row says
        # what it watches on its own.
        ref = c.input_ref
        if ref.startswith(("[", ".")):
            ref = f"{c.host_tag}{ref}"
        rows.append({
            "name": c.name,
            "bytes": _condition_cost(c, cfg, tag_types, udt_members),
            "detail": ref,
            "condition_type": c.condition_type,
            "severity": c.severity,
        })
    return rows
