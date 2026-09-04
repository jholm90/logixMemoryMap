"""Partial exports must not be sized as whole projects.

James, 2026-09-04: "Anything that's not a controller export can not use the
prices sir base load, but rungs, routines and programs might contain
controller tags."

Every assertion here is pinned against a REAL Studio 5000 export in
samples/local/Template/, not a hand-written fixture -- the exact shapes that
broke the old code (a rung export whose containing Routine element carries
no Type attribute; a target routine sitting inside a context program) are
things this project would not have invented on its own.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from l5x_memory_analyzer.parser.export_scope import (
    context_names,
    detect_export_scope,
    split_totals,
)
from l5x_memory_analyzer.parser.logic import parse_rll_routines, routine_language
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

TEMPLATE = Path(__file__).resolve().parent.parent / "samples" / "local" / "Template"
WHOLE = (Path(__file__).resolve().parent.parent / "samples" / "local" / "L5X_Samples"
         / "MurrayBros_20260122r1.L5X")
MODEL = load_memory_model()

_real = pytest.mark.skipif(not TEMPLATE.is_dir(), reason="real sample exports not present")


def _report(path: Path):
    root = ET.parse(path).getroot()
    entries, errors = build_report(root, MODEL)
    scope = detect_export_scope(root)
    return root, entries, errors, scope, split_totals(entries, context_names(root, scope))


@_real
@pytest.mark.parametrize("name,target_type", [
    ("HMILugChain_Program.L5X", "Program"),
    ("Flashers_Routine_RLL.L5X", "Routine"),
    ("Rung11_from_Main.L5X", "Rung"),
    ("SingleSolValve_AOI.L5X", "AddOnInstructionDefinition"),
])
def test_partial_export_gets_no_project_base_load(name, target_type):
    _root, entries, errors, scope, totals = _report(TEMPLATE / name)

    assert scope.target_type == target_type
    assert scope.is_whole_controller is False
    # The bug this replaces: an exported RUNG reported 15,080 bytes, 13,296
    # of which was empty_project_baseline -- a controller's fixed
    # scaffolding, charged to a single rung.
    assert totals["project"] == 0
    assert not [e for e in entries if e.category == "project_baseline"]
    assert not [e for e in entries if e.category == "task_program_shell"]
    # ...and it says so in its own report rather than looking like a project.
    assert [e for e in errors if e.path == "scope/partial_export"]


@_real
def test_whole_controller_export_still_gets_the_base_load():
    """The scope rule must not touch whole-project files -- they are what
    every fitted constant in this model was calibrated against."""
    if not WHOLE.exists():
        pytest.skip("whole-project sample not present")
    _root, entries, _errors, scope, totals = _report(WHOLE)

    assert scope.is_whole_controller is True
    assert totals["context"] == 0
    assert totals["project"] > 0
    assert [e for e in entries if e.category == "project_baseline"]


@_real
def test_rung_export_actually_sizes_its_rung():
    """A rung export's containing Routine carries Use and Name but NO Type
    attribute, so requiring Type=="RLL" parsed the file to zero routines and
    never sized the exported rung -- the entire point of the file."""
    root = ET.parse(TEMPLATE / "Rung11_from_Main.L5X").getroot()

    routine_el = next(el for el in root.iter("Routine"))
    assert routine_el.get("Type") is None
    assert routine_language(routine_el) == "RLL"

    routines = parse_rll_routines(root)
    assert len(routines) == 1
    assert sum(routines[0].instruction_counts.values()) > 0

    _r, _e, _err, _s, totals = _report(TEMPLATE / "Rung11_from_Main.L5X")
    assert totals["target"] > 0


@_real
def test_target_routine_inside_a_context_program_is_target_not_context():
    """Flashers_Routine_RLL.L5X exports one routine out of program
    "Housekeeping". The program is context; the routine is the target. A
    path-prefix rule that only asked "is the program context?" classified
    the target routine as context and reported target=0."""
    _root, _entries, _errors, _scope, totals = _report(TEMPLATE / "Flashers_Routine_RLL.L5X")

    assert totals["target"] > 0
    # It really does carry controller tags along, which is James's point --
    # they are counted, just not as part of the routine itself.
    assert totals["context"] > 0


@_real
def test_every_real_template_export_is_detected_as_partial():
    """No real export in this directory may quietly earn a base load."""
    for path in sorted(TEMPLATE.glob("*.L5X")):
        root = ET.parse(path).getroot()
        scope = detect_export_scope(root)
        assert not scope.is_whole_controller, path.name
        assert scope.contains_context is True, path.name
