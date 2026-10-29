"""Where each ladder instruction may stand in a rung (sample_gen.ladder_roles), and lint's use of it."""

import pytest

from sample_gen.ladder_roles import role, rung_findings, terminated


@pytest.mark.parametrize("mn,expected", [
    ("OTE", "output"), ("MOV", "output"), ("MAM", "output"), ("TON", "output"),
    ("NEQ", "condition"), ("GRT", "condition"), ("CMP", "condition"), ("GT", "condition"), ("XIC", "condition"),
    ("ONS", "condition"), ("IsINF", "condition"), ("AFI", "condition"),
    ("IOT", "control"), ("UIE", "control"), ("MCR", "control"), ("LBL", "control"), ("SBR", "control"),
])
def test_roles(mn, expected):
    assert role(mn) == expected


def kinds(text, aois=frozenset()):
    return [k for k, _ in rung_findings(text, aois)]


@pytest.mark.parametrize("text", [
    "XIC(a)OTE(b);", "LBL(L1)NOP();", "LBL(L1)XIC(a)OTE(b);", "SBR(x)NOP();", "XIC(a)MCR();", "MCR();",
    "[XIC(a),XIC(b)]OTE(c);", "XIC(a)[OTE(b),MOV(1,c)];", "MOV(a,b)XIC(c)OTE(d);", "IOT(Rack:O);",
    "XIC(a)[GRT(b,1),LES(b,5)]NOP();", "UID();",
])
def test_valid_rungs(text):
    assert kinds(text) == []


@pytest.mark.parametrize("text,kind", [
    ("MOV(a,b)EQU(c,d);", "condition_at_rung_end"),
    ("XIC(a)[OTE(b),XIC(c)];", "condition_at_rung_end"),
    ("XIC(a)LBL(L1)NOP();", "must_be_first_on_rung"),
    ("XIC(a)SBR(x)NOP();", "must_be_first_on_rung"),
    ("MCR()NOP();", "must_be_last_on_rung"),
    ("LBL(L1);", "first_on_rung_needs_trailing"),
])
def test_invalid_rungs(text, kind):
    assert kind in kinds(text)


def test_an_aoi_named_like_an_instruction_is_not_held_to_its_rules():
    assert kinds("XIC(a)LBL(x);", frozenset({"LBL"})) == []


def test_terminated_adds_a_nop_only_after_a_condition():
    assert terminated("XIC(a)EQU(b,c);") == "XIC(a)EQU(b,c)NOP();"
    assert terminated("XIC(a)OTE(b);") == "XIC(a)OTE(b);"


def _wrap(rungs):
    body = "".join(f'<Rung Number="{i}" Type="N"><Text><![CDATA[{t}]]></Text></Rung>' for i, t in enumerate(rungs))
    return ('<RSLogix5000Content><Controller Name="C" MajorRev="35"><Programs><Program Name="P"><Routines>'
            f'<Routine Name="R" Type="RLL"><RLLContent>{body}</RLLContent></Routine>'
            '</Routines></Program></Programs></Controller></RSLogix5000Content>')


def test_lint_refuses_a_misplaced_instruction():
    from sample_gen.lint import lint_l5x
    found = {f.kind for f in lint_l5x(_wrap(["NOP();", "SBR(x)NOP();", "MOV(a,b)EQU(c,d);", "XIC(a)LBL(L)NOP();",
                                            "MCR()NOP();"]))}
    assert {"sbr_not_first_rung", "condition_at_rung_end", "must_be_first_on_rung", "must_be_last_on_rung"} <= found


def test_lint_accepts_well_placed_rungs():
    from sample_gen.lint import lint_l5x
    kinds = {f.kind for f in lint_l5x(_wrap(["SBR(x)NOP();", "LBL(L)NOP();", "XIC(a)MCR();"]))}
    assert not kinds & {"sbr_not_first_rung", "condition_at_rung_end", "must_be_first_on_rung", "must_be_last_on_rung"}
