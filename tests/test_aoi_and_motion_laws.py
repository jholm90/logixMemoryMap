"""Pins the laws wired from the 2026-10-04 capture batch against the controller.

Each check differences two captured files and requires the engine's difference
to equal the controller's (samples/captures.csv), so a later change to any
constant behind these laws fails here rather than silently on the real set.

The captured L5X files are no longer kept in the repository. Each one is rebuilt
from its generator (tests/conftest.py) and must hash identically to the file
the controller measured, date stamps aside (tests/captured_file_hashes.json,
taken from the committed files before they were deleted). A generator that
drifts fails here instead of being compared against a reading of other content.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from l5x_memory_analyzer.parser.logic import inout_operand_instruction_count  # noqa: E402
from l5x_memory_analyzer.sizing.constants import load_memory_model  # noqa: E402
from l5x_memory_analyzer.sizing.report import build_report  # noqa: E402
from sample_gen.manifest_store import load_manifest  # noqa: E402

HASHES = json.loads((Path(__file__).parent / "captured_file_hashes.json").read_text())
GENERATORS = ("gen_motion_literals", "gen_block_string", "gen_aoi_literal_args", "gen_aoi_complex",
              "gen_aoi_internal_shape", "gen_aoi_structure", "gen_aoi_internal_shape_isolation")
_DATES = re.compile(rb'(ExportDate|ProjectCreationDate|LastModifiedDate)="[^"]*"')


@lru_cache(maxsize=None)
def _actual() -> dict[str, int]:
    return {r["sample_id"]: int(r["actual_bytes"]) for r in load_manifest() if r.get("actual_bytes")}


@pytest.fixture(scope="module")
def residual(regenerate):
    root = regenerate(*GENERATORS)
    cache: dict[str, int] = {}

    def _residual(sample_id: str) -> int:
        if sample_id not in cache:
            path = next(root.rglob(f"{sample_id}.L5X"))
            body = _DATES.sub(rb'\1=""', path.read_bytes().replace(b"\r\n", b"\n"))
            assert hashlib.sha256(body).hexdigest() == HASHES[sample_id]["sha256_dates_blanked"], (
                f"{sample_id}: the generator no longer reproduces the captured file")
            entries, _ = build_report(ET.parse(path).getroot(), load_memory_model())
            cache[sample_id] = _actual()[sample_id] - sum(e.bytes for e in entries)
        return cache[sample_id]

    return _residual


PAIRS = [
    # OQ-MOTIONLIT: literal law on MAJ / MAPC / MCCP / MAG, weights without literals.
    ("motlit_maj_ilit", "motlit_n00"), ("motlit_maj_tag", "motlit_n00"),
    ("motlit_mapc_ilit", "motlit_n00"), ("motlit_mccp_flit", "motlit_n00"),
    ("motlit_mag_ilit", "motlit_n00"),
    # OQ-BLOCKSTR: FLL of an integer literal into REAL.
    ("blkstr_fll_real_l10", "blkstr_n00"),
    # OQ-AOILITARG: REAL Input parameter given an integer literal, 0, a float, a DINT tag.
    ("aoilit_r_ilit5", "aoilit_tag"), ("aoilit_r_ilit0", "aoilit_tag"),
    ("aoilit_r_flit", "aoilit_tag"), ("aoilit_r_dint", "aoilit_tag"),
    # OQ-AOICOMPLEX: InOut reads, InOut word writes, nested AOI call.
    ("aoicx_bits", "aoicx_n00"), ("aoicx_cmp", "aoicx_n00"), ("aoicx_jmp", "aoicx_n00"),
    ("aoicx_gsv", "aoicx_n00"), ("aoicx_nested", "aoicx_n00"),
    ("aoiint_inout", "aoiint_local"), ("aoiint_axis", "aoiint_local"),
    # OQ-AOIROUTINES: scan-mode routines beyond Logic.
    ("aoiint_eif", "aoiint_local"),
]


@pytest.mark.parametrize("sample, control", PAIRS)
def test_engine_difference_matches_the_controller(residual, sample, control):
    assert abs(residual(sample) - residual(control)) <= 8


@pytest.mark.parametrize("sample, expected", [
    ("aoistr_routines_n1", 0), ("aoistr_routines_n2", 4), ("aoistr_routines_n3", 0),
    ("aoierr_tworoutine", 4),
])
def test_extra_aoi_routines_are_exact(residual, sample, expected):
    assert residual(sample) == expected


def test_inout_counter_reads_bits_and_sources_but_not_word_destinations():
    io = frozenset({"Srv", "Ax"})
    rungs = [
        "XIC(Srv.B0)OTE(Srv.B1);",           # bit read + bit write: 2
        "MOV(5,Srv.D0);",                    # word write into InOut: 0
        "MOV(Srv.D1,LoD);",                  # read: 1
        "GRT(Srv.R0,Srv.R1)OTE(LoB);",       # one instruction, two reads: 1
        "GSV(Axis,Ax,ConversionConstant,LoR);",  # GSV instance: 0
        "MSO(Ax,Srv.Mso);",                  # motion on InOut axis: 1
    ]
    assert inout_operand_instruction_count(rungs, io) == 5
