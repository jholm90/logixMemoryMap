"""A standalone atomic tag's data is a fixed 4-byte slot. OQ-SHELLCONST.

Six bare tag-count files -- 50 tags each, one type per file, no logic and
nothing else -- give -3.00/tag on SINT, -2.00 on INT, +4.00 on LINT and exactly 0
on BOOL/DINT/REAL. All six fit one rule with zero residual: the slot is 4 bytes.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

MODEL = load_memory_model()


def _root(tags_xml: str) -> ET.Element:
    return ET.fromstring(f"""
    <RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="35.05">
      <Controller Name="T" ProcessorType="1756-L81E" MajorRev="35" MinorRev="11">
        <DataTypes/><AddOnInstructionDefinitions/>
        <Tags>{tags_xml}</Tags>
        <Programs/><Tasks/>
      </Controller>
    </RSLogix5000Content>""")


def _tag(name: str, data_type: str, dims: str = "") -> str:
    dim = f' Dimensions="{dims}"' if dims else ""
    return (f'<Tag Name="{name}" TagType="Base" DataType="{data_type}"{dim}'
            f' Radix="Decimal" Constant="false" ExternalAccess="Read/Write"/>')


def _tag_bytes(name: str, data_type: str, dims: str = "") -> int:
    entries, _errors = build_report(_root(_tag(name, data_type, dims)), MODEL)
    return next(e.bytes for e in entries if e.path.endswith(name))


def test_every_standalone_atomic_type_gets_the_same_slot() -> None:
    """SINT (1 byte) and LINT (8) land on the same total as DINT (4): the slot
    is the type-independent part, and the per-tag overhead on top is identical
    for tags of the same name length."""
    sizes = {t: _tag_bytes("Probe", t) for t in ("SINT", "INT", "DINT", "REAL", "LINT")}
    assert len(set(sizes.values())) == 1, sizes


def test_sint_is_padded_up_not_charged_one_byte() -> None:
    assert _tag_bytes("Probe", "SINT") == _tag_bytes("Probe", "DINT")


def test_lint_is_not_charged_its_eight_bytes() -> None:
    """+4.00/tag on type_lint_50tag: a LINT tag is reported in a 4-byte slot
    rather than the 8 its value needs."""
    assert _tag_bytes("Probe", "LINT") == _tag_bytes("Probe", "DINT")


def test_arrays_keep_element_size_times_count() -> None:
    """Deliberately untouched: every array sweep in the corpus confirms
    element_size x count, so the slot is a per-TAG rule and must not leak into
    array sizing. A SINT[100] must stay far smaller than a DINT[100]."""
    sint = _tag_bytes("Arr", "SINT", "100")
    dint = _tag_bytes("Arr", "DINT", "100")
    assert dint - sint == 300


def test_the_typesweep_pool_now_nets_to_zero() -> None:
    """The 69 typesweep_* files sat at exactly -5 because their pool is 5 tags
    each of SINT/INT/DINT/LINT/REAL: -15 -10 +0 +20 +0. Under the slot rule the
    five types contribute identically, so that pool's net error is 0."""
    pool = "".join(
        _tag(f"T{t[0]}{i}", t)
        for t in ("SINT", "INT", "DINT", "LINT", "REAL") for i in range(5)
    )
    entries, _errors = build_report(_root(pool), MODEL)
    tag_entries = [e for e in entries if e.category == "controller_tag"]
    assert len(tag_entries) == 25
    assert len(set(e.bytes for e in tag_entries)) == 1
