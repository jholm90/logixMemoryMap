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


@pytest.fixture(scope="module")
def report() -> dict:
    return {k["key"]: {i["name"]: i for i in k["items"]} for k in unused_report(UsageIndex(ET.fromstring(_l5x())))["kinds"]}


def test_statuses_of_controller_tags(report):
    tags = report["controller_tags"]
    assert tags["Dst"]["status"] == "used"
    assert tags["Nobody"]["status"] == "unused"
    assert tags["Rec"]["status"] == "partial"
    assert {e["name"]: e["used"] for e in tags["Rec"]["elements"]} == {"Rec.Id": True, "Rec.Spare": False}
    assert tags["Whole"]["status"] == "used"      # every member used through the whole structure
    assert all(e["whole"] for e in tags["Whole"]["elements"])


def test_small_atomic_array_lists_each_element(report):
    arr = report["controller_tags"]["Arr"]
    assert [e["name"] for e in arr["elements"] if e["used"]] == ["Arr[0]", "Arr[2]"]
    assert arr["status"] == "partial" and arr["unused_elements"] == 2


def test_udt_elements(report):
    udts = report["udt_elements"]
    assert udts["Idle_t"]["status"] == "unused"   # no tag of the type
    assert udts["Rec_t"]["status"] in ("used", "partial")
    assert {e["name"] for e in udts["Rec_t"]["elements"]} == {"Id", "Spare"}


def test_endpoints(tmp_path):
    from l5x_memory_analyzer.ui.server import create_app
    path = tmp_path / "unused.L5X"
    path.write_text(_l5x(), encoding="utf-8")
    client = create_app(str(path)).test_client()
    summary = client.get("/api/unused").get_json()
    kinds = {k["key"]: k for k in summary["kinds"]}
    assert set(kinds) == {"controller_tags", "program_tags", "aoi_tags", "udt_elements"}
    names = [i["name"] for i in kinds["controller_tags"]["items"]]
    detail = client.get(f"/api/unused/item?kind=controller_tags&index={names.index('Rec')}").get_json()
    assert detail["name"] == "Rec" and len(detail["elements"]) == 2
    assert "elements" in kinds["controller_tags"]["items"][0] and isinstance(kinds["controller_tags"]["items"][0]["elements"], int)
    assert client.get("/api/unused/item?kind=nope&index=0").status_code == 404
