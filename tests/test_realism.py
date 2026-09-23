"""The realism floor: >= 5 I/O nodes, >= 25% fill, no output bit written twice."""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from sample_gen import realism  # noqa: E402
from sample_gen.builders import rung_xml, tag_xml  # noqa: E402
from sample_gen.lint import lint_l5x, realism_findings  # noqa: E402
from sample_gen.manifest import predicted_bytes  # noqa: E402
from sample_gen.wrapper import build_l5x  # noqa: E402


@pytest.fixture(scope="module")
def baseline() -> str:
    return build_l5x(target_name="RealismGuard", **realism.with_baseline(tags_xml=""))


def _kinds(l5x: str, predicted: int | None) -> set[str]:
    return {f.kind for f in realism_findings(l5x, predicted)}


def test_baseline_meets_the_floor(baseline):
    assert lint_l5x(baseline) == []
    assert _kinds(baseline, predicted_bytes(baseline)) == set()


def test_baseline_alone_is_over_a_quarter_of_an_l81e(baseline):
    assert predicted_bytes(baseline) >= 3_145_728 // 4


def test_racks_are_the_specified_shape(baseline):
    root = ET.fromstring(baseline)
    adapters = [m for m in root.iter("Module") if m.get("CatalogNumber") == "1734-AENTR/C"]
    assert [m.get("Name") for m in adapters] == ["RACK_1", "RACK_2", "RACK_3", "RACK_4", "RACK_5"]
    for rack in adapters:
        assert rack.find(".//Bus").get("Size") == "9"
        assert "AB:1734_9SLOT:I:0" in ET.tostring(rack, encoding="unicode")
        cards = {int(m.find(".//Port").get("Address")): m.get("CatalogNumber")
                 for m in root.iter("Module") if m.get("ParentModule") == rack.get("Name")}
        assert cards == {1: "1734-IB8/C", 2: "1734-IB8/C", 3: "1734-IB8/C", 4: "1734-IB8/C",
                         5: "1734-OB8/C", 6: "1734-OB8/C", 7: "1734-OB8/C", 8: "1734-OB8/C"}
    assert len(realism.input_points()) == len(realism.output_points()) == 160


def test_bare_file_is_refused():
    l5x = build_l5x(target_name="Bare", tags_xml="")
    assert _kinds(l5x, predicted_bytes(l5x)) == {"realism_io_nodes", "realism_fill"}


@pytest.mark.parametrize("rungs,refused", [
    (["XIC(A)OTE(B);", "XIC(C)OTE(D);"], False),
    (["XIC(A)OTE(B);", "XIC(C)OTE(B);"], True),
    (["XIC(A)ONS(B)OTE(D);", "XIC(C)OTE(B);"], True),
    (["XIC(A)OTL(B);", "XIC(C)OTU(B);"], False),
    (["XIC(A)OTL(B);", "XIC(C)OTE(B);"], True),
])
def test_duplicate_output_bits(rungs, refused):
    tags = "\n".join(tag_xml(n, "BOOL") for n in "ABCD")
    l5x = build_l5x(target_name="Dup", tags_xml=tags,
                    extra_rungs_xml="\n".join(rung_xml(i, r) for i, r in enumerate(rungs)))
    assert ("realism_duplicate_output_bit" in _kinds(l5x, None)) is refused


def test_every_station_output_is_written_once(baseline):
    outs = re.findall(r"\bOTE\((Stn\d+\.\w+)\)", baseline)
    assert len(outs) == len(set(outs)) == realism.STATIONS * 5
