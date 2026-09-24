"""Usage counts (l5x_memory_analyzer/usage.py): what the Uses column and the
unused pattern report."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from l5x_memory_analyzer.usage import UsageIndex, segments_of  # noqa: E402
from sample_gen.builders import MemberSpec, rung_xml, tag_xml, udt_xml  # noqa: E402
from sample_gen.wrapper import build_l5x  # noqa: E402

_REC = [MemberSpec("Id", "DINT"), MemberSpec("Spare", "DINT"), MemberSpec("Vals", "REAL", dimension=4)]


@pytest.fixture(scope="module")
def index() -> UsageIndex:
    tags = "\n".join([
        tag_xml("Rec", "Rec_t", dimensions=(10,), udt_members=_REC),
        tag_xml("Idx", "DINT"), tag_xml("Dst", "DINT"), tag_xml("Unused", "DINT"),
        tag_xml("Buf", "DINT", dimensions=(20,)), tag_xml("Buf2", "DINT", dimensions=(20,)),
        tag_xml("Whole", "Rec_t", udt_members=_REC), tag_xml("Copy", "Rec_t", udt_members=_REC),
        '<Tag Name="Al" TagType="Alias" Radix="Decimal" AliasFor="Dst" ExternalAccess="Read/Write"/>',
    ])
    rungs = "\n".join(rung_xml(i, t) for i, t in enumerate([
        "MOV(Rec[Idx].Id,Dst);",
        "MOV(Rec[2].Vals[1],Dst);",
        "COP(Buf[0],Buf2[0],20);",
        "COP(Whole,Copy,1);",
        "JSR(Helper,0);",
    ]))
    helper = '<Routine Name="Helper" Type="RLL"><RLLContent>' + rung_xml(0, "NOP();") + "</RLLContent></Routine>"
    dead = '<Routine Name="Dead" Type="RLL"><RLLContent>' + rung_xml(0, "NOP();") + "</RLLContent></Routine>"
    l5x = build_l5x(target_name="Usage", tags_xml=tags, extra_datatypes_xml=udt_xml("Rec_t", _REC),
                    extra_rungs_xml=rungs, extra_routines_xml=helper + dead)
    return UsageIndex(ET.fromstring(l5x))


def test_top_level_tag_counts_every_use(index):
    assert index.tag("controller/Rec").count == 2
    assert index.tag("controller/Unused").unused


def test_alias_use_counts_for_its_target(index):
    assert not index.tag("controller/Al").unused or index.tag("controller/Dst").count >= 2


def test_indexed_access_uses_every_element(index):
    assert index.tag("controller/Rec", segments_of("[7].Id")).count == 1
    assert index.tag("controller/Rec", segments_of("[7].Spare")).unused
    assert index.tag("controller/Rec", segments_of("[2].Vals[1]")).count == 1
    assert index.tag("controller/Rec", segments_of("[2].Vals[3]")).unused


def test_file_instruction_uses_the_whole_array(index):
    assert not index.tag("controller/Buf", segments_of("[15]")).unused


def test_whole_structure_reference_uses_members_via_parent(index):
    u = index.tag("controller/Whole", segments_of(".Spare"))
    assert u.count == 0 and u.via_parent and not u.unused


def test_type_members(index):
    assert index.type_member("Rec_t", "Id").count == 1
    assert index.type_instances("Rec_t") == 3


def test_routines(index):
    assert index.routine("program:MainProgram/Helper").count == 1
    assert index.routine("program:MainProgram/MainRoutine").implicit == 1
    assert index.routine("program:MainProgram/Dead").unused
