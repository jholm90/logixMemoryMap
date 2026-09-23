"""The confound checker must not wave a family through.

A false clean is worse than no check: it certifies a family as differenceable
when a capture on it will measure a sum. Three real blind spots were found
and fixed -- expressions inside a rung operand, ST bodies in
<Line>, and definition member order -- each of which made genuinely different
files read as byte-identical. These lock all three, and the confound case.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from confound_check import differing, profile  # noqa: E402

HEAD = ('<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="35.05">'
        '<Controller Name="T" ProcessorType="1756-L81E">')
TAIL = "</Controller></RSLogix5000Content>"


def _write(tmp_path, name, body):
    p = tmp_path / name
    p.write_text(HEAD + body + TAIL)
    return profile(str(p))


def _rung(text):
    return ("<Programs><Program Name=\"P\"><Routines><Routine Name=\"R\">"
            f"<RLLContent><Rung Number=\"0\"><Text>{text}</Text></Rung>"
            "</RLLContent></Routine></Routines></Program></Programs>")


def _st(lines):
    body = "".join(f"<Line Number=\"{i}\">{t}</Line>" for i, t in enumerate(lines))
    return ("<Programs><Program Name=\"P\"><Routines><Routine Name=\"R\" Type=\"ST\">"
            f"<STContent>{body}</STContent></Routine></Routines></Program></Programs>")


def test_expression_content_is_visible(tmp_path):
    """CPT tier arrangement: one opcode, one operand, different expression."""
    a = _write(tmp_path, "a.L5X", _rung("CPT(Dest,A+B*C);"))
    b = _write(tmp_path, "b.L5X", _rung("CPT(Dest,A*B+C);"))
    assert differing(a, b) == ["operand text"]


def test_st_body_is_visible(tmp_path):
    """ST operator families live in <Line>, which no rung sweep reaches."""
    a = _write(tmp_path, "a.L5X", _st(["D0 := D1 + D2;"]))
    b = _write(tmp_path, "b.L5X", _st(["D0 := D1 * D2;"]))
    assert differing(a, b) == ["ST text"]


def test_definition_member_order_is_visible(tmp_path):
    """Permuting members changes nothing countable."""
    def udt(members):
        inner = "".join(f'<Member Name="{n}" DataType="{t}"/>' for n, t in members)
        return f'<DataTypes><DataType Name="U">{inner}</DataType></DataTypes>'
    a = _write(tmp_path, "a.L5X", udt([("b1", "BOOL"), ("d1", "DINT")]))
    b = _write(tmp_path, "b.L5X", udt([("d1", "DINT"), ("b1", "BOOL")]))
    assert differing(a, b) == ["definition member order"]


def test_two_dimensions_moving_is_reported_as_a_confound(tmp_path):
    a = _write(tmp_path, "a.L5X",
               '<Tags><Tag Name="T1" DataType="DINT"/></Tags>' + _rung("XIC(A)OTE(B);"))
    b = _write(tmp_path, "b.L5X",
               '<Tags><Tag Name="T1" DataType="DINT"/><Tag Name="T2" DataType="DINT"/></Tags>'
               + _rung("XIC(A)XIC(C)OTE(B);"))
    assert sorted(differing(a, b)) == ["instruction inventory", "tag inventory"]


def test_identical_files_report_nothing_moving(tmp_path):
    a = _write(tmp_path, "a.L5X", _rung("XIC(A)OTE(B);"))
    b = _write(tmp_path, "b.L5X", _rung("XIC(A)OTE(B);"))
    assert differing(a, b) == []


def test_a_finer_dimension_does_not_double_report_its_parent(tmp_path):
    """Changing the opcode moves operand shapes and text too; only the most
    informative one is reported, or every real change reads as a confound."""
    a = _write(tmp_path, "a.L5X", _rung("XIC(A)OTE(B);"))
    b = _write(tmp_path, "b.L5X", _rung("XIO(A)OTE(B);"))
    assert differing(a, b) == ["instruction inventory"]


def test_branch_arrangement_is_visible(tmp_path):
    """Same opcodes, same operands, different bracket structure -- the exact
    shape OQ-RUNGSHAPE was opened to test, and invisible to every other
    dimension."""
    a = _write(tmp_path, "a.L5X", _rung("XIC(A)XIC(B)OTE(C);"))
    b = _write(tmp_path, "b.L5X", _rung("[XIC(A),XIC(B)]OTE(C);"))
    assert differing(a, b) == ["rung structure"]


def test_subscript_commas_are_not_operand_separators(tmp_path):
    """`COP(Hist[0,0],Tmp[0,0],800)` is three operands, not five. Counting
    them naively manufactured a real-versus-corpus operand-shape gap that does
    not exist."""
    from confound_check import _split_operands
    assert _split_operands("Hist[0,0],Tmp[0,0],800") == ["Hist[0,0]", "Tmp[0,0]", "800"]
    assert _split_operands("A,B,C") == ["A", "B", "C"]
    assert _split_operands("") == []


def test_tag_declaration_order_is_visible(tmp_path):
    """Permuting the same tag multiset changes nothing countable, so a Counter
    over tag types calls two order-test files byte-identical."""
    def tags(seq):
        return "<Tags>" + "".join(
            f'<Tag Name="T{i}" DataType="{ty}"/>' for i, ty in enumerate(seq)) + "</Tags>"
    a = _write(tmp_path, "a.L5X", tags(["BOOL", "BOOL", "DINT", "DINT"]))
    b = _write(tmp_path, "b.L5X", tags(["BOOL", "DINT", "BOOL", "DINT"]))
    assert differing(a, b) == ["tag declaration order"]


def test_array_subscript_is_not_a_branch(tmp_path):
    """`A[1].B` is an operand spelling, not a branch leg."""
    a = _write(tmp_path, "a.L5X", _rung("MOV(A.B,D);"))
    b = _write(tmp_path, "b.L5X", _rung("MOV(A[1].B,D);"))
    c = _write(tmp_path, "c.L5X", _rung("XIC(X)[OTE(Y),OTE(Z)];"))
    assert differing(a, b) == ["operand text"]
    assert a["branched rungs"] == b["branched rungs"] == 0 and c["branched rungs"] == 1
