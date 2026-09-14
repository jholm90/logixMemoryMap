"""An identifier's own NAME costs bytes (OQ-IDENTNAMELEN).

8 bytes per whole 8 characters -- a STEP, the same form the project already uses
for tag, UDT and AOI-definition names. Shared by Program names, JSR target
routine names and ordinary routine names.

CORRECTED 2026-09-14 (segment 9) from a three-regime ramp (0 below 5 characters,
2/char to 8, then 1 x len). That ramp was anchored at 1/4/8/16/32/40 and this law
agrees with it at every one of those anchors; it was wrong only across the
interval it had to interpolate, which its own entry called "an interpolation
between two anchors rather than measured". `identnamelen_*` is the sweep that
measured it: 19 of 19 rows byte-exact, against 7 of 19 before.

These tests pin the law's SHAPE rather than restating its constants, pin that a
routine's name follows the same law as a program's, and pin the n-1 convention
each one uses -- per project for programs, PER PROGRAM for routines, which is the
one thing the two arms of the sweep disagreed about until it was measured.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report


@pytest.fixture
def model():
    return load_memory_model()


def test_a_name_shorter_than_one_bucket_is_free(model):
    """identnamelen_prog_c{01..07} all read the same total, and
    identnamelen_rtn_c01/_c04 are exact at zero."""
    nl = model.identifier_name_length
    for length in range(0, nl.bucket_chars):
        assert nl.bytes_for("x" * length) == 0, length


def test_the_cost_is_whole_buckets_only(model):
    """The step, which is what the ramp got wrong: 9 through 15 characters cost
    the same as 8, not 9 through 15. identnamelen_prog_c{08..12} are five files
    at five different lengths reading one identical total."""
    nl = model.identifier_name_length
    for length in (8, 16, 32, 40):
        assert nl.bytes_for("x" * length) == nl.bucket_bytes * (length // nl.bucket_chars)
    assert nl.bytes_for("x" * 8) == nl.bytes_for("x" * 12) == nl.bytes_for("x" * 15)
    assert nl.bytes_for("x" * 16) > nl.bytes_for("x" * 15)


def test_it_matches_the_measured_points(model):
    """The captured sweep, per identifier, both arms."""
    nl = model.identifier_name_length
    measured = {1: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 8, 9: 8, 12: 8, 16: 16, 32: 32, 40: 40}
    for length, expected in measured.items():
        assert nl.bytes_for("x" * length) == expected, length


def test_cost_never_decreases_with_length(model):
    nl = model.identifier_name_length
    values = [nl.bytes_for("x" * n) for n in range(0, 41)]
    assert values == sorted(values)


def _project(program_names: list[str], routine_name: str = "Main") -> ET.Element:
    programs = "".join(
        f'''<Program Name="{name}" Class="Standard">
              <Routines><Routine Name="{routine_name}" Type="RLL"><RLLContent/></Routine></Routines>
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


def _one_program(routine_names: list[str]) -> ET.Element:
    routines = "".join(
        f'<Routine Name="{name}" Type="RLL"><RLLContent/></Routine>'
        for name in routine_names
    )
    return ET.fromstring(f"""
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test" ProcessorType="1756-L81E" MajorRev="35">
        <DataTypes/><AddOnInstructionDefinitions/><Tags/><Modules/>
        <Programs><Program Name="Main" Class="Standard">
          <Routines>{routines}</Routines>
        </Program></Programs>
        <Tasks><Task Name="MainTask" Type="CONTINUOUS">
          <ScheduledPrograms><ScheduledProgram Name="Main"/></ScheduledPrograms>
        </Task></Tasks>
      </Controller>
    </RSLogix5000Content>
    """)


def test_a_routine_name_costs_the_same_as_a_program_name(model):
    """Ordinary routines were charged NOTHING before 2026-09-14 -- only JSR
    targets were, via jsr_target_declaration. identnamelen_rtn_* holds 10
    non-JSR routines and reads 8 bytes per routine per 8-character bucket."""
    nl = model.identifier_name_length
    short = _shell_bytes(_one_program(["Ab", "Cd"]), model)
    long = _shell_bytes(_one_program(["Ab", "C" * 40]), model)
    assert long - short == nl.bytes_for("C" * 40)


def test_the_first_routine_in_EACH_program_is_free(model):
    """PER PROGRAM, not per project -- the one thing the two arms of the sweep
    disagreed about. identnamelen_rtn_* puts 11 routines in ONE program and
    charges 10 of them; identnamelen_prog_* puts 11 routines across 11 programs,
    one each, and charges NONE of them. A flat project-wide n-1 fits the first
    and over-charges the second by exactly 80 on all twelve files."""
    nl = model.identifier_name_length
    long_name = "R" * 40
    # One long routine per program, two programs: both are firsts, both free.
    spread = _shell_bytes(_project(["Pa", "Pb"], routine_name="Rb"), model)
    spread_long = _shell_bytes(_project(["Pa", "Pb"], routine_name=long_name), model)
    assert spread_long == spread, "a program's only routine must be free at any name length"
    # Both in one program: the second one pays.
    stacked = _shell_bytes(_one_program(["Main", long_name]), model)
    stacked_short = _shell_bytes(_one_program(["Main", "Rb"]), model)
    assert stacked - stacked_short == nl.bytes_for(long_name)
