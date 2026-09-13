"""Non-atomic declared members cost more than the flat per-item rate.

OQ-AOIDEFITEMIZE, wired 2026-09-13 from aoilt_swap_{timer,counter,motion,real,
string}_n01..n08 -- 40 files, each swapping k of 8 DINT LocalTags for another
type with the MEMBER COUNT HELD AT 8, so the per-type rate separates from the
per-item rate. One form fits all 40 with zero residual:

    extra = 8 * floor(sum(count_T * rate_T) / 8)

The FLOOR is the half that two data points could never have shown, and these
tests exist mainly to pin it: TIMER and COUNTER are 8/member and land on the
boundary so they look perfectly linear, while MOTION_INSTRUCTION (12) and
STRING (84) alternate as odd counts lose the remainder. Fitting a slope to
either from two points gives 12 and 84 and is wrong at every odd count.
"""

from __future__ import annotations

import math

import pytest

from l5x_memory_analyzer.sizing.constants import load_memory_model


@pytest.fixture
def aoi_def():
    return load_memory_model().aoi_definition


@pytest.mark.parametrize("type_name,rate", [
    ("TIMER", 8), ("COUNTER", 8), ("MOTION_INSTRUCTION", 12), ("STRING", 84), ("REAL", 0),
])
def test_measured_rates(aoi_def, type_name, rate):
    assert aoi_def.member_type_extra.get(type_name) == rate


@pytest.mark.parametrize("type_name", ["TIMER", "COUNTER", "MOTION_INSTRUCTION", "STRING"])
def test_the_total_is_floored_not_rounded(aoi_def, type_name):
    """Every one of the 8 measured counts, against the closed form."""
    rate = aoi_def.member_type_extra[type_name]
    align = aoi_def.member_type_extra_alignment
    for k in range(1, 9):
        assert aoi_def.member_type_extra_bytes({type_name: k}) == align * math.floor(k * rate / align)


def test_odd_counts_lose_the_remainder_for_a_non_aligned_rate(aoi_def):
    """MOTION_INSTRUCTION at 12/member: two members cost 24, one costs 8 not 12.
    This is the exact behaviour a linear fit would have got wrong."""
    assert aoi_def.member_type_extra_bytes({"MOTION_INSTRUCTION": 1}) == 8
    assert aoi_def.member_type_extra_bytes({"MOTION_INSTRUCTION": 2}) == 24
    assert aoi_def.member_type_extra_bytes({"MOTION_INSTRUCTION": 3}) == 32


def test_an_aligned_rate_looks_linear(aoi_def):
    """TIMER at 8/member never loses a remainder, which is why the two-point
    reading happened to be right for it and wrong for the others."""
    for k in range(1, 9):
        assert aoi_def.member_type_extra_bytes({"TIMER": k}) == 8 * k


def test_atomic_types_in_per_type_rate_are_not_charged_twice(aoi_def):
    """Anything with its own per_type_rate entry must be absent here, or the
    cost lands twice. REAL is the one exception and only because it is zero."""
    for type_name in aoi_def.per_type_rate:
        extra = aoi_def.member_type_extra.get(type_name, 0)
        assert extra == 0, f"{type_name} is in both tables with a nonzero extra"


def test_unknown_types_cost_nothing_extra(aoi_def):
    assert aoi_def.member_type_extra_bytes({"SOME_UNMEASURED_UDT": 50}) == 0


def test_expansion_still_sums_to_the_total():
    """The drill-down has to add up. The extra is floored over the WHOLE member
    set, so it cannot be divided among the per-member rows -- it is its own line
    for that reason, and this pins that the parts still equal the whole."""
    from l5x_memory_analyzer.parser.datatypes import DataTypeDef, Member
    from l5x_memory_analyzer.sizing.tree import _expand_aoi_definition
    from l5x_memory_analyzer.sizing.udt import compute_aoi_definition_cost

    model = load_memory_model()
    aoi = DataTypeDef(
        name="MixedShape",
        members=[
            Member(name="EnableIn", data_type="BOOL", dimension=0),
            Member(name="EnableOut", data_type="BOOL", dimension=0),
            Member(name="Tmr1", data_type="TIMER", dimension=0),
            Member(name="Tmr2", data_type="TIMER", dimension=0),
            Member(name="Mot1", data_type="MOTION_INSTRUCTION", dimension=0),
            Member(name="Plain", data_type="DINT", dimension=0),
        ],
        is_aoi=True,
    )
    children = _expand_aoi_definition(aoi, model)
    total, _basis = compute_aoi_definition_cost(aoi.name, {aoi.name: aoi}, model)
    assert sum(c.bytes for c in children) == total
    assert any(c.segment == ".typeextra" for c in children)
