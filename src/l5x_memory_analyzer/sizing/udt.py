"""Recursive byte-size calculator for atomic types, UDTs, and arrays.

Formulas and confidence tags come straight from docs/MEMORY_MODEL.md via
constants.py -- see that file for the reasoning behind each one.
"""

from __future__ import annotations

import math

from l5x_memory_analyzer.parser.datatypes import DataTypeDef
from l5x_memory_analyzer.sizing.confidence import weakest
from l5x_memory_analyzer.sizing.constants import MemoryModel


class UnknownDataTypeError(ValueError):
    """DataType name is neither an atomic type, BOOL/STRING, nor a known UDT."""


class RecursiveUdtError(ValueError):
    """A UDT references itself, directly or transitively (not valid Logix)."""


def compute_element_size(
    data_type: str,
    data_types: dict[str, DataTypeDef],
    model: MemoryModel,
    _stack: frozenset[str] = frozenset(),
) -> tuple[int, str]:
    """Size of one scalar (non-array) instance of data_type."""
    if data_type == "BIT":
        return 0, "KNOWN"  # UDT bit-alias member; storage already counted via its backing SINT
    if data_type in model.atomic_types:
        atomic = model.atomic_types[data_type]
        return atomic.bytes, atomic.confidence
    if data_type in model.predefined_structures:
        struct = model.predefined_structures[data_type]
        return struct.bytes, struct.confidence
    if data_type == "BOOL":
        return model.bool.standalone_tag_bytes, model.bool.standalone_confidence
    if data_type == "STRING":
        return (
            model.string.len_field_bytes + model.string.default_data_bytes,
            model.string.confidence,
        )
    if data_type in data_types:
        return compute_udt_size(data_type, data_types, model, _stack)
    raise UnknownDataTypeError(data_type)


def compute_array_size(
    data_type: str,
    dimensions: tuple[int, ...],
    data_types: dict[str, DataTypeDef],
    model: MemoryModel,
    _stack: frozenset[str] = frozenset(),
) -> tuple[int, str]:
    """Size of data_type given its array dimensions (empty tuple = scalar)."""
    if not dimensions:
        return compute_element_size(data_type, data_types, model, _stack)

    element_count = math.prod(dimensions)

    if data_type == "BOOL":
        # See docs/MEMORY_MODEL.md Array sizing -- OQ-BOOLARRAY.
        words = -(-element_count // model.bool.array_bits_per_packed_word)  # ceil
        return words * model.bool.array_packed_word_bytes, model.bool.array_confidence

    if data_type in model.predefined_array_structures:
        # Predefined structures whose real cost is base + per_element*N
        # rather than a flat scalar -- CAM_PROFILE etc, always used as an
        # array in real Logix. See memory_model.yaml predefined_array_
        # structures for the derivation.
        struct = model.predefined_array_structures[data_type]
        return struct.base + struct.per_element * element_count, struct.confidence

    if data_type == "STRING":
        # Array-of-builtin-STRING: a DIFFERENT real mechanism from a
        # scalar STRING tag (OQ-STRINGARRAYPAD, confirmed 2026-08-26) --
        # array elements do NOT get the scalar tag's -2/tag benefit, and
        # instead carry their own flat one-time array_base PLUS a real
        # per-element surcharge on top of the ordinary N x (LEN+DATA)
        # size. See memory_model.yaml string_array for the derivation
        # (6/6 real count points exact, zero residual).
        element_bytes, element_confidence = compute_element_size(data_type, data_types, model, _stack)
        sa = model.string_array
        total = sa.builtin_array_base + (element_bytes + sa.builtin_per_element) * element_count
        return total, weakest(element_confidence, sa.builtin_confidence)

    element_bytes, element_confidence = compute_element_size(
        data_type, data_types, model, _stack
    )
    if data_type in data_types and data_types[data_type].is_string_family:
        # Array-of-custom-string: same real "different from scalar"
        # mechanism as builtin STRING above, different confirmed rate
        # (4/element vs 2/element) -- see memory_model.yaml string_array.
        # custom_array_base is FITTED, not KNOWN: real data shows it's
        # type-name-length-dependent (an already-separately-flagged, still
        # -open effect on the custom-string scalar definition cost too),
        # so this is confirmed exact for the specific type name it was
        # fit against, a good approximation for others.
        sa = model.string_array
        total = sa.custom_array_base + (element_bytes + sa.custom_per_element) * element_count
        return total, weakest(element_confidence, sa.custom_confidence)
    if data_type in data_types and data_types[data_type].is_aoi:
        # Array-of-AOI-instances: a real, DIFFERENT formula from plain
        # array-of-UDT below -- confirmed 2026-08-26, see memory_model.yaml
        # aoi_array for the full derivation. Per-instance cost is the
        # scalar instance size minus a flat discount, minus 4 bytes per
        # declared BOOL member (EnableIn/EnableOut excluded -- they aren't
        # part of the declared member list this counts), with a further
        # +4 correction each time the BOOL member count crosses a
        # 32-member packed-word boundary.
        bool_count = sum(
            1 for m in data_types[data_type].members
            if m.data_type == "BOOL" and m.name not in ("EnableIn", "EnableOut")
        )
        per_instance = element_bytes - model.aoi_array.flat_discount
        if bool_count > 0:
            word_size = model.aoi_array.bool_word_size
            words = -(-bool_count // word_size)  # ceil
            per_instance -= bool_count * 4
            per_instance += model.aoi_array.bool_word_extra * max(0, words - 1)
        return per_instance * element_count, weakest(element_confidence, model.aoi_array.confidence)
    if data_type in data_types:
        # Array-of-UDT: each element rounds up to a 4-byte boundary --
        # confirmed 2026-08-24 (OQ-ARRAYPACK/OQ-UDTARRAYALIGN resolved,
        # see RESOLVED_QUESTIONS.md) against real data for a 3-byte-tight
        # UDT array (arraypack_odd3b_n*, n=10/100/1000/5000 all landed on
        # exactly the same residual as the universal small-baseline noise
        # once each element is rounded 3->4 bytes -- zero residual growth
        # left once this rounding is applied) and confirmed as a genuine
        # non-effect for an already-4-byte-aligned UDT (udtarrayalign_
        # tight8b_n*, 8 bytes/element, flat +4 residual at every count,
        # no growth -- rounding an already-aligned size is a no-op, so
        # this doesn't contradict that earlier "no per-element padding"
        # finding, it sharpens it: no padding beyond the 4-byte boundary
        # itself). Does NOT apply to atomic-type arrays (untested at this
        # rounding question, atomic array sizing stays dimension*element_size
        # unchanged).
        element_bytes = -(-element_bytes // 4) * 4
        array_confidence = model.array.udt_confidence
    else:
        array_confidence = model.array.atomic_confidence
    return element_bytes * element_count, weakest(element_confidence, array_confidence)


def custom_string_maxlen(udt: DataTypeDef) -> int:
    """The declared DATA[N] dimension of a StringFamily type -- shared by
    compute_udt_size and report.py's per-tag/per-definition correction
    logic, both of which need the same maxlen mod 4 to pick the right
    real-data-confirmed bucket (see memory_model.yaml's string: block)."""
    data_member = next((m for m in udt.members if m.name == "DATA"), None)
    return data_member.dimension if data_member else 0


def compute_udt_size(
    name: str,
    data_types: dict[str, DataTypeDef],
    model: MemoryModel,
    _stack: frozenset[str] = frozenset(),
) -> tuple[int, str]:
    if name in _stack:
        raise RecursiveUdtError(name)
    udt = data_types[name]

    if udt.is_string_family:
        # Custom string type: LEN + DATA[N]. Real-bug fix 2026-08-25: the
        # DATA member (SINT[N]) does NOT round up to a plain 4-byte
        # boundary -- it rounds to the NEAREST multiple of 8, rounding
        # DOWN at the exact tie (remainder 4). Confirmed exact (0 residual)
        # against 9 real maxlen points (49-1000) spanning every mod-4 and
        # mod-8 remainder: pad to 4 first (n_padded), then if that lands
        # exactly at the midpoint (n_padded % 8 == 4), drop back by 4 to
        # the next-lower multiple of 8. See memory_model.yaml's
        # custom_data_padding_multiple comment for the full derivation.
        n = custom_string_maxlen(udt)
        pad = model.string.custom_data_padding_multiple
        n_padded = -(-n // pad) * pad if pad else n
        if n_padded % (2 * pad) == pad:
            n_padded -= pad
        confidence = weakest(model.string.custom_confidence, model.string.custom_data_padding_confidence)
        return model.string.len_field_bytes + n_padded, confidence

    stack = _stack | {name}

    total = 0
    confidence = "KNOWN"
    for member in udt.members:
        if member.is_bit_alias:
            continue
        dims = (member.dimension,) if member.dimension > 0 else ()
        size, member_confidence = compute_array_size(
            member.data_type, dims, data_types, model, stack
        )
        total += size
        confidence = weakest(confidence, member_confidence)

    confidence = weakest(confidence, model.udt.alignment_confidence)
    return total, confidence


def compute_udt_definition_cost(
    name: str, data_types: dict[str, DataTypeDef], model: MemoryModel
) -> tuple[int, str]:
    """One-time cost of the DataType *definition* itself (member list +
    type name), separate from and additive with any instance's tag_overhead
    + tight-packed member size. See memory_model.yaml udt_definition for the
    formula and its confirmed-vs-flagged caveats. declared_member_count
    counts members the way a user would (a BOOL run is still N members, not
    N+1) -- excludes only the HIDDEN backing SINT, not the visible BIT-alias
    members it backs, each of which is one real declared BOOL member.
    Getting this backwards (excluding bit-aliases instead of hidden
    members) was a real bug caught 2026-08-22: an all-BOOL UDT computed
    declared_member_count=0 (its only non-bit-alias member IS the hidden
    one), silently undercounting every UDT with any BOOL members.

    bool_run_bonus applies ONCE PER hidden backing SINT, not once per UDT
    regardless of count -- also caught 2026-08-22: a BOOL,DINT,BOOL shape
    (a non-BOOL member breaking the run, per OQ-ALIGN, needs two separate
    hidden SINTs) real-measured at base+2*bonus, not base+1*bonus."""
    udt = data_types[name]
    declared_member_count = sum(1 for m in udt.members if not m.hidden)
    bool_run_count = sum(1 for m in udt.members if m.hidden)
    return (
        model.udt_definition.bytes_for(name, declared_member_count, bool_run_count),
        model.udt_definition.confidence,
    )


def compute_aoi_definition_cost(
    name: str, data_types: dict[str, DataTypeDef], model: MemoryModel
) -> tuple[int, str]:
    """One-time cost of an AOI *definition* itself (its own Parameters/
    LocalTags declaration) -- separate from and additive with any tag
    instance's own tag_overhead + member size, same relationship
    compute_udt_definition_cost has to a plain UDT. See memory_model.yaml
    aoi_definition for the formula's derivation (per-type rate for a
    single-type AOI def, flat rate for a mixed-type one) and its FITTED
    (not KNOWN) confidence.

    type_counts excludes EnableIn/EnableOut (always present, not something
    a user declares) -- parse_aoi_definitions already excludes InOut params
    from `members` entirely (reference, not storage), so every remaining
    member here is a real declared Input/Output Parameter or LocalTag,
    grouped by its own data_type so bytes_for can apply a per-type rate.
    """
    aoi = data_types[name]
    type_counts: dict[str, int] = {}
    for m in aoi.members:
        if m.name in ("EnableIn", "EnableOut"):
            continue
        type_counts[m.data_type] = type_counts.get(m.data_type, 0) + 1
    confidence = weakest(model.aoi_definition.confidence, model.aoi_definition.name_length_bucket_confidence)
    return model.aoi_definition.bytes_for(type_counts, name), confidence


def referenced_data_type_names(
    data_type: str, data_types: dict[str, DataTypeDef], _seen: set[str] | None = None
) -> set[str]:
    """Transitive closure of every UDT name reachable from data_type (itself
    included if it's a UDT) -- a type only ever used as a nested member,
    never as a top-level tag's own DataType, still needs its own definition
    cost counted once."""
    seen = _seen if _seen is not None else set()
    if data_type not in data_types or data_type in seen:
        return seen
    seen.add(data_type)
    udt = data_types[data_type]
    if udt.is_string_family:
        return seen
    for member in udt.members:
        if member.is_bit_alias:
            continue
        referenced_data_type_names(member.data_type, data_types, seen)
    return seen
