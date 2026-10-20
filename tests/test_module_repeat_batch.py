"""OQ-MODREPEAT: the modrep_* batch's shape."""

from __future__ import annotations

import re

from sample_gen import gen_module_repeat as M
from sample_gen.lint import lint_l5x


def test_the_batch_is_36_files_round_one_unchanged():
    ids = [sid for sid, _what, _fn in M.plan()]
    assert len(ids) == len(set(ids)) == 36
    assert ids[:15] == [f"modrep_{M._slug(c)}_n{n:02d}" for c in M.CATALOGS for n in M.COUNTS]
    assert M.target_name("modrep_ex260_sen1_a_n04") == "ModRepEX260SEN1AN4"


def test_a_point_rack_is_sized_to_its_cards():
    xml = M.point_rack_xml(4)
    assert '<Bus Size="5" />' in xml and "AB:1734_5SLOT:I:0" in xml
    assert re.findall(r'Address="(\d)" Type="PointIO" Upstream="true"', xml) == ["1", "2", "3", "4"]


def test_5069_racks_keep_their_captured_bus_and_each_card_its_own_slot():
    xml = M.racks_5069_xml(4, 1)
    assert xml.count('<Bus Size="32"/>') == 4
    assert re.findall(r'ParentModule="(AENT\d)"', xml) == ["AENT1", "AENT2", "AENT3", "AENT4"]
    one = M.racks_5069_xml(1, 4)
    assert re.findall(r'<Port Id="1" Address="(\d+)"\s*Type="5069"\s*Upstream="true"', one) == ["1", "2", "3", "4"]


def test_each_round_two_shape_is_lint_clean_on_the_floor():
    fns = {sid: fn for sid, _what, fn in M.plan()}
    for sid in ("modrep_1734_ie2c_c_rack_n02", "modrep_5069_ob16_b_r4x1", "modrep_genem_diff"):
        assert not lint_l5x(M.make(sid, fns[sid])), sid
