"""Pins the standard-side laws wired from batch A (2026-10-21) against the controller.

Each check differences two captured files and requires the engine's difference to equal
the controller's (samples/captures.csv). The files are rebuilt from their generators and
must hash identically to the files the controller measured, date stamps aside
(tests/captured_file_hashes.json), so a generator that drifts fails here instead of being
compared against a reading of other content.

OQ-STSHAPE: every clean stshape_* file against stshape_n00, to the byte. OQ-MODREPEAT: each
catalog's further copies against its first, to the byte, and the 1756-IF8 / OF8 per-copy
cost from the per-channel configuration law alone within 50 bytes a copy.
"""

from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import replace
from functools import lru_cache
from pathlib import Path

import pytest

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report
from sample_gen.manifest_store import load_manifest

HASHES = json.loads((Path(__file__).parent / "captured_file_hashes.json").read_text())
_DATES = re.compile(rb'(ExportDate|ProjectCreationDate|LastModifiedDate)="[^"]*"')

ST_SHAPES = [
    "assign400", "member400", "scalarmember400", "vidx_dst400", "vidx_both400", "vidx_member400",
    "vidx_bymember400", "vidx_offset400", "real400", "real_member400", "real_mul400", "bool_lit400",
    "bool_copy400", "bool_not400", "bool_and400", "bool_cmp400", "if_bool200", "if_cmp200", "if_eq200",
    "if_cmptag200", "if_and200", "if_and3_200", "if_or200", "if_not200", "if_range200", "if_real200",
    "if_member200", "if_vidx200", "if_two200", "if_else200", "if_nested200", "cop200", "cop_vidx200",
    "for_lit50", "for_tag50", "for_vidx50", "cmt400",
]
MODREP = ["1732e_ib16m12r_a", "1732e_ob16m12r_a", "1756_if8_a", "1756_of8_b", "843e_mipxxbax_a",
          "ex260_sen1_a", "ex260_sen3_a", "powerflex_525_eenet", "powerflex_755_eenet"]


@lru_cache(maxsize=None)
def _actual() -> dict[str, int]:
    return {r["sample_id"]: int(r["actual_bytes"]) for r in load_manifest() if r.get("actual_bytes")}


@pytest.fixture(scope="module")
def built(regenerate):
    root = regenerate("gen_st_shapes", "gen_module_repeat")

    def _path(sample_id: str) -> Path:
        path = next(root.rglob(f"{sample_id}.L5X"))
        body = _DATES.sub(rb'\1=""', path.read_bytes().replace(b"\r\n", b"\n"))
        assert hashlib.sha256(body).hexdigest() == HASHES[sample_id]["sha256_dates_blanked"], (
            f"{sample_id}: the generator no longer reproduces the captured file")
        return path

    return _path


def _engine(path: Path, model=None) -> int:
    if model is None:
        return _engine_default(path)
    return sum(e.bytes for e in build_report(ET.parse(path).getroot(), model)[0])


@lru_cache(maxsize=None)
def _engine_default(path: Path) -> int:
    """The shared control files are priced once, not once per test."""
    return sum(e.bytes for e in build_report(ET.parse(path).getroot(), load_memory_model())[0])


@pytest.mark.parametrize("shape", ST_SHAPES)
def test_each_st_shape_costs_what_the_controller_measured(built, shape):
    sid, ctl = f"stshape_{shape}", "stshape_n00"
    engine = _engine(built(sid)) - _engine(built(ctl))
    assert engine == _actual()[sid] - _actual()[ctl], sid


@pytest.mark.parametrize("slug", MODREP)
def test_each_further_copy_costs_its_measured_repeat(built, slug):
    first, second, fourth = (f"modrep_{slug}_n{n:02d}" for n in (1, 2, 4))
    engine = [_engine(built(s)) for s in (first, second, fourth)]
    real = [_actual()[s] for s in (first, second, fourth)]
    assert engine[1] - engine[0] == real[1] - real[0], slug
    assert engine[2] - engine[1] == real[2] - real[1], slug


@pytest.mark.parametrize("slug", ["1756_if8_a", "1756_of8_b"])
def test_per_channel_configuration_alone_prices_a_further_specialty_card(built, slug):
    """With its own repeat rate removed, a 1756-IF8 / OF8 further copy priced by the type
    sharing law and its per-channel configuration (2.2 x its packed bytes) lands within 50
    bytes of the controller; without the configuration term it read 432 / 744 under."""
    m = load_memory_model()
    mo = m.module_overhead_by_catalog
    catalog = {"1756_if8_a": "1756-IF8/A", "1756_of8_b": "1756-OF8/B"}[slug]
    blind = replace(m, module_overhead_by_catalog=replace(
        mo, repeat_by_catalog={k: v for k, v in mo.repeat_by_catalog.items() if k != catalog}))
    first, fourth = f"modrep_{slug}_n01", f"modrep_{slug}_n04"
    per_copy_engine = (_engine(built(fourth), blind) - _engine(built(first), blind)) / 3
    per_copy_real = (_actual()[fourth] - _actual()[first]) / 3
    assert abs(per_copy_engine - per_copy_real) <= 50, (slug, per_copy_engine, per_copy_real)
