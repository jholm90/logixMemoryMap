"""The Report tab's unused analysis (l5x_memory_analyzer/unused.py) and its endpoints."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from l5x_memory_analyzer.unused import unused_report  # noqa: E402
from l5x_memory_analyzer.usage import UsageIndex  # noqa: E402
from sample_gen.builders import MemberSpec, rung_xml, tag_xml, udt_xml  # noqa: E402
from sample_gen.wrapper import build_l5x  # noqa: E402

_REC = [MemberSpec("Id", "DINT"), MemberSpec("Spare", "DINT")]
_IDLE = [MemberSpec("A", "DINT"), MemberSpec("B", "DINT")]


def _l5x() -> str:
    tags = "\n".join([
        tag_xml("Rec", "Rec_t", udt_members=_REC),          # partial: Id used, Spare not
        tag_xml("Whole", "Rec_t", udt_members=_REC),        # used as a whole by COP
        tag_xml("Copy", "Rec_t", udt_members=_REC),
        tag_xml("Dst", "DINT"), tag_xml("Nobody", "DINT"),  # used / unused
        tag_xml("Arr", "DINT", dimensions=(4,)),             # elements 0 and 2 used
    ])
    rungs = "\n".join(rung_xml(i, t) for i, t in enumerate([
        "MOV(Rec.Id,Dst);", "COP(Whole,Copy,1);", "MOV(Arr[0],Arr[2]);",
    ]))
    return build_l5x(target_name="Unused", tags_xml=tags,
                     extra_datatypes_xml=udt_xml("Rec_t", _REC) + udt_xml("Idle_t", _IDLE),
                     extra_rungs_xml=rungs)


def _report() -> dict:
    from l5x_memory_analyzer.parser.aoi import parse_aoi_definitions
    from l5x_memory_analyzer.parser.datatypes import parse_data_types
    from l5x_memory_analyzer.sizing.constants import load_memory_model
    root = ET.fromstring(_l5x())
    types = {**parse_data_types(root), **parse_aoi_definitions(root)}
    return unused_report(UsageIndex(root), types, load_memory_model())


@pytest.fixture(scope="module")
def report() -> dict:
    return {k["key"]: {i["n"]: i for i in k["items"]} for k in _report()["kinds"]}


def _leaves(node, prefix=""):
    if not node.get("c"):
        return {prefix: bool(node["u"])}
    out = {}
    for c in node["c"]:
        out.update(_leaves(c, prefix + (c["n"] if c["n"].startswith("[") else "." + c["n"])))
    return out


def test_statuses_of_controller_tags(report):
    tags = report["controller_tags"]
    assert tags["Dst"]["status"] == "used"
    assert tags["Nobody"]["status"] == "unused"
    assert tags["Rec"]["status"] == "partial"
    assert _leaves(tags["Rec"]) == {".Id": True, ".Spare": False}
    assert (tags["Rec"]["u"], tags["Rec"]["k"]) == (1, 2)
    assert tags["Whole"]["status"] == "used"      # every member used through the whole structure
    assert all(c["w"] for c in tags["Whole"]["c"])


def test_sizes_are_the_engines(report):
    tags = report["controller_tags"]
    assert tags["Dst"]["s"] > 0 and all(c["s"] > 0 for c in tags["Rec"]["c"])


def test_every_reference_names_its_place(report):
    """Up to ten places: program, routine, rung."""
    tags = report["controller_tags"]
    assert tags["Dst"]["r"] == [["MainProgram", "MainRoutine", "Rung 0", 1]]
    assert tags["Rec"]["c"][0]["r"] == [["MainProgram", "MainRoutine", "Rung 0", 1]]
    assert tags["Arr"]["r"] == [["MainProgram", "MainRoutine", "Rung 2", 2]]   # twice on one rung: one place, 2 uses
    assert tags["Nobody"]["r"] == []


def test_an_array_is_one_element(report):
    """Never split by index: indirect addressing makes the element unknowable."""
    arr = report["controller_tags"]["Arr"]
    assert "c" not in arr and arr["status"] == "used" and arr["x"] == 2


def test_every_row_carries_its_reference_count(report):
    tags = report["controller_tags"]
    assert tags["Nobody"]["x"] == 0 and tags["Dst"]["x"] == 1
    assert {c["n"]: c["x"] for c in tags["Rec"]["c"]} == {"Id": 1, "Spare": 0}


def test_udt_elements(report):
    udts = report["udt_elements"]
    assert udts["Idle_t"]["status"] == "unused"   # no tag of the type
    assert udts["Rec_t"]["status"] in ("used", "partial")
    assert {c["n"] for c in udts["Rec_t"]["c"]} == {"Id", "Spare"}


def test_endpoints(tmp_path):
    from l5x_memory_analyzer.ui.server import create_app
    path = tmp_path / "unused.L5X"
    path.write_text(_l5x(), encoding="utf-8")
    client = create_app(str(path)).test_client()
    kinds = {k["key"]: k for k in client.get("/api/unused").get_json()["kinds"]}
    assert set(kinds) == {"controller_tags", "program_tags", "aoi_tags", "udt_elements"}
    items = kinds["controller_tags"]["items"]
    assert all("c" not in i for i in items)       # summaries only
    rec = [i["n"] for i in items].index("Rec")
    assert items[rec]["has_children"] and (items[rec]["u"], items[rec]["k"]) == (1, 2)
    detail = client.get(f"/api/unused/item?kind=controller_tags&index={rec}").get_json()
    assert detail["n"] == "Rec" and len(detail["c"]) == 2
    assert client.get("/api/unused/item?kind=nope&index=0").status_code == 404


def test_st_lines_count_from_one_and_fbd_elements_give_sheet_and_position():
    st = ('<Routine Name="Disp" Type="ST"><STContent><Line Number="0"><![CDATA[(* note *)]]></Line>'
          '<Line Number="1"><![CDATA[Dst := Rec.Id;]]></Line></STContent></Routine>')
    fbd = ('<Routine Name="Wire" Type="FBD"><FBDContent SheetSize="Letter - 8.5 x 11 in" SheetOrientation="Landscape">'
           '<Sheet Number="1"><IRef ID="0" X="180" Y="120" Operand="Rec.Id" HideDesc="false"/>'
           '<ORef ID="1" X="420" Y="120" Operand="Dst" HideDesc="false"/><Wire FromID="0" ToID="1"/></Sheet>'
           '</FBDContent></Routine>')
    l5x = build_l5x(target_name="Places", tags_xml=tag_xml("Rec", "Rec_t", udt_members=_REC) + tag_xml("Dst", "DINT"),
                    extra_datatypes_xml=udt_xml("Rec_t", _REC), extra_routines_xml=st + fbd,
                    extra_rungs_xml=rung_xml(0, "JSR(Disp,0);JSR(Wire,0);"))
    u = UsageIndex(ET.fromstring(l5x))
    places = u._tries["controller/Rec"].kids[".Id"].locs
    assert ["MainProgram", "Disp", "Line 2", 1] in places
    assert ["MainProgram", "Wire", "Sheet 1, X 180 Y 120", 1] in places
