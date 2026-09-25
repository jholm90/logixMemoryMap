"""gen_motion_operands: every motop_* pair differs only in the operands under test."""

import re

from sample_gen import gen_motion_operands as g

def _skeleton(text: str) -> str:
    """The rung with every operand blanked: what must match across a pair."""
    return re.sub(r"\(([^()]*)\)", lambda m: "(" + ",".join("_" for _ in m.group(1).split(",")) + ")", text)


def test_isolation_pairs_match_rung_shape():
    s = g._isolation()
    pairs = [("axr_mov_ref_n400", "axr_mov_cip_n400"), ("axr_grt_ref_n400", "axr_grt_cip_n400"),
             ("axr_lim_ref_n400", "axr_lim_cip_n400"), ("axr_sub2_ref_n400", "axr_sub2_cip_n400"),
             ("axb_xic_ref_n400", "axb_xic_cip_n400"), ("mi_xic_tmr_arr_n400", "mi_xic_mi_arr_n400"),
             ("mi_xic_tmr_sc_n400", "mi_xic_mi_sc_n400"), ("mi_xic_tmr_udt_n400", "mi_xic_mi_udt_n400"),
             ("mi_otu_tmr_arr_n400", "mi_otu_mi_arr_n400"), ("mi_otu_tmr_sc_n400", "mi_otu_mi_sc_n400"),
             ("mi_otu_tmr_udt_n400", "mi_otu_mi_udt_n400")]
    for control, test in pairs:
        a, b = s[control][0], s[test][0]
        assert len(a) == len(b) == g.N
        assert [_skeleton(x) for x in a] == [_skeleton(x) for x in b]


def test_density_files_carry_the_same_units():
    units = re.compile(r"MoC\[(\d+)\]")
    for stem, (rungs, _) in g._density().items():
        seen = sorted(int(u) for r in rungs for u in units.findall(r))
        assert seen == list(range(g.UNITS)), stem


def test_every_output_bit_written_once():
    for group in (g._isolation(), g._density()):
        for stem, (rungs, _) in group.items():
            written = [op for r in rungs for op in re.findall(r"OTE\(([^)]+)\)", r)]
            assert len(written) == len(set(written)), stem


def test_no_real_rung_templates():
    """A real rung's structure rebuilt over synthetic tags is customer-derived content."""
    assert not hasattr(g, "_templates")
    assert not any(p.name.startswith("motop_tpl_") for p in g.OUT_ROOT.glob("*.L5X"))
