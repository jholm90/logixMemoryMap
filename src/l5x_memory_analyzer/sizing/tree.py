"""Lazy, one-level-at-a-time recursive drill-down for the UI treemap.

James (2026-08-20): infinite depth, no masking a large array just because
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
from l5x_memory_analyzer.sizing.constants import MemoryModel
from l5x_memory_analyzer.sizing.udt import (
    RecursiveUdtError,
    compute_array_size,
    compute_element_size,
)


class NotDrillableError(ValueError):
    """The resolved node is a true leaf -- no further children exist."""


@dataclass(frozen=True)
class Child:
    name: str  # display label, e.g. "Speed" or "[42]"
    segment: str  # token to append to the path for a further drill, e.g. ".Speed" or "[42]"
    data_type: str
    dimensions: tuple[int, ...]
    bytes: float  # float for packed-BOOL-array elements' proportional share; int otherwise
    basis: str
    has_children: bool


def has_children(
    data_type: str, dimensions: tuple[int, ...], data_types: dict[str, DataTypeDef], model: MemoryModel
) -> bool:
    if dimensions:
        return math.prod(dimensions) > 0
    if data_type in data_types:
        return True  # UDT/AOI (merged) and custom string types all expose at least LEN+DATA or members
    if data_type in model.predefined_structures:
        return True  # TIMER/COUNTER/CONTROL expose their 3 documented fields
    if data_type == "STRING":
        return True  # built-in STRING: LEN + DATA
    return False  # plain atomic scalar (SINT/INT/DINT/LINT/REAL) or standalone BOOL -- true leaf


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
    if data_type in model.predefined_structures:
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
            children.append(Child(member.name, f".{member.name}", "BIT", (), 0, "KNOWN", False))
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
            if data_type in model.predefined_structures and member_name in ("Status", "PRE", "ACC", "POS"):
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
