"""Safety round 2 (OQ-SAFETYPARTITION, TASKS 0u): its roster and its builder."""

from __future__ import annotations

import re

from sample_gen import gen_safety_partition as G
from sample_gen import gen_safety_round2 as R

_DATES = re.compile(r'(ExportDate|ProjectCreationDate|LastModifiedDate)="[^"]*"')


def test_the_roster_is_74_new_files():
    ids = [sid for sid, _, _ in R.plan()]
    assert len(ids) == len(set(ids)) == 74
    assert not set(ids) & {sid for sid, _, _ in G.plan()}
    assert all(sid.startswith("safe_") for sid in ids)


def test_every_round2_difference_names_files_in_the_roster_or_round1():
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "safety_eval", Path(__file__).resolve().parent.parent / "scripts" / "safety_eval.py")
    ev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ev)
    known = {sid for sid, _, _ in R.plan()} | {sid for sid, _, _ in G.plan()}
    for _, a, b, _ in ev.ROUND2_DIFFS:
        assert a in known and b in known, (a, b)


def test_one_program_one_routine_is_round_1s_builder_byte_for_byte():
    tags = [G._program_safety_tag(f"SafeDint_{i:03d}", "DINT") for i in range(50)]
    a = G.build("safe_tag_dint_50_prog", safety_tags=tags)
    b = R.build("safe_tag_dint_50_prog", programs=[R.main_program(tags)])
    assert _DATES.sub("", a) == _DATES.sub("", b)


def test_every_safety_program_is_scheduled_in_the_safety_task():
    task = R._task(["SafetyProgram", "SafetyPrg02"])
    assert task.count("<ScheduledProgram ") == 2 and 'Class="Safety"' in task
    assert R._task(["SafetyProgram"]) == G._SAFETY_TASK


def test_both_scopes_are_covered_for_every_tag_shape():
    ids = {sid for sid, _, _ in R.plan()}
    for label, _, _ in R.ARRAY_SHAPES:
        assert {f"safe_arr_{label}_ctl", f"safe_arr_{label}_prog"} <= ids
    for typ in R.STRUCT_TYPES:
        assert {f"safe_struct_{typ.lower()}_ctl", f"safe_struct_{typ.lower()}_prog"} <= ids
    for size in ("s", "l"):
        assert {f"safe_udt_{size}_ctl20", f"safe_udt_{size}_prog20"} <= ids


# --- round 3, logic (TASKS 0v) -----------------------------------------------------------

from sample_gen import gen_safety_round3 as R3


def test_round_3_is_78_new_files_on_one_pool():
    plan = R3.plan()
    ids = [sid for sid, _, _ in plan]
    assert len(ids) == len(set(ids)) == 78
    assert not set(ids) & ({sid for sid, _, _ in R.plan()} | {sid for sid, _, _ in G.plan()})
    pool = R3._pool()
    for sid, _, kw in plan:
        if sid.startswith("safe_lg_"):
            assert kw["programs"][0][1] == pool, sid


def test_no_round_3_rung_writes_an_output_bit_twice():
    for sid, _, kw in R3.plan():
        if "programs" not in kw:
            continue
        rungs = kw["programs"][0][2][0][1]
        writes = [m for r in rungs for m in re.findall(r"(?:OTE|OTL|OTU)\((\w+\[\d+\]|\w+)\)", r)]
        writes += [m for r in rungs for m in re.findall(r"OS[RF]\(\w+\[\d+\],(\w+\[\d+\])\)", r)]
        assert len(writes) == len(set(writes)), sid


# --- the safety-routine palette (lint: instruction_not_in_safety_palette) ------------------

from sample_gen.lint import lint_l5x
from sample_gen.wrapper import build_l5x


def _safety_file(rungs: list[str]) -> str:
    return build_l5x("SafeLint", tags_xml="", processor_type=G.PROCESSOR, safety_level="SIL2",
                     extra_programs_xml=R._program("SafetyProgram", [R.prog_tag("Pv", "REAL"), R.prog_tag("Cv", "REAL"),
                                                                     R.prog_tag("Da", "DINT"), R.prog_tag("Db", "DINT"),
                                                                     R.prog_tag("Qo", "BOOL")],
                                                   [("MainRoutine", rungs)]),
                     extra_tasks_xml=R._task(["SafetyProgram"]))


def _palette_findings(rungs: list[str]) -> list:
    return [f for f in lint_l5x(_safety_file(rungs)) if f.kind == "instruction_not_in_safety_palette"]


def test_an_instruction_outside_the_safety_palette_is_refused():
    assert _palette_findings(["SIN(Pv,Cv);"])
    assert _palette_findings(["CPS(Da,Db,1);"])


def test_every_ordinary_palette_instruction_and_its_v36_spelling_is_accepted():
    assert not _palette_findings(["NEQ(Da,Db)OTE(Qo);", "SQR(Pv,Cv);", "MOV(Da,Db);"])
    assert not _palette_findings(["NE(Da,Db)OTE(Qo);", "SQRT(Pv,Cv);"])


def test_the_palette_is_58_ordinary_instructions_without_pid():
    from sample_gen.lint import _SAFETY_ROUTINE_ORDINARY
    assert len(_SAFETY_ROUTINE_ORDINARY) == 58
    assert "PID" not in _SAFETY_ROUTINE_ORDINARY and "NEQ" in _SAFETY_ROUTINE_ORDINARY


def test_the_safety_aoi_is_class_safety_and_lints_clean():
    xml, storage = R3.safety_aoi(10)
    assert 'Name="SafeAoiA" Class="Safety"' in xml
    assert [m.name for m in storage][:4] == ["EnableIn", "EnableOut", "InA", "OutQ"]
    for sid, _, kw in R3.plan():
        if sid in ("safe_aoi_call_20", "safe_aoi_inst_ctl20"):
            assert not lint_l5x(R.build(sid, **kw)), sid
