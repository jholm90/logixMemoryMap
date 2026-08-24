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


def test_predefined_structures_timer_counter_control():
    assert size("TIMER") == (12, "KNOWN")
    assert size("COUNTER") == (12, "KNOWN")
    assert size("CONTROL") == (12, "KNOWN")


def test_predefined_structure_as_udt_member():
    udt = DataTypeDef(
        name="MotorTimers",
        members=[
            Member(name="RunTmr", data_type="TIMER", dimension=0),
            Member(name="FaultCtr", data_type="COUNTER", dimension=0),
        ],
    )
    # 12 (TIMER) + 12 (COUNTER) = 24, UDT alignment is now KNOWN (OQ-ALIGN resolved)
    assert size("MotorTimers", data_types={"MotorTimers": udt}) == (24, "KNOWN")


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
    assert confidence == "KNOWN"  # UDT alignment confirmed KNOWN (OQ-ALIGN)


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
    assert size("Outer", data_types=data_types) == (9, "KNOWN")


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
    # 4-byte LEN + 40-byte DATA = 44 (40 is already a multiple of 8, so no
    # rounding applies either way), and NOT tainted by UDT alignment
    # UNKNOWN. KNOWN: the nearest-8 padding formula below is confirmed
    # exact against 9 real data points, see memory_model.yaml.
    assert size("STRING40", data_types=data_types) == (44, "KNOWN")


def test_custom_string_type_data_member_rounds_to_nearest_8_tie_down():
    # Real-bug fix 2026-08-25: DATA[N] does not just pad up to 4 -- it
    # rounds to the NEAREST multiple of 8, rounding DOWN at the exact tie
    # (remainder 4). maxlen=51 is a real verified data point: pads to 4
    # (52), which lands exactly on the 8-byte tie, so it drops back to 48.
    string51 = DataTypeDef(
        name="STRING51",
        family="StringFamily",
        members=[
            Member(name="LEN", data_type="DINT", dimension=0),
            Member(name="DATA", data_type="SINT", dimension=51),
        ],
    )
    data_types = {"STRING51": string51}
    # 4-byte LEN + 48-byte DATA (rounded DOWN from the 52-byte 4-pad) = 52,
    # NOT the raw 4+51=55 or the naive 4-pad-only 4+52=56.
    assert size("STRING51", data_types=data_types) == (52, "KNOWN")


def test_bool_packing_run_broken_by_non_bool_member():
    # James (2026-08-20): "BOOL/DINT/BOOL will take up 8+32+8 space where
    # DINT/BOOL/BOOL will take up 32+8 space" -- a run of consecutive BOOLs
    # shares one backing SINT, but a non-BOOL member breaks the run and the
    # next BOOL(s) get a fresh backing SINT. Mirrors Logix Designer's own
    # hidden-SINT-per-run XML shape (see parser/datatypes.py), not something
    # this code re-derives independently.
    bool_dint_bool = DataTypeDef(name="BoolDintBool", members=[
        Member(name="_hidden01", data_type="SINT", dimension=0),
        Member(name="FlagA", data_type="BIT", dimension=0),
        Member(name="Count", data_type="DINT", dimension=0),
        Member(name="_hidden02", data_type="SINT", dimension=0),
        Member(name="FlagB", data_type="BIT", dimension=0),
    ])
    dint_bool_bool = DataTypeDef(name="DintBoolBool", members=[
        Member(name="Count", data_type="DINT", dimension=0),
        Member(name="_hidden01", data_type="SINT", dimension=0),
        Member(name="FlagA", data_type="BIT", dimension=0),
        Member(name="FlagB", data_type="BIT", dimension=0),
    ])
    data_types = {"BoolDintBool": bool_dint_bool, "DintBoolBool": dint_bool_bool}

    assert size("BoolDintBool", data_types=data_types) == (6, "KNOWN")  # 8+32+8 bits
    assert size("DintBoolBool", data_types=data_types) == (5, "KNOWN")  # 32+8 bits


def test_self_referential_udt_raises():
    bad = DataTypeDef(
        name="Bad", members=[Member(name="Self", data_type="Bad", dimension=0)]
    )
    with pytest.raises(RecursiveUdtError):
        size("Bad", data_types={"Bad": bad})


# ---------------------------------------------------------------------------
# Array-of-STRING -- 2026-08-26, OQ-STRINGARRAYPAD. A different real
# mechanism from a scalar STRING tag (no -2/tag benefit for array
# elements, but a real additive array_base + per-element surcharge
# instead). Values match the confirmed real formula in memory_model.yaml
# string_array exactly (6/6 and 4/4 real manifest rows verified live).
# ---------------------------------------------------------------------------

def test_builtin_string_array_matches_confirmed_real_formula():
    # total = array_base(6) + (86 + per_element(2)) * n
    assert size("STRING", (1,)) == (6 + 88 * 1, "KNOWN")
    assert size("STRING", (5,)) == (6 + 88 * 5, "KNOWN")
    assert size("STRING", (100,)) == (6 + 88 * 100, "KNOWN")


def test_cam_predefined_array_structure_matches_confirmed_real_formula():
    # OQ-PREDEFINED item 8, wired 2026-08-26: base(8) + per_element(12),
    # confirmed via a 5-point real count sweep (2/5 exact, 3/5 within the
    # same small universal noise band seen throughout this project).
    assert size("CAM", (1,)) == (8 + 12 * 1, "KNOWN")
    assert size("CAM", (50,)) == (8 + 12 * 50, "KNOWN")


def test_custom_string_array_matches_confirmed_real_formula():
    string100 = DataTypeDef(
        name="CStrArrCsTest", family="StringFamily",
        members=[Member(name="LEN", data_type="DINT", dimension=0), Member(name="DATA", data_type="SINT", dimension=100)],
    )
    data_types = {"CStrArrCsTest": string100}
    # scalar element = LEN(4) + DATA(100 rounds DOWN to 96, exact mod-8
    # tie per the nearest-8 padding rule) = 100. total = array_base(12) +
    # (100 + per_element(4)) * n
    assert size("CStrArrCsTest", (1,), data_types=data_types) == (12 + 104 * 1, "FITTED")
    assert size("CStrArrCsTest", (100,), data_types=data_types) == (12 + 104 * 100, "FITTED")
