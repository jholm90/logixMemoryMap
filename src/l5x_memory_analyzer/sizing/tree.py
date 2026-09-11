"""Lazy, one-level-at-a-time recursive drill-down for the UI treemap.

2026-08-20 requirement: infinite depth, no masking a large array just because
it's nested inside something else -- every level, down to individual BOOL
bits, must be drillable. Materializing that whole tree eagerly for a 40k-tag
project with 10k-element arrays would be enormous, so this computes exactly
one level of children at a time, on demand (`ui/server.py`'s /api/node),
mirroring the same recursion `sizing/udt.py` already does for totals -- this
module must never disagree with udt.py's numbers, so it delegates every byte
calculation back to udt.py rather than recomputing independently.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from l5x_memory_analyzer.parser.datatypes import DataTypeDef, Member
from l5x_memory_analyzer.sizing.confidence import weakest
from l5x_memory_analyzer.sizing.constants import MemoryModel
from l5x_memory_analyzer.sizing.udt import (
    RecursiveUdtError,
    UnknownDataTypeError,
    compute_array_size,
    compute_element_size,
    custom_string_maxlen,
)


class NotDrillableError(ValueError):
    """The resolved node is a true leaf -- no further children exist."""


# Predefined structures with a real, confirmed per-field byte breakdown
# (each field an equal 1/3 share of the total, see _expand_predefined_
# structure) -- deliberately NOT every key in model.predefined_structures.
# The SFC/FBD-family additions (2026-08-27) only have a confirmed
# TOTAL (read off real Decorated-XML L5K array length), not a confirmed
# per-field byte attribution or even a consistent field count (SFC_STEP
# has 7 fields, SFC_ACTION has 4, RATE_LIMITER has 23...) -- showing them
# via the generic 3-way split would be a fabricated breakdown the total
# doesn't actually support. They stay correctly-sized, non-drillable
# leaves until a real per-field derivation exists.
_THREE_FIELD_PREDEFINED = {"TIMER", "COUNTER", "CONTROL"}


@dataclass(frozen=True)
class Child:
    name: str  # display label, e.g. "Speed" or "[42]"
    segment: str  # token to append to the path for a further drill, e.g. ".Speed" or "[42]"
    data_type: str
    dimensions: tuple[int, ...]
    bytes: float  # float for packed-BOOL-array elements' proportional share; int otherwise
    basis: str
    has_children: bool
    # Set only on a BIT alias member: where its storage actually lives.
    # A zero-byte member with no explanation reads as a gap in the model;
    # naming the backing SINT and bit says the size is zero because the
    # bytes are charged elsewhere, which is a fact, not an absence.
    alias_of: str | None = None
    alias_bit: int | None = None


def has_children(
    data_type: str, dimensions: tuple[int, ...], data_types: dict[str, DataTypeDef], model: MemoryModel
) -> bool:
    if dimensions:
        return math.prod(dimensions) > 0
    if data_type in data_types:
        return True  # UDT/AOI (merged) and custom string types all expose at least LEN+DATA or members
    if data_type in _THREE_FIELD_PREDEFINED:
        return True  # TIMER/COUNTER/CONTROL expose their 3 documented fields
    if data_type == "STRING":
        return True  # built-in STRING: LEN + DATA
    return False  # plain atomic scalar (SINT/INT/DINT/LINT/REAL), standalone BOOL, or a
    # predefined structure with a confirmed total but no confirmed per-field
    # breakdown yet (SFC_STEP/SFC_ACTION/etc, model.predefined_structures
    # but not _THREE_FIELD_PREDEFINED) -- all true leaves for drill purposes.


def subtree_confidence(
    data_type: str,
    dimensions: tuple[int, ...],
    data_types: dict[str, DataTypeDef],
    model: MemoryModel,
    _stack: frozenset[str] = frozenset(),
) -> dict[str, float]:
    """Byte-weighted {tier: bytes} over the WHOLE subtree under a node.

    The UI used to derive this by walking whatever children the browser
    had lazily fetched, which gave a node one answer before it was
    expanded and a different one afterwards. Computing it here makes the
    answer a property of the data instead of a property of the browsing
    history.

    Arrays are summarised by pricing ONE element and multiplying, rather
    than walking N identical elements -- a 1,024-element array of a UDT
    would otherwise cost 1,024 identical traversals to reach the same
    numbers.
    """
    acc: dict[str, float] = {"KNOWN": 0.0, "FITTED": 0.0, "ASSUMED": 0.0, "UNKNOWN": 0.0}

    def tally(child: Child, multiplier: int = 1) -> None:
        if child.has_children:
            try:
                inner = subtree_confidence(
                    child.data_type, child.dimensions, data_types, model, _stack
                )
            except (NotDrillableError, RecursiveUdtError, UnknownDataTypeError):
                inner = None
            if inner and sum(inner.values()):
                for tier, value in inner.items():
                    acc[tier] = acc.get(tier, 0.0) + value * multiplier
                return
        tier = (child.basis or "UNKNOWN").upper()
        acc[tier if tier in acc else "UNKNOWN"] += child.bytes * multiplier

    if dimensions:
        count = math.prod(dimensions)
        if count <= 0:
            return acc
        # One representative element, scaled. Element children are
        # identical by construction, so this is exact, not an estimate.
        element = expand_children(data_type, dimensions, data_types, model, _stack)[0]
        tally(element, count)
        return acc

    for child in expand_children(data_type, dimensions, data_types, model, _stack):
        tally(child)
    return acc


def expand_children(
    data_type: str,
    dimensions: tuple[int, ...],
    data_types: dict[str, DataTypeDef],
    model: MemoryModel,
    _stack: frozenset[str] = frozenset(),
) -> list[Child]:
    """Exactly one level of children for (data_type, dimensions). Raises
    NotDrillableError if this node is a true leaf (nothing to expand)."""
    if dimensions:
        return _expand_array(data_type, dimensions, data_types, model, _stack)
    if data_type in data_types:
        return _expand_udt(data_type, data_types, model, _stack)
    if data_type in _THREE_FIELD_PREDEFINED:
        return _expand_predefined_structure(data_type, model)
    if data_type == "STRING":
        return _expand_builtin_string(model)
    raise NotDrillableError(data_type)


def _expand_array(
    data_type: str,
    dimensions: tuple[int, ...],
    data_types: dict[str, DataTypeDef],
    model: MemoryModel,
    _stack: frozenset[str],
) -> list[Child]:
    count = math.prod(dimensions)

    if data_type == "BOOL":
        # Bit-packed -- individual elements have no addressable byte offset.
        # Give each an even proportional share of the packed total so the
        # array is still fully drillable (never masked), while the tooltip
        # can make clear this is a visualization share, not a real address.
        total_bytes, basis = compute_array_size(data_type, dimensions, data_types, model, _stack)
        per_element = total_bytes / count if count else 0.0
        return [
            Child(f"[{i}]", f"[{i}]", "BOOL", (), per_element, basis, has_children=False)
            for i in range(count)
        ]

    element_bytes, element_basis = compute_element_size(data_type, data_types, model, _stack)
    kids = has_children(data_type, (), data_types, model)
    return [
        Child(f"[{i}]", f"[{i}]", data_type, (), element_bytes, element_basis, kids)
        for i in range(count)
    ]


def _expand_udt(
    name: str, data_types: dict[str, DataTypeDef], model: MemoryModel, _stack: frozenset[str]
) -> list[Child]:
    if name in _stack:
        raise RecursiveUdtError(name)
    udt = data_types[name]
    stack = _stack | {name}

    if udt.is_string_family:
        return _expand_string_family_members(udt, model)

    children = []
    for member in udt.members:
        if member.is_bit_alias:
            # 0-byte, but still surfaced so a UDT's individual BOOL bits are
            # visible/clickable down to "bit level" rather than disappearing
            # into their backing SINT's byte count.
            children.append(Child(
                member.name, f".{member.name}", "BIT", (), 0, "KNOWN", False,
                alias_of=member.target, alias_bit=member.bit_number,
            ))
            continue
        dims = (member.dimension,) if member.dimension > 0 else ()
        size, basis = compute_array_size(member.data_type, dims, data_types, model, stack)
        kids = has_children(member.data_type, dims, data_types, model)
        children.append(Child(member.name, f".{member.name}", member.data_type, dims, size, basis, kids))
    return children


def _expand_string_family_members(udt: DataTypeDef, model: MemoryModel) -> list[Child]:
    data_member = next((m for m in udt.members if m.name == "DATA"), None)
    n = data_member.dimension if data_member else 0
    return [
        Child("LEN", ".LEN", "DINT", (), model.string.len_field_bytes, "KNOWN", False),
        Child("DATA", ".DATA", "SINT", (n,), n, model.string.custom_confidence, has_children=n > 0),
    ]


def _expand_builtin_string(model: MemoryModel) -> list[Child]:
    return [
        Child("LEN", ".LEN", "DINT", (), model.string.len_field_bytes, "KNOWN", False),
        Child(
            "DATA", ".DATA", "SINT", (model.string.default_data_bytes,),
            model.string.default_data_bytes, model.string.confidence,
            has_children=model.string.default_data_bytes > 0,
        ),
    ]


def _expand_predefined_structure(data_type: str, model: MemoryModel) -> list[Child]:
    struct = model.predefined_structures[data_type]
    third_name = "POS" if data_type == "CONTROL" else "ACC"
    # See docs/MEMORY_MODEL.md predefined structures: 1 status DINT + 2 data
    # DINTs = struct.bytes total (12), split evenly since all 3 are DINTs.
    each = struct.bytes // 3
    return [
        Child("Status", ".Status", "DINT", (), each, struct.confidence, False),
        Child("PRE", ".PRE", "DINT", (), each, struct.confidence, False),
        Child(third_name, f".{third_name}", "DINT", (), each, struct.confidence, False),
    ]


def expand_definition_children(
    name: str, data_types: dict[str, DataTypeDef], model: MemoryModel
) -> list[Child]:
    """Breakdown of a UDT/AOI/custom-string *definition*'s own one-time
    cost into its contributing pieces (2026-08-26, "click-to-drill
    into a defs pool node -> locals+params breakdown").

    NOT the same drill as expand_children/_expand_udt above, which breaks
    an INSTANCE's data size into its members' own byte sizes. A
    definition's cost formula (base + per-member/per-item flat rate +
    name-length [+ bool-run bonus]) isn't naturally member-size-
    attributable -- per_member/per_declared_item are flat rates per
    declared thing, independent of that thing's own data size -- so each
    declared member/param/local gets an even share of that flat rate,
    labeled by its real name, alongside separate rows for the parts that
    aren't per-member (base, name length, BOOL-run packing bonus). Always
    exactly one level deep (every child here has_children=False) -- this
    is a cost-attribution breakdown, not a further-drillable structure.
    """
    dtdef = data_types[name]
    if dtdef.is_string_family:
        return _expand_string_definition(dtdef, model)
    if dtdef.is_aoi:
        return _expand_aoi_definition(dtdef, model)
    return _expand_plain_udt_definition(name, dtdef, model)


def _expand_plain_udt_definition(name: str, udt: DataTypeDef, model: MemoryModel) -> list[Child]:
    declared_members = [m for m in udt.members if not m.hidden]
    bool_runs = [m for m in udt.members if m.hidden]
    conf = model.udt_definition.confidence
    name_cost = model.udt_definition.name_per_8_chars * math.ceil(len(name) / 8)
    children = [
        Child("Base + type name", ".base", "OVERHEAD", (), model.udt_definition.base + name_cost, conf, False)
    ]
    for m in declared_members:
        children.append(Child(m.name, f".{m.name}", m.data_type, (), model.udt_definition.per_member, conf, False))
    for i, _ in enumerate(bool_runs, start=1):
        children.append(
            Child(f"BOOL packing (run {i})", f".boolrun{i}", "OVERHEAD", (),
                  model.udt_definition.bool_run_bonus, conf, False)
        )
    return children


def _expand_aoi_definition(aoi: DataTypeDef, model: MemoryModel) -> list[Child]:
    conf = model.aoi_definition.confidence
    declared_items = [m for m in aoi.members if m.name not in ("EnableIn", "EnableOut")]
    children = [Child("Base", ".base", "OVERHEAD", (), model.aoi_definition.base, conf, False)]
    # Each member carries its flat declared-item rate PLUS the cost of its own
    # name, so the breakdown still sums to compute_aoi_definition_cost and a
    # long-named member visibly costs more than a short-named one -- which is
    # the whole point of showing this per member rather than as one lump.
    member_conf = weakest(conf, model.aoi_definition.member_name_confidence)
    for m in declared_items:
        children.append(Child(
            m.name, f".{m.name}", m.data_type, (),
            model.aoi_definition.per_declared_item
            + model.aoi_definition.member_name_bytes([m.name]),
            member_conf, False,
        ))
    name_conf = weakest(conf, model.aoi_definition.name_length_bucket_confidence)
    children.append(
        Child("Type name length", ".namelen", "OVERHEAD", (),
              model.aoi_definition.name_length_bytes(aoi.name), name_conf, False)
    )
    return children


def _expand_string_definition(udt: DataTypeDef, model: MemoryModel) -> list[Child]:
    conf = model.string.custom_definition_confidence
    children = [
        Child(
            "Base definition cost", ".base", "OVERHEAD", (),
            model.string.custom_definition_cost_for(len(udt.name)), conf, False,
        )
    ]
    if custom_string_maxlen(udt) % 4 == 1:
        children.append(
            Child("mod-4 alignment bonus", ".mod4bonus", "OVERHEAD", (),
                  model.string.custom_mod4eq1_definition_bonus, conf, False)
        )
    return children


def resolve_type_at_path(
    data_type: str,
    dimensions: tuple[int, ...],
    path_segments: list[str],
    data_types: dict[str, DataTypeDef],
    model: MemoryModel,
) -> tuple[str, tuple[int, ...]]:
    """Walks path_segments (each like '.Speed' or '[42]') from a starting
    (data_type, dimensions) to find what's actually at that path -- so
    /api/node can then call expand_children on the result."""
    stack: frozenset[str] = frozenset()
    for segment in path_segments:
        if segment.startswith("["):
            if not dimensions:
                raise NotDrillableError(f"{data_type} has no array dimensions to index")
            dimensions = ()  # indexing into an array yields one scalar element
        elif segment.startswith("."):
            member_name = segment[1:]
            if data_type in _THREE_FIELD_PREDEFINED and member_name in ("Status", "PRE", "ACC", "POS"):
                data_type, dimensions = "DINT", ()
                continue
            if data_type not in data_types:
                raise NotDrillableError(f"{data_type} is not a UDT/AOI, can't resolve member {member_name!r}")
            if data_type in stack:
                raise RecursiveUdtError(data_type)
            stack = stack | {data_type}
            udt = data_types[data_type]
            if udt.is_string_family:
                if member_name == "LEN":
                    data_type, dimensions = "DINT", ()
                elif member_name == "DATA":
                    data_member = next((m for m in udt.members if m.name == "DATA"), None)
                    n = data_member.dimension if data_member else 0
                    data_type, dimensions = "SINT", (n,)
                else:
                    raise NotDrillableError(f"{data_type} has no member {member_name!r}")
                continue
            member = next((m for m in udt.members if m.name == member_name), None)
            if member is None:
                raise NotDrillableError(f"{data_type} has no member {member_name!r}")
            if member.is_bit_alias:
                data_type, dimensions = "BIT", ()
            else:
                data_type = member.data_type
                dimensions = (member.dimension,) if member.dimension > 0 else ()
        else:
            raise NotDrillableError(f"unrecognized path segment {segment!r}")
    return data_type, dimensions
