"""OQ-INDIRECTUDT and OQ-MIXEDTYPE: the laws measured on the realism floor
(opsp_ind_*, opsp_str_movidx, opsp_mixed_*), pinned against the model."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from l5x_memory_analyzer.parser.logic import _indirect_index_sites  # noqa: E402
from l5x_memory_analyzer.sizing.constants import load_memory_model  # noqa: E402

LOGIC = load_memory_model().logic_instructions


def test_index_sites_carry_the_array_path_and_what_follows():
    assert _indirect_index_sites(["MOV(A[I].M,D);XIC(B[I])OTE(Q);MOV(S.T[S.I+1],X);XIC(W[I].3)"]) == [
        ("tag", "A", "member"), ("tag", "B", ""), ("tag_offset", "S.T", ""), ("tag", "W", "bit")]


def test_element_costs():
    ix = LOGIC.indirect_index
    assert ix.cost_for("tag") + ix.element_cost_for("member", None) == 124
    assert ix.cost_for("tag") + ix.element_cost_for("", "BOOL") == 104
    assert ix.cost_for("tag") + ix.element_cost_for("", "STRING") == 192
    assert ix.element_cost_for("", "DINT") == 0 and ix.element_cost_for("bit", None) == 0


def test_mixed_type_law_reproduces_every_measured_call():
    ots = LOGIC.operand_type_surcharge
    measured = {
        ("MOV", ("DINT", "REAL"), 1): 76, ("MOV", ("REAL", "DINT"), 1): 72,
        ("MOV", ("INT", "DINT"), 1): 60, ("MOV", ("DINT", "INT"), 1): 52,
        ("ADD", ("DINT", "REAL", "REAL"), 2): 68, ("ADD", ("REAL", "DINT", "DINT"), 2): 108,
        ("GRT", ("REAL", "DINT"), None): 68, ("GRT", ("INT", "DINT"), None): 60,
    }
    for (mnemonic, types, dest), cost in measured.items():
        assert ots.mixed_surcharge_for(mnemonic, list(types), dest) == cost, (mnemonic, types)
    assert ots.mixed_surcharge_for("MOV", ["REAL", "REAL"], 1) is None
    # REAL with INT is measured now (litint_int_*_flit): REAL 24 + INT destination 48.
    assert ots.mixed_surcharge_for("MOV", ["REAL", "INT"], 1) == 72


def test_literals_take_the_type_their_spelling_implies():
    """OQ-LITREAL: every rule reproduces the litreal_*/litint_*/realidiom_mam_* captures."""
    from l5x_memory_analyzer.sizing.constants import FLOAT_LITERAL as F
    from l5x_memory_analyzer.sizing.constants import INT_LITERAL as I
    from l5x_memory_analyzer.sizing.logic import _operand_type

    class _NoTags:
        def resolve(self, op):
            return None

    lt = LOGIC.operand_type_surcharge.literal_types
    assert [_operand_type(op, _NoTags(), lt) for op in ("5", "-1", "5.0", "1.5e3", "Tag")] == [I, I, F, F, None]
    o = LOGIC.operand_type_surcharge
    measured = {  # per call, over the same call with a tag of the call's own type
        ("GRT", ("REAL", I), None): 16 + 52, ("ADD", ("REAL", I, "REAL"), 2): 16 + 52,
        ("LIM", (I, "REAL", I), None): -8 + 96, ("MOV", (F, "REAL"), 1): 24 + 4,
        ("MOV", (I, "INT"), 1): 104 - 52, ("ADD", ("INT", I, "INT"), 2): 156 - 52,
        ("GRT", ("SINT", I), None): 88 - 40, ("MOV", (F, "DINT"), 1): 76,
        ("ADD", ("DINT", F, "DINT"), 2): 112, ("ADD", ("INT", F, "INT"), 2): 168,
        ("GRT", ("SINT", F), None): 116, ("LIM", ("INT", "INT", F), None): 204,
    }
    for (mnemonic, types, dest), cost in measured.items():
        assert o.mixed_surcharge_for(mnemonic, list(types), dest) == cost, (mnemonic, types)
    assert o.mixed_surcharge_for("GRT", ("DINT", I), None) is None  # free beside DINT
    assert o.literal_run_cost(2, 0) == 96 and o.literal_run_cost(4, 0) == 184 and o.literal_run_cost(0, 4) == 16
    assert o.single_operand_surcharge("CLR", "REAL") == 0 and o.single_operand_surcharge("CLR", "INT") == 52
