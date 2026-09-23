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
        #
        # The ELEMENT BLOCK is padded to an 8-byte boundary; the base sits
        # outside it. Confirmed across every captured CAM and
        # CAM_PROFILE point, 15 of 15 at zero residual. It only shows up on
        # CAM, whose 12-byte element leaves 12*N off an 8-byte boundary at
        # odd N -- CAM_PROFILE's 56-byte element is always 8-aligned
        # already, so the padding term is identically zero there and the
        # formula is unchanged for it. That is the cross-check: the same
        # rule explains the one type that needed it and leaves the other
        # exactly where 13 captured points already put it.
        struct = model.predefined_array_structures[data_type]
        element_block = struct.per_element * element_count
        padded = -(-element_block // 8) * 8  # ceil to the next 8-byte boundary
        return struct.base + padded, struct.confidence

    if data_type == "STRING":
        # Array-of-builtin-STRING: a DIFFERENT real mechanism from a
        # scalar STRING tag (OQ-STRINGARRAYPAD, confirmed) --
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
        # Only the one-time array_base is uncertain here, and only for a
        # type name whose length was never measured -- see
        # StringArrayModel.custom_base_for. The element size and the
        # +4/element surcharge are both KNOWN, so an array of a custom
        # string type with a measured name length is KNOWN end to end.
        sa = model.string_array
        array_base, base_confidence = sa.custom_base_for(len(data_type))
        total = array_base + (element_bytes + sa.custom_per_element) * element_count
        return total, weakest(element_confidence, base_confidence)
    if data_type in data_types and data_types[data_type].is_aoi:
        # Array-of-AOI-instances: a real, DIFFERENT formula from plain
        # array-of-UDT below -- confirmed, see memory_model.yaml
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
            # EnableIn/EnableOut share these words even though bool_count
            # excludes them -- see memory_model.yaml
            # aoi_array.enable_bits_packed_with_bools (36 files, 12 bool counts
            # across three 32-bit boundaries, 12/12).
            packed_bits = bool_count + model.aoi_array.enable_bits_packed_with_bools
            words = -(-packed_bits // word_size)  # ceil
            per_instance -= bool_count * 4
            per_instance += model.aoi_array.bool_word_extra * max(0, words - 1)
        # The whole block is padded up to an 8-byte boundary, not each
        # instance -- see memory_model.yaml aoi_array.block_alignment_bytes
        # (OQ-AOIBOOLPACK-PAIRING, 48/48 captured sweep families).
        align = model.aoi_array.block_alignment_bytes
        block = per_instance * element_count
        block = -(-block // align) * align
        # The array TAG's own flat cost, on top of the aligned block -- see
        # memory_model.yaml aoi_array.array_tag_flat_bytes (24 controlled
        # def_only-versus-array measurements).
        block += model.aoi_array.array_tag_flat_bytes
        return block, weakest(element_confidence, model.aoi_array.confidence)
    if data_type in data_types:
        # Array-of-UDT: each element rounds up to a 4-byte boundary --
        # confirmed (OQ-ARRAYPACK/OQ-UDTARRAYALIGN resolved,
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
        # Custom string type: LEN + DATA[N]. Real-bug fix: the
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
    members) was a real bug caught: an all-BOOL UDT computed
    declared_member_count=0 (its only non-bit-alias member IS the hidden
    one), silently undercounting every UDT with any BOOL members.

    bool_run_bonus applies ONCE PER hidden backing SINT, not once per UDT
    regardless of count -- also caught: a BOOL,DINT,BOOL shape
    (a non-BOOL member breaking the run, per OQ-ALIGN, needs two separate
    hidden SINTs) real-measured at base+2*bonus, not base+1*bonus."""
    udt = data_types[name]
    declared_member_count = sum(1 for m in udt.members if not m.hidden)
    bool_run_count = sum(1 for m in udt.members if m.hidden)
    return (
        model.udt_definition.bytes_for(
            name, declared_member_count, bool_run_count,
            [m.name for m in udt.members if not m.hidden]),
        model.udt_definition.confidence,
    )


def compute_aoi_definition_cost(
    name: str, data_types: dict[str, DataTypeDef], model: MemoryModel
) -> tuple[int, str]:
    """One-time cost of an AOI *definition* itself (its own Parameters/
    LocalTags declaration) -- separate from and additive with any tag
    instance's own tag_overhead + member size, the same relationship
    compute_udt_definition_cost has to a plain UDT.

    One itemised form, derived from 124 captured def-only files:

        base
        + per_member_descriptor_bytes per declared member
        + that member's OWN DATA BYTES
        + bool_word_bytes per 32-bit word the declared scalar BOOLs occupy
        + the members' names, pooled and 8-aligned
        + name_length_bytes(the AOI's own type name)

    See memory_model.yaml aoi_definition for the derivation, for what each of
    the four terms it replaces was really measuring, and for the unexplained
    8-byte residual recorded in OQ-AOIDEFSHAPE. Members exclude EnableIn/
    EnableOut (always present, not declared) and InOut parameters, which
    parse_aoi_definitions already drops as reference rather than storage.
    """
    aoi = data_types[name]
    aoi_def = model.aoi_definition
    member_names: list[str] = []
    data_bytes = 0
    bool_count = 0
    member_confidences: list[str] = []
    for m in aoi.members:
        if m.name in ("EnableIn", "EnableOut"):
            continue
        member_names.append(m.name)
        if m.data_type == "BOOL" and not m.dimension:
            # A scalar BOOL has no data bytes of its own: it is a bit in the
            # packed words charged below.
            bool_count += 1
            continue
        # Every other declared member costs its own data space on top of the
        # descriptor. Measured for arrays from the 27-file
        # aoi_arraylocal_* sweep (DINT dim 10/50/100/250/500/1000 reading
        # 41/201/401/1001/2001/4001, i.e. 4 bytes per element with the
        # project-wide +1 residual; SINT 1.0, REAL 4.0 per element at dim 50;
        # additive across 1/2/3 array members at 200/392/592) and
        # definition-side only -- the _1_instance twin of every file carries
        # the same deficit, so an instance does not pay it twice. The scalar
        # case is what supersedes aoi_member_type_extra: REAL 0, TIMER 8 and
        # COUNTER 8 are exactly that type's size minus the 4 bytes of DINT
        # that the old flat 20/item rate had baked in (STRING lands 2 short of
        # its old 84, MOTION_INSTRUCTION 4 short of its 12 -- see
        # OQ-AOIDEFSHAPE).
        #
        # compute_array_size, not element_size x dimension: CAM/CAM_PROFILE
        # are predefined ARRAY structures with their own base + per_element
        # shape and no scalar element size at all, and real programs declare
        # CAM_PROFILE array LocalTags (10 of them across the 16 real exports).
        #
        # A BOOL ARRAY is deliberately left unpriced rather than approximated,
        # see OQ-AOIARRAYLOCALTAG: a BOOL[50] measured -13 where neither the
        # 7-byte packed size nor an 8-byte two-word rounding fits.
        if m.data_type == "BOOL":
            continue
        try:
            if m.dimension:
                member_bytes, member_conf = compute_array_size(
                    m.data_type, (m.dimension,), data_types, model)
            else:
                member_bytes, member_conf = compute_element_size(
                    m.data_type, data_types, model)
        except UnknownDataTypeError:
            # A declared member whose type this model cannot size at all
            # leaves its data space unpriced rather than aborting the whole
            # report -- the coverage audit is what surfaces it.
            continue
        data_bytes += member_bytes
        member_confidences.append(member_conf)

    total = aoi_def.aligned_total(
        aoi_def.base
        + aoi_def.per_member_descriptor_bytes * len(member_names)
        + data_bytes
        + aoi_def.bool_word_cost(bool_count)
        + aoi_def.member_name_pool_bytes(member_names)
        + aoi_def.name_length_bytes(name)
    )
    confidence = weakest(
        aoi_def.confidence,
        aoi_def.name_length_bucket_confidence,
        *member_confidences,
    )
    return total, confidence


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
