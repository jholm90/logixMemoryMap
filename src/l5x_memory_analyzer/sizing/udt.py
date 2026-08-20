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

    element_bytes, element_confidence = compute_element_size(
        data_type, data_types, model, _stack
    )
    array_confidence = (
        model.array.udt_confidence
        if data_type in data_types
        else model.array.atomic_confidence
    )
    return element_bytes * element_count, weakest(element_confidence, array_confidence)


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
        # Custom string type: LEN + DATA[N], a fixed 2-member convention with
        # no realistic alignment ambiguity -- doesn't inherit the generic
        # UDT alignment taint below. See docs/MEMORY_MODEL.md Custom string type.
        data_member = next((m for m in udt.members if m.name == "DATA"), None)
        n = data_member.dimension if data_member else 0
        return model.string.len_field_bytes + n, model.string.custom_confidence

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
