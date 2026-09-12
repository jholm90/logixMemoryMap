"""An identifier's own NAME costs bytes (OQ-IDENTNAMELEN, wired 2026-09-12).

Two independent sweeps -- JSR target routine names and Program names, 10
identifiers per file at lengths 4/8/16/32/40 -- returned the identical
per-identifier cost, which is why one shared law serves both. These tests pin
the law's SHAPE (a floor below 8 characters, then exactly 1 byte per
character) rather than restating its constants, and pin that both call sites
use the same one.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report


@pytest.fixture
def model():
    return load_memory_model()


def test_names_at_or_below_the_free_length_cost_nothing(model):
    """Measured: a 4-character name costs 0, not 4. Without this floor the
    len=4 row of both sweeps is over-predicted."""
    nl = model.identifier_name_length
    for length in range(0, nl.free_chars + 1):
        assert nl.bytes_for("x" * length) == 0, length


def test_above_the_crossover_the_cost_is_the_character_count(model):
    """1 byte per character, no bucketing -- the measured 8/16/32/40 points."""
    nl = model.identifier_name_length
    for length in (9, 16, 32, 40):
        assert nl.bytes_for("x" * length) == length * nl.per_char_above_limit


def test_the_two_pieces_meet_at_the_crossover(model):
    """The sub-crossover interval is an interpolation between two measured
    anchors; if it ever stops meeting the per-character line at the crossover,
    one of the two pieces has been edited without the other."""
    nl = model.identifier_name_length
    at_limit = "x" * nl.doubled_rate_limit
    assert (nl.sub_limit_rate * (nl.doubled_rate_limit - nl.free_chars)
            == nl.per_char_above_limit * nl.doubled_rate_limit)
    assert nl.bytes_for(at_limit) == nl.per_char_above_limit * nl.doubled_rate_limit


def test_cost_never_decreases_with_length(model):
    nl = model.identifier_name_length
    values = [nl.bytes_for("x" * n) for n in range(0, 41)]
    assert values == sorted(values)


def _project(program_names: list[str]) -> ET.Element:
    programs = "".join(
        f'''<Program Name="{name}" Class="Standard">
              <Routines><Routine Name="Main" Type="RLL"><RLLContent/></Routine></Routines>
            </Program>'''
        for name in program_names
    )
    return ET.fromstring(f"""
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test" ProcessorType="1756-L81E" MajorRev="35">
        <DataTypes/><AddOnInstructionDefinitions/><Tags/><Modules/>
        <Programs>{programs}</Programs>
        <Tasks><Task Name="MainTask" Type="CONTINUOUS">
          <ScheduledPrograms>{"".join(f'<ScheduledProgram Name="{n}"/>' for n in program_names)}</ScheduledPrograms>
        </Task></Tasks>
      </Controller>
    </RSLogix5000Content>
    """)


def _shell_bytes(root: ET.Element, model) -> int:
    entries, _ = build_report(root, model)
    return next(e.bytes for e in entries if e.path == "task_program_shell")


def test_extra_program_names_are_charged_and_the_first_is_not(model):
    """program_extra follows an n-1 convention because the first program is
    inside the fitted baseline; its NAME has to follow the same convention or
    a single-program file shifts."""
    nl = model.identifier_name_length
    one_long = _shell_bytes(_project(["A" * 40]), model)
    one_short = _shell_bytes(_project(["Ab"]), model)
    assert one_long == one_short

    two_short = _shell_bytes(_project(["Ab", "Cd"]), model)
    two_long = _shell_bytes(_project(["Ab", "C" * 40]), model)
    assert two_long - two_short == nl.bytes_for("C" * 40)
