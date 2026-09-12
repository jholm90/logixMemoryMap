"""The AOI instance-array block is padded to an 8-byte boundary.

OQ-AOIBOOLPACK-PAIRING, derived 2026-09-12 from 48 captured sweep families
with zero exceptions. These lock the shape of the rule rather than a single
byte count: that padding is applied to the WHOLE block and not per instance
(per-instance padding would make the residual grow with instance count, and
the real data is flat in n), and that it is identically zero whenever the
per-instance size is already 8-aligned.
"""

from __future__ import annotations

import pytest

from l5x_memory_analyzer.parser.datatypes import DataTypeDef, Member
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.udt import compute_array_size


def _aoi(name: str, members: list[tuple[str, str]]) -> DataTypeDef:
    return DataTypeDef(
        name=name,
        members=[Member(name=n, data_type=t, dimension=0) for n, t in members],
        is_aoi=True,
    )


@pytest.fixture
def model():
    return load_memory_model()


def test_block_alignment_constant_is_eight(model):
    assert model.aoi_array.block_alignment_bytes == 8


def _size(aoi: DataTypeDef, n: int, model) -> int:
    size, _conf = compute_array_size(aoi.name, (n,), {aoi.name: aoi}, model)
    return size


def test_every_array_length_lands_on_an_eight_byte_boundary(model):
    """Whatever the per-instance size, the block is 8-aligned."""
    aoi = _aoi("AlignProbe", [(f"In{i}", "DINT") for i in range(3)])
    for n in range(1, 13):
        assert _size(aoi, n, model) % 8 == 0, n


def test_odd_length_costs_four_more_when_per_instance_is_four_mod_eight(model):
    """The residual that started this question: a single BOOL parameter gives a
    4-byte instance, so odd lengths pay a 4-byte pad and even lengths do not."""
    aoi = _aoi("AlignOneBool", [("InB0", "BOOL")])
    per = _size(aoi, 2, model) // 2
    assert per % 8 == 4
    assert _size(aoi, 3, model) == _size(aoi, 2, model) + per + 4
    assert _size(aoi, 4, model) == _size(aoi, 3, model) + per - 4


def test_padding_is_zero_when_per_instance_is_already_aligned(model):
    """An 8-aligned instance size must show no parity effect at all -- this is
    the half of the rule that the 'pure BOOL versus mixed' reading got wrong."""
    # 3 DINT declared -> 12-byte instance, less the 4-byte flat discount = 8.
    aoi = _aoi("AlignAligned", [(f"In{i}", "DINT") for i in range(3)])
    per = _size(aoi, 2, model) // 2
    assert per % 8 == 0
    for n in range(1, 9):
        assert _size(aoi, n, model) == per * n


def test_padding_is_per_block_not_per_instance(model):
    """A per-instance pad would grow linearly with n; a block pad never
    exceeds 7 bytes no matter how long the array gets."""
    aoi = _aoi("AlignBlockOnly", [("InB0", "BOOL")])
    per = _size(aoi, 2, model) // 2
    for n in (1, 3, 25, 101, 1001):
        assert 0 <= _size(aoi, n, model) - per * n < 8, n
