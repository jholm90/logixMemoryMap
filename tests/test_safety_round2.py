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
