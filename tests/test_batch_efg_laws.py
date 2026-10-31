"""Pins the laws wired from batches E, F and G (captured 2026-10-31) against the controller.

Each file is rebuilt from its generator, must hash as the file the controller measured, date
stamps aside (tests/captured_file_hashes.json), and the engine's difference against the
batch's control must equal the controller's.

OQ-LDGAPS: thirteen ladder weights, each at 50 and 100 rungs, to the byte. Batch H: the AOI call
from ST at 10 / 50 / 100 calls and the CASE law, to the byte; EVENT from ST against its control. OQ-STINSTR: ST
functions, function-block calls, instruction calls and motion calls, against stinstr_n00, to
16 bytes a file (the array-argument blocks and the motion files carry a fixed 4 to 16 bytes of
tag pricing, the same at every call count). OQ-STEXTENDED: the shapes the engine prices exactly,
JSR parameters from ST included.
"""

from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

import pytest

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report
from sample_gen.manifest_store import load_manifest

HASHES = json.loads((Path(__file__).parent / "captured_file_hashes.json").read_text())
_DATES = re.compile(rb'(ExportDate|ProjectCreationDate|LastModifiedDate)="[^"]*"')

LD = ["atan2", "ln", "std", "lower", "ctd", "lfl", "ddt", "sqi", "sql", "sqo", "eot", "iot", "isinf", "isnan"]
ST_FB = ["ctud", "osri", "osfi", "setd", "resd", "dff", "jkff", "btdt", "mvmt", "scl", "pide", "alm", "intg",
         "pi", "pmul", "scrv", "soc", "updn", "hpf", "lpf", "ntch", "ldlg", "ldl2", "derv", "tot", "d2sd",
         "d3sd", "esel", "hll", "rlim", "sneg", "ssum", "maxc", "minc", "posp", "srtp", "imc", "cc", "mmc",
         "hmibc", "dedt", "fgen", "mave", "mstd", "rmps"]
ST_FN = ["abs", "sqrt", "ln", "log", "sin", "cos", "tan", "asin", "acos", "atan", "deg", "rad", "trunc", "atan2"]
ST_OP = ["pid", "msg", "ssv", "iot", "uid", "tnd", "eot", "swpb", "insert", "mid", "stod", "rtos", "stor",
         "upper", "lower", "srt"]
ST_MO = ["mam", "mah", "mas", "mso", "mrp", "msf", "maw", "mar", "mdr"]
STE_EXACT = ["aoi_p2_10", "aoi_p2_50", "aoi_p2_100", "aoi_p6_50", "case20x5", "case20x10", "case40x5",
             "case20x5else", "casemember20x5",
             "jsr0_50", "jsr3_50", "jsr3lower_50", "tonr_call50", "tonr_dnif50", "concat100", "dtos100",
             "delete100", "find100", "size50", "cop200", "coplower200", "gsv50", "cps50", "ifupper200",
             "iflower200", "dot3_400", "vidxdot3_400", "innerarr400", "amp400"]


@lru_cache(maxsize=None)
def _actual() -> dict[str, int]:
    return {r["sample_id"]: int(r["actual_bytes"]) for r in load_manifest() if r.get("actual_bytes")}


@pytest.fixture(scope="module")
def built(regenerate):
    root = regenerate("gen_ld_gaps", "gen_st_instructions", "gen_st_extended")

    def _path(sample_id: str) -> Path:
        path = next(root.rglob(f"{sample_id}.L5X"))
        body = _DATES.sub(rb'\1=""', path.read_bytes().replace(b"\r\n", b"\n"))
        assert hashlib.sha256(body).hexdigest() == HASHES[sample_id]["sha256_dates_blanked"], (
            f"{sample_id}: the generator no longer reproduces the captured file")
        return path

    return _path


@lru_cache(maxsize=None)
def _engine(path: Path) -> int:
    return sum(e.bytes for e in build_report(ET.parse(path).getroot(), load_memory_model())[0])


def _residual(built, sid: str, ctl: str) -> int:
    return (_actual()[sid] - _actual()[ctl]) - (_engine(built(sid)) - _engine(built(ctl)))


@pytest.mark.parametrize("mn", LD)
@pytest.mark.parametrize("n", [50, 100])
def test_ladder_gap_weights(built, mn, n):
    assert _residual(built, f"ldgap_{mn}_{n}", "ldgap_n00") == 0


@pytest.mark.parametrize("sid", [f"stinstr_fb_{x}" for x in ST_FB] + [f"stinstr_fn_{x}" for x in ST_FN]
                         + [f"stinstr_op_{x}" for x in ST_OP] + [f"stinstr_mo_{x}" for x in ST_MO])
def test_st_calls(built, sid):
    assert abs(_residual(built, sid, "stinstr_n00")) <= 16, sid


@pytest.mark.parametrize("shape", STE_EXACT)
def test_st_extended_shapes_priced_exactly(built, shape):
    assert _residual(built, f"ste_{shape}", "ste_n00") == 0


def test_new_ladder_weights_are_known_and_pinned():
    li = load_memory_model().logic_instructions
    expected = {"ATAN2": 64, "LN": 60, "STD": 116, "LOWER": 84, "LFL": 76, "DDT": 84, "SQI": 48, "SQL": 60,
                "SQO": 56, "EOT": 64, "IOT": 72, "IsINF": 40, "IsNAN": 40, "CTD": 20}
    for mn, w in expected.items():
        assert li.weights[mn] == w, mn


def test_event_from_st_costs_its_ladder_weight(built):
    """Batch H: 50 EVENT calls against the same file without them (the task and its program)."""
    assert _residual(built, "stinstr_op_event", "stinstr_event_n00") == 0

