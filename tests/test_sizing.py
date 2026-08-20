"""Hand-calculated sizing checks against docs/MEMORY_MODEL.md's current formulas."""

import pytest

from l5x_memory_analyzer.parser.datatypes import DataTypeDef, Member
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.udt import (
    RecursiveUdtError,
    UnknownDataTypeError,
    compute_array_size,
)

MODEL = load_memory_model()


def size(data_type, dimensions=(), data_types=None):
    return compute_array_size(data_type, dimensions, data_types or {}, MODEL)


def test_atomic_scalar():
    assert size("DINT") == (4, "KNOWN")
    assert size("SINT") == (1, "KNOWN")
    assert size("LINT") == (8, "KNOWN")


def test_atomic_array():
    assert size("DINT", (10,)) == (40, "KNOWN")


def test_bool_standalone_scalar_is_4_bytes_not_bit_packed():
    assert size("BOOL") == (4, "ASSUMED")


def test_bool_array_bit_packs_32_per_dint():
    assert size("BOOL", (100,)) == (16, "ASSUMED")  # ceil(100/32)=4 words * 4 bytes
    assert size("BOOL", (32,)) == (4, "ASSUMED")  # exact word boundary
    assert size("BOOL", (33,)) == (8, "ASSUMED")  # rolls into a second word


def test_builtin_string_default():
    assert size("STRING") == (86, "KNOWN")  # 4-byte LEN + 82-byte DATA


def test_unknown_type_raises():
    with pytest.raises(UnknownDataTypeError):
        size("NotARealType")


def test_udt_mixed_bool_dint_string_with_bit_packing():
    # Mirrors what Logix Designer itself emits for a UDT with 2 BOOL members:
    # one hidden backing SINT + two visible BIT aliases into it.
    udt = DataTypeDef(
        name="MixedUdt",
        members=[
            Member(name="Count", data_type="DINT", dimension=0),
            Member(name="ZZZZZZZZZZBoolMember01", data_type="SINT", dimension=0),
            Member(name="FlagA", data_type="BIT", dimension=0),
            Member(name="FlagB", data_type="BIT", dimension=0),
            Member(name="Label", data_type="STRING", dimension=0),
        ],
    )
    data_types = {"MixedUdt": udt}
    # 4 (DINT) + 1 (backing SINT) + 0 (FlagA alias) + 0 (FlagB alias) + 86 (STRING) = 91
    bytes_, confidence = size("MixedUdt", data_types=data_types)
    assert bytes_ == 91
    assert confidence == "UNKNOWN"  # tainted by the untested UDT alignment assumption


def test_udt_nested_two_levels():
    inner = DataTypeDef(
        name="Inner",
        members=[
            Member(name="A", data_type="DINT", dimension=0),
            Member(name="B", data_type="SINT", dimension=0),
        ],
    )  # 4 + 1 = 5 bytes
    outer = DataTypeDef(
        name="Outer",
        members=[
            Member(name="Header", data_type="DINT", dimension=0),  # 4
            Member(name="Payload", data_type="Inner", dimension=0),  # 5
        ],
    )
    data_types = {"Inner": inner, "Outer": outer}
    assert size("Outer", data_types=data_types) == (9, "UNKNOWN")


def test_udt_array_of_udt():
    inner = DataTypeDef(
        name="Inner",
        members=[Member(name="A", data_type="DINT", dimension=0)],
    )  # 4 bytes
    data_types = {"Inner": inner}
    bytes_, confidence = size("Inner", (10,), data_types=data_types)
    assert bytes_ == 40
    assert confidence == "UNKNOWN"  # OQ-ARRAYPACK is UNKNOWN and outranks the element's tier


def test_custom_string_type_uses_len_plus_data_not_generic_udt_path():
    string40 = DataTypeDef(
        name="STRING40",
        family="StringFamily",
        members=[
            Member(name="LEN", data_type="DINT", dimension=0),
            Member(name="DATA", data_type="SINT", dimension=40),
        ],
    )
    data_types = {"STRING40": string40}
    # 4-byte LEN + 40-byte DATA = 44, and NOT tainted by UDT alignment UNKNOWN
    assert size("STRING40", data_types=data_types) == (44, "KNOWN")


def test_self_referential_udt_raises():
    bad = DataTypeDef(
        name="Bad", members=[Member(name="Self", data_type="Bad", dimension=0)]
    )
    with pytest.raises(RecursiveUdtError):
        size("Bad", data_types={"Bad": bad})
