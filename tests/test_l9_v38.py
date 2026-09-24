"""ControlLogix 5590 / firmware v38 shape in build_l5x, and the v36+
instruction spelling (OQ-V36MNEMONIC) in the parser and lint."""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from l5x_memory_analyzer.parser.logic import V36_MNEMONIC_ALIASES, canonical_rung_text  # noqa: E402
from sample_gen.builders import rung_xml, tag_xml  # noqa: E402
from sample_gen.lint import lint_l5x, to_v36_spelling  # noqa: E402
from sample_gen.manifest import predicted_bytes  # noqa: E402
from sample_gen.realism import with_baseline  # noqa: E402
from sample_gen.wrapper import build_l5x  # noqa: E402

_RUNGS = [
    "EQU(A,1)OTE(B0);", "NEQ(A,1)OTE(B1);", "GRT(A,1)OTE(B2);",
    "LES(A,1)OTE(B3);", "GEQ(A,1)OTE(B4);", "LEQ(A,1)OTE(B5);",
]


def _file(major: str = "35", software: str = "35.05", processor: str = "1756-L81E") -> str:
    tags = "\n".join([tag_xml("A", "DINT")] + [tag_xml(f"B{i}", "BOOL") for i in range(6)])
    rungs = "\n".join(rung_xml(i, t) for i, t in enumerate(_RUNGS))
    return build_l5x(target_name="PlatNineT", tags_xml=tags, extra_rungs_xml=rungs,
                     processor_type=processor, major_rev=major, software_revision=software)


def test_canonical_rung_text_maps_every_v36_spelling():
    for new, old in V36_MNEMONIC_ALIASES.items():
        assert canonical_rung_text(f"{new}(A,1)OTE(B);") == f"{old}(A,1)OTE(B);"
    # A member or tag named like a mnemonic is not a call.
    assert canonical_rung_text("XIC(Tag.GE)OTE(NE);") == "XIC(Tag.GE)OTE(NE);"
    # A file-declared AOI of the same name wins.
    assert canonical_rung_text("GE(Inst,A)", frozenset({"GE"})) == "GE(Inst,A)"


def test_v36_spelling_prices_identically():
    v35 = _file(major="38", software="38.02")
    v36 = to_v36_spelling(v35)
    assert "GE(A,1)" in v36 and "GEQ(" not in v36
    assert predicted_bytes(v36) == predicted_bytes(v35)


def test_lint_refuses_v36_spelling_before_v36():
    v36_on_v35 = to_v36_spelling(_file())
    kinds = [f.kind for f in lint_l5x(v36_on_v35)]
    assert kinds.count("v36_mnemonic_before_v36") == 6
    assert not lint_l5x(to_v36_spelling(_file(major="38", software="38.02")))


def test_lint_refuses_v35_spelling_at_v36():
    kinds = [f.kind for f in lint_l5x(_file(major="38", software="38.02"))]
    assert kinds.count("v35_mnemonic_at_v36") == 6


def test_the_sixteen_renames():
    assert V36_MNEMONIC_ALIASES == {
        "EQ": "EQU", "NE": "NEQ", "GT": "GRT", "GE": "GEQ", "LT": "LES", "LE": "LEQ",
        "MOVE": "MOV", "LIMIT": "LIM", "SQRT": "SQR", "TRUNC": "TRN", "EXPT": "XPY",
        "ACOS": "ACS", "ASIN": "ASN", "ATAN": "ATN", "TO_BCD": "TOD", "BCD_TO": "FRD",
    }
    rung = "<Text><![CDATA[MOV(A,B)LIM(0,A,9)OTE(C);TOD(A,B)XIC(T.MOV)OTE(D);]]></Text>"
    assert to_v36_spelling(rung) == (
        "<Text><![CDATA[MOVE(A,B)LIMIT(0,A,9)OTE(C);TO_BCD(A,B)XIC(T.MOV)OTE(D);]]></Text>")


def test_l9_shell_matches_the_real_exports():
    l5x = build_l5x(target_name="PlatNineShell", tags_xml="", processor_type="1756-L908TS",
                    major_rev="38", software_revision="38.02", **{
                        k: v for k, v in with_baseline(stations=10).items() if k != "tags_xml"})
    root = ET.fromstring(l5x)
    ctl = root.find("Controller")
    assert ctl.get("EtherNetIPMode") == "A1/A2: Dual-IP"
    assert re.fullmatch(r"\{[0-9A-F-]{36}\}", ctl.get("DataExchangeId"))
    assert ctl.find("SafetyInfo").get("SafetyEnabled") == "false"
    assert ctl.find("OpcUaInfo") is not None and ctl.find("DataLogs") is None
    local = ctl.find("Modules/Module[@Name='Local']")
    assert local.get("ProductCode") == "319"
    assert [p.get("Id") for p in local.iter("Port")] == ["1", "3", "4"]
    ethernet_parents = {m.get("ParentModPortId") for m in ctl.iter("Module")
                        if m.get("ParentModule") == "Local" and m.get("Name") != "Local"}
    assert ethernet_parents == {"4"}


def test_l9_refused_below_v38():
    with pytest.raises(ValueError):
        build_l5x(target_name="PlatNineOld", tags_xml="", processor_type="1756-L908TS")


def test_data_exchange_id_is_v38_only_and_stable():
    assert "DataExchangeId" not in _file()
    assert _file("38", "38.02").count("DataExchangeId") == 1
    a = re.search(r'DataExchangeId="([^"]+)"', _file("38", "38.02")).group(1)
    b = re.search(r'DataExchangeId="([^"]+)"', _file("38", "38.02")).group(1)
    assert a == b
