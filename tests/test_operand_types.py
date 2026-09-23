"""Operand -> type resolution for the operand-type surcharge (sizing/operand_types.py)."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from l5x_memory_analyzer.sizing.constants import load_memory_model  # noqa: E402
from l5x_memory_analyzer.sizing.operand_types import FileOperandTypes  # noqa: E402
from l5x_memory_analyzer.sizing.report import build_report  # noqa: E402
from sample_gen.builders import MemberSpec, rung_xml, tag_xml, udt_xml  # noqa: E402
from sample_gen.wrapper import build_l5x  # noqa: E402

_MEMBERS = [MemberSpec("Pv", "REAL"), MemberSpec("Cnt", "INT"), MemberSpec("On", "BOOL")]


def _file(rungs: list[str], program_tags: str = "") -> str:
    tags = "\n".join([
        tag_xml("U", "OtUdt", udt_members=_MEMBERS),
        tag_xml("UA", "OtUdt", dimensions=(4,), udt_members=_MEMBERS),
        tag_xml("R", "REAL"), tag_xml("D", "DINT"), tag_xml("W", "DINT"),
        '<Tag Name="AlR" TagType="Alias" Radix="Float" AliasFor="U.Pv" ExternalAccess="Read/Write"/>',
    ])
    return build_l5x(target_name="OpTypes", tags_xml=tags, extra_datatypes_xml=udt_xml("OtUdt", _MEMBERS),
                     extra_program_tags_xml=program_tags,
                     extra_rungs_xml="\n".join(rung_xml(i, r) for i, r in enumerate(rungs)))


def test_resolves_every_spelling():
    root = ET.fromstring(_file(["NOP();"], program_tags=tag_xml("P", "INT")))
    t = FileOperandTypes(root).for_program("MainProgram")
    assert t.resolve("U.Pv") == "REAL"
    assert t.resolve("UA[W].Cnt") == "INT"
    assert t.resolve("U.On") == "BOOL"
    assert t.resolve("W.3") == "BOOL"
    assert t.resolve("AlR") == "REAL"
    assert t.resolve("P") == "INT"
    assert t.resolve("5") is None and t.resolve("1.5") is None
    assert t.resolve("Rack:1:I.0") is None
    assert FileOperandTypes(root).for_program("NoSuchProgram").resolve("P") is None


def _total(rung: str) -> int:
    entries, _ = build_report(ET.fromstring(_file([rung])), load_memory_model())
    return sum(e.bytes for e in entries)


def test_member_path_pays_the_same_surcharge_as_a_bare_tag():
    # MOV REAL surcharge is 24 (memory_model.yaml operand_type_surcharge).
    assert _total("MOV(U.Pv,R);") == _total("MOV(R,R);")
    assert _total("MOV(U.Pv,R);") - _total("MOV(D,D);") == 24
    assert _total("MOV(AlR,R);") == _total("MOV(R,R);")
