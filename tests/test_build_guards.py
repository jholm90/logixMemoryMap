"""Guards for build failures that have already happened once.

Each test here pins a defect that shipped to a capture run after it had been
diagnosed, because the diagnosis lived in a comment instead of a check:

  * 2198 -ERS3 drives with no <ExtendedProperties> ConfigID -> Studio makes a
    `:SI` safety tag and fails Build on a standard controller.
  * ALMD with 7 operands -> "Invalid number of arguments for instruction".

The last three tests run over the batch waiting for capture -- every committed
generated file with no conversion record -- so a file that would fail one of
these checks -- or below the realism floor -- cannot be handed over.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from sample_gen.gen_module_motion import _drive_module_xml, bus_supply_with_converter  # noqa: E402
from sample_gen.lint import lint_l5x  # noqa: E402
from sample_gen.builders import rung_xml  # noqa: E402
from sample_gen.wrapper import build_l5x  # noqa: E402

ERS3 = ("2198-D012-ERS3", "2198-D020-ERS3", "2198-D032-ERS3", "2198-D057-ERS3",
        "2198-S086-ERS3", "2198-S130-ERS3")


def _kinds(l5x: str) -> set[str]:
    return {f.kind for f in lint_l5x(l5x)}


def _drive_file(drive_xml: str) -> str:
    supply, _converter = bus_supply_with_converter()
    return build_l5x(target_name="Guard", tags_xml="", extra_modules_xml=supply + "\n" + drive_xml)


@pytest.mark.parametrize("catalog", ERS3)
def test_proven_drive_block_passes(catalog):
    assert "kinetix_drive_missing_configid" not in _kinds(
        _drive_file(_drive_module_xml("Drv1", catalog, "false", address="192.168.1.20")))


@pytest.mark.parametrize("catalog", ERS3)
def test_drive_without_configid_is_refused(catalog):
    xml = _drive_module_xml("Drv1", catalog, "false", address="192.168.1.20")
    stripped = re.sub(r"<ExtendedProperties>.*?</ExtendedProperties>\s*", "", xml, flags=re.S)
    assert "kinetix_drive_missing_configid" in _kinds(_drive_file(stripped))


def test_module_tables_carry_only_proven_drive_blocks():
    from sample_gen.gen_module_sweep import _MODULE_CHAINS
    from sample_gen.gen_module_sweep_variants import _MODULE_VARIANTS
    blocks = [xml for c, (xml, _s, _n) in _MODULE_CHAINS.items() if c in ERS3]
    blocks += [xml for c, v in _MODULE_VARIANTS.items() if c in ERS3 for _l, xml, _s, _n in v]
    assert blocks, "no -ERS3 entries found; the guard is checking nothing"
    assert all("<ConfigID>" in xml for xml in blocks)
    assert all("Safety" not in label for c, v in _MODULE_VARIANTS.items() if c in ERS3
               for label, *_ in v)


@pytest.mark.parametrize("call,refused", [
    ("ALMD(Alm1,1,1,0,0);", False),
    ("ALMD(Alm1,AlmProgAck,AlmProgReset,AlmProgDisable,AlmProgEnable,0,0);", True),
])
def test_almd_operand_count(call, refused):
    tags = '<Tag Name="Alm1" TagType="Base" DataType="ALARM_DIGITAL" ExternalAccess="Read/Write"/>'
    kinds = _kinds(build_l5x(target_name="Guard", tags_xml=tags, extra_rungs_xml=rung_xml(0, call)))
    assert ("native_instruction_arg_count" in kinds) is refused


def _waiting_batch() -> list[Path]:
    """Committed generated L5X files with no conversion record and no capture --
    what the next capture run will pick up. A file made in Studio and read by
    hand has a capture but never passes through the converter."""
    seen = set()
    with open(REPO_ROOT / "samples" / "convert_log.csv", newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            seen.add(Path((row.get("l5x_path") or "").replace("\\", "/")).name)
    with open(REPO_ROOT / "samples" / "captures.csv", newline="", encoding="utf-8-sig") as f:
        seen |= {row["sample_id"] + ".L5X" for row in csv.DictReader(f)
                 if (row.get("actual_bytes") or "").strip()}
    return sorted(p for p in (REPO_ROOT / "samples" / "generated").rglob("*.L5X")
                  if p.name not in seen)


def test_waiting_batch_is_lint_clean():
    dirty = {p.name: sorted(_kinds(p.read_text(encoding="utf-8-sig"))) for p in _waiting_batch()}
    assert not {n: k for n, k in dirty.items() if k}


def test_waiting_batch_meets_the_realism_floor():
    """Every file waiting for capture: >= 5 I/O nodes, >= 25% fill, no output
    bit written twice (lint.realism_findings). Fill is read from the engine's
    entries even where it reports an unsized item, which can only under-count."""
    import xml.etree.ElementTree as ET
    from l5x_memory_analyzer.sizing.constants import load_memory_model
    from l5x_memory_analyzer.sizing.report import build_report
    from sample_gen.lint import realism_findings
    model = load_memory_model()
    below = {}
    for p in _waiting_batch():
        text = p.read_text(encoding="utf-8-sig")
        entries, _errors = build_report(ET.fromstring(text), model)
        kinds = sorted(f.kind for f in realism_findings(text, sum(e.bytes for e in entries)))
        if kinds:
            below[p.name] = kinds
    assert not below


def test_waiting_batch_kinetix_blocks_are_proven():
    from check_proven_blocks import check, proven_blocks
    kinetix = [p for p in _waiting_batch()
               if "2198-" in p.read_text(encoding="utf-8-sig", errors="ignore")]
    if not kinetix:
        pytest.skip("no Kinetix file waiting for capture")
    assert check(kinetix, proven_blocks()) == []
