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
    assert ots.mixed_surcharge_for("MOV", ["REAL", "INT"], 1) is None
