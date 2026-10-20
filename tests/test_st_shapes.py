"""OQ-STSHAPE: how an ST operand is read, and the stshape_* batch's shape."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.operand_types import FileOperandTypes
from l5x_memory_analyzer.sizing.structured_text import (
    _cpt_call_for, _operands, parse_st_routines, size_st_assignments, strip_comments)
from sample_gen import gen_st_shapes as S
from sample_gen.lint import lint_l5x

MODEL = load_memory_model()


def test_every_comment_form_is_stripped():
    code = strip_comments("A := 1; // x := 2;\n(* FOR i := 0 TO 9 DO *)\n/* IF B THEN C := 3; END_IF; */\nD := 4;")
    assert ":=" in code and "FOR" not in code and "IF" not in code and "C :=" not in code and "x :=" not in code


def test_an_operand_is_read_whole_and_its_index_is_not_a_source():
    assert _operands("StU[Ix].A + StE[Ix + 1] * MPS.Count - ABS(R0) + 1.5") == [
        "StU[Ix].A", "StE[Ix + 1]", "MPS.Count", "R0"]
    assert _operands("Arc[MPS.Day].Cnt[i] AND NOT B") == ["Arc[MPS.Day].Cnt[i]", "B"]
    call = _cpt_call_for("StR[3]", "StR[3] + 1.5")
    assert call.operators == ["+"] and call.int_literals == 0 and call.float_literals == 1
    call = _cpt_call_for("StD[i]", "StE[Ix + 1] + 1")
    assert call.operators == ["+"] and call.int_literals == 1 and call.operand_names == ("StE[Ix + 1]",)


def _st_cost(sample_id: str, scope: bool) -> int:
    lines = dict((sid, lines) for sid, lines, _ in S.plan())[sample_id]
    root = ET.fromstring(S.make(sample_id, lines))
    routine = next(r for r in parse_st_routines(root) if r.routine_name == "StTarget")
    flat = {t.get("Name"): t.get("DataType") for t in root.findall("Controller/Tags/Tag")}
    types = FileOperandTypes(root).for_program(routine.program_name) if scope else flat
    return size_st_assignments(routine, MODEL, types)[0]


def test_a_real_member_destination_prices_as_real_through_the_scope():
    # The same statement on a REAL array element and on a REAL UDT member costs the same
    # once the member resolves; through a flat tag table the member reads as untyped.
    assert _st_cost("stshape_real_member400", scope=True) == _st_cost("stshape_real400", scope=True)
    assert _st_cost("stshape_real_member400", scope=False) != _st_cost("stshape_real400", scope=False)


def test_the_batch_is_42_files_and_one_of_each_family_lints_clean():
    plan = dict((sid, lines) for sid, lines, _ in S.plan())
    assert len(plan) == 42
    for sid in ("stshape_n00", "stshape_vidx_offset400", "stshape_if_nested200", "stshape_aoi_if200"):
        assert not lint_l5x(S.make(sid, plan[sid])), sid


def test_the_aoi_logic_routine_is_structured_text():
    definition, storage = S.aoi_definition(["LD[0] := LD[0] + 1;"])
    root = ET.fromstring(definition)
    assert [(r.get("Name"), r.get("Type")) for r in root.iter("Routine")] == [("Logic", "ST")]
    assert {m.name for m in storage} >= {"InA", "InB", "LD", "LE", "LB"}
