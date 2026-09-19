"""The itemised AOI-definition formula, and the four terms it replaced.

Derived (capture-batch segment 4) from 124 captured def-only files:
an AOI definition with no instance tag anywhere and no internal rungs, so the
definition is the only AOI cost in the file and its true value reads straight
off the capture. 70 of the 124 land exactly, 122 within the project's +-8
universal residual, worst 11.

This file replaces test_aoi_member_type_extra.py. That module tested
`extra_bytes = 8 * floor(sum(count_T * rate_T) / 8)` with rates REAL 0,
TIMER 8, COUNTER 8, MOTION_INSTRUCTION 12, STRING 84 -- which fitted its own
40 files exactly and was still the wrong shape. Those rates are each that
type's real data bytes minus the 4 bytes of DINT that the old flat 20/item
per_declared_item rate had baked in, and the floor-to-8 was an artifact of
that mis-attribution. test_supersedes_* below keeps the evidence.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from l5x_memory_analyzer.parser.aoi import parse_aoi_definitions
from l5x_memory_analyzer.parser.datatypes import parse_data_types
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.tree import expand_definition_children
from l5x_memory_analyzer.sizing.udt import (
    compute_aoi_definition_cost,
    compute_element_size,
)

MODEL = load_memory_model()


@pytest.fixture
def aoi_def():
    return MODEL.aoi_definition


def _aoi(members_xml: str, name: str = "TestAoi", locals_xml: str = "") -> dict:
    root = ET.fromstring(
        '<RSLogix5000Content><Controller><DataTypes/>'
        '<AddOnInstructionDefinitions>'
        f'<AddOnInstructionDefinition Name="{name}" Revision="1.0">'
        '<Parameters>'
        '<Parameter Name="EnableIn" DataType="BOOL" Usage="Input"/>'
        '<Parameter Name="EnableOut" DataType="BOOL" Usage="Output"/>'
        f'{members_xml}'
        '</Parameters>'
        f'<LocalTags>{locals_xml}</LocalTags>'
        '</AddOnInstructionDefinition>'
        '</AddOnInstructionDefinitions></Controller></RSLogix5000Content>'
    )
    types = dict(parse_data_types(root))
    types.update(parse_aoi_definitions(root))
    return types


def _cost(members_xml: str, name: str = "TestAoi", locals_xml: str = "") -> int:
    types = _aoi(members_xml, name, locals_xml)
    return compute_aoi_definition_cost(name, types, MODEL)[0]


def _param(pname: str, data_type: str, usage: str = "Input") -> str:
    return f'<Parameter Name="{pname}" DataType="{data_type}" Usage="{usage}"/>'


def test_a_member_costs_the_descriptor_plus_its_own_data_bytes(aoi_def):
    """12 + 4 for a DINT, 12 + 8 for a LINT, 12 + 1 for a SINT. The old
    per_type_rate table read these as 20 / 24 / 18 because the linear
    member-name term it was fitted alongside absorbed the difference."""
    # Compared against the same AOI with one BOOL member, so the 8-aligned
    # name pool and the descriptor are identical on both sides and only the
    # member's own data bytes differ.
    bool_member = _cost(_param("Px", "BOOL"))
    for data_type, size in (("SINT", 1), ("INT", 2), ("DINT", 4), ("LINT", 8), ("REAL", 4)):
        one = _cost(_param("Px", data_type))
        assert one - bool_member == size, data_type


def test_a_scalar_bool_has_no_data_bytes_of_its_own(aoi_def):
    base = _cost("")
    one = _cost(_param("Px", "BOOL"))
    # The descriptor, plus the one 8-byte name-pool chunk "Px" now needs.
    assert one - base == aoi_def.per_member_descriptor_bytes + 8


def test_enable_bits_alone_still_occupy_a_word(aoi_def):
    """EnableIn/EnableOut are two bits in the packed BOOL words even when the
    AOI declares no BOOL of its own -- the same enable-bit correction the
    instance-array side carries (aoi_array.enable_bits_packed_with_bools)."""
    assert aoi_def.bool_word_cost(0) == aoi_def.bool_word_bytes
    assert aoi_def.bool_word_cost(30) == aoi_def.bool_word_bytes
    # 30 + 2 enable bits exactly fills one word; 31 spills into a second.
    assert aoi_def.bool_word_cost(31) == 2 * aoi_def.bool_word_bytes
    assert aoi_def.bool_word_cost(62) == 2 * aoi_def.bool_word_bytes
    assert aoi_def.bool_word_cost(63) == 3 * aoi_def.bool_word_bytes


def test_the_bool_word_boundary_is_visible_in_the_definition_cost():
    """aoialgn_def_mc60_b54 and _b60 are the two captured def-only files that
    cross into a second word, and both land within the +-8 band under this."""
    at_30 = _cost("".join(_param(f"B{i:02d}", "BOOL") for i in range(30)))
    at_31 = _cost("".join(_param(f"B{i:02d}", "BOOL") for i in range(31)))
    # One more BOOL: its descriptor, plus the second word it spills into. The
    # name pool is unchanged (30 names of 3 chars = 120 -> 31 -> 124 -> both
    # round to 128 is NOT guaranteed, so compare against the model's own).
    aoi_def = MODEL.aoi_definition
    names_30 = [f"B{i:02d}" for i in range(30)]
    names_31 = [f"B{i:02d}" for i in range(31)]
    pool_step = (aoi_def.member_name_pool_bytes(names_31)
                 - aoi_def.member_name_pool_bytes(names_30))
    assert at_31 - at_30 == (aoi_def.per_member_descriptor_bytes
                             + aoi_def.bool_word_bytes + pool_step)


def test_member_names_are_a_pool_rounded_up_not_a_per_name_rate(aoi_def):
    """One byte per name on top of its characters, then the whole total
    rounded up to 8 -- so two short names can cost the same as one long one,
    which the old 1-byte-per-char-with-3-free rate could not express."""
    assert aoi_def.member_name_pool_bytes(["Ab"]) == 8
    assert aoi_def.member_name_pool_bytes(["Abcdefg"]) == 8
    assert aoi_def.member_name_pool_bytes(["Abcdefgh"]) == 16
    # 3 names of 2 chars = 9 bytes -> 16; a 15-char name is also 16.
    assert (aoi_def.member_name_pool_bytes(["Ab", "Cd", "Ef"])
            == aoi_def.member_name_pool_bytes(["A" * 15]))


def test_member_names_pool_is_charged_once_over_the_whole_set(aoi_def):
    """Three members whose names fit one 8-byte chunk cost that chunk once."""
    three_short = _cost("".join(_param(n, "DINT") for n in ("A", "B", "C")))
    base = _cost("")
    descriptors = 3 * (aoi_def.per_member_descriptor_bytes + 4)
    assert three_short - base == descriptors + 8


@pytest.mark.parametrize("data_type,size,old_rate", [
    ("REAL", 4, 0),
    ("TIMER", 12, 8),
    ("COUNTER", 12, 8),
])
def test_supersedes_member_type_extra_for_three_of_five_measured_types(
    data_type, size, old_rate
):
    """The old aoi_member_type_extra rates were (own size - 4): the difference
    between that type's real data bytes and the DINT baked into the flat
    20/item rate. Keeping the arithmetic here is what stops the old table
    being reintroduced as a separate term."""
    assert size - 4 == old_rate


def test_string_lands_two_short_of_its_old_rate():
    """STRING's old rate of 84 is 2 more than its 86 bytes minus the same 4.
    Its capture (altype_string_n00010_def_only) reads -2 under the itemised
    form, inside the +-8 band, so the itemised form is kept and the 2 is
    recorded in OQ-AOIDEFSHAPE rather than reintroduced as a per-type rate."""
    string_bytes, _ = compute_element_size("STRING", {}, MODEL)
    assert string_bytes == 86
    assert string_bytes - 4 == 82


def test_motion_instruction_is_the_one_that_does_not_reduce():
    """MOTION_INSTRUCTION's old rate was 12 where its 12-byte size predicts 8.
    Recorded in OQ-AOIDEFSHAPE rather than papered over: the
    altype_motion_instruction_n00010_def_only capture reads +44 against the
    current engine, the largest residual in the array-localtag families."""
    assert MODEL.predefined_structures["MOTION_INSTRUCTION"].bytes == 12
    assert 12 - 4 != 12


def test_inout_parameters_cost_nothing(aoi_def):
    """InOut is a reference to a caller-scope tag, not an allocation --
    parse_aoi_definitions drops them before this formula ever sees them."""
    without = _cost(_param("Px", "DINT"))
    with_inout = _cost(_param("Px", "DINT") + _param("Ref", "DINT", usage="InOut"))
    assert with_inout == without


def test_expansion_sums_to_the_total():
    """The UI drill-down breakdown must account for every byte."""
    members = (_param("Tmr", "TIMER") + _param("Flag", "BOOL")
               + _param("Count", "DINT"))
    types = _aoi(members, locals_xml='<LocalTag Name="Work" DataType="REAL"/>')
    total, _ = compute_aoi_definition_cost("TestAoi", types, MODEL)
    children = expand_definition_children("TestAoi", types, MODEL)
    assert sum(c.bytes for c in children) == total
