"""OQ-AOIBOOLINST: the aoibool_* batch's shape."""

from __future__ import annotations

import re

from sample_gen import gen_aoi_bool_instances as A
from sample_gen.lint import lint_l5x


def test_the_batch_is_22_files_with_three_counts_per_bool_width():
    plan = {sid: kw for sid, kw, _ in A.plan()}
    assert len(plan) == 22
    for k in A.KS:
        assert {plan[f"aoibool_k{k:02d}_{n}"]["n"] for n in ("def", "n01", "n50")} == {0, 1, 50}


def test_bool_bits_bracket_each_32_bit_word():
    words = [-(-(k + 4) // 32) for k in A.KS]
    assert words == [1, 1, 2, 2, 2, 3]


def test_instances_are_scalar_and_named_alike_and_the_array_is_one_tag():
    plan = {sid: kw for sid, kw, _ in A.plan()}
    l5x = A.make("aoibool_k55_n50", plan["aoibool_k55_n50"])
    names = re.findall(r'<Tag Name="(BiI\d\d)"[^>]*DataType="BoolInst"', l5x)
    assert len(names) == 50 and {len(n) for n in names} == {5}
    arr = A.make("aoibool_k55_arr50", plan["aoibool_k55_arr50"])
    assert re.search(r'<Tag Name="BiArr"[^>]*DataType="BoolInst" Dimensions="50"', arr)
    assert not lint_l5x(l5x) and not lint_l5x(arr)
    assert not lint_l5x(A.make("aoibool_p55_n01", plan["aoibool_p55_n01"]))
