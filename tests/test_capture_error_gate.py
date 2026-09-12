"""The step-2b gate must fail, not pass, when an error has nowhere to go.

A gate that can only pass is not a gate. These tests drive
scripts/capture_errors.py's own routing and gate logic directly, because the
failure this step exists to prevent -- an errored capture that nothing points
at -- is invisible unless the check is exercised against a row that breaks it.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _module():
    spec = importlib.util.spec_from_file_location(
        "capture_errors", REPO_ROOT / "scripts" / "capture_errors.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_errored_rows_are_only_those_with_a_nonzero_count() -> None:
    ce = _module()
    rows = [
        {"sample_id": "a", "error_count": ""},
        {"sample_id": "b", "error_count": "0"},
        {"sample_id": "c", "error_count": "3"},
    ]
    assert [r["sample_id"] for r in ce._errored_rows(rows)] == ["c"]


def test_description_names_the_owning_question() -> None:
    """Uses a question with no alias entry: OQ-BLOCKBYTE was the original
    example here and stopped working the day it closed and gained one, which is
    the alias mechanism doing its job rather than a regression."""
    ce = _module()
    row = {"sample_id": "zzz_not_in_owner_map", "description": "see OQ-JSRFOLD", "notes": ""}
    assert ce._owning_questions(row) == ["OQ-JSRFOLD"]


def test_owner_map_prefix_beats_the_description() -> None:
    """An explicit line is a deliberate statement of ownership; a mention in
    prose is incidental. axis_scale_* names OQ-AXISSTRUCT in its description
    and belongs to OQ-AXISMARGINAL."""
    ce = _module()
    row = {"sample_id": "axis_scale_n08_single",
           "description": "... OQ-AXISSTRUCT ...", "notes": ""}
    assert ce._owning_questions(row) == ["OQ-AXISMARGINAL"]


def test_closed_question_alias_redirects_to_its_successor() -> None:
    ce = _module()
    row = {"sample_id": "zzz_not_in_owner_map",
           "description": "built for OQ-STSIZING", "notes": ""}
    assert ce._owning_questions(row) == ["OQ-STEXPR"]


def test_an_unowned_errored_row_has_no_question() -> None:
    ce = _module()
    row = {"sample_id": "zzz_nothing_matches_this", "description": "no question named",
           "notes": ""}
    assert ce._owning_questions(row) == []


def test_never_attempted_file_is_not_a_conversion_failure() -> None:
    """A batch built today has no convert_log row at all. Counting that as a
    failure floods the report with noise and trains people to ignore it."""
    ce = _module()
    rows = [{"sample_id": "brand_new", "l5x_path": "samples/generated/x/never_submitted.L5X"}]
    assert ce._conversion_failures(rows) == []


def test_gate_line_is_matched_with_its_count() -> None:
    ce = _module()
    assert ce._GATE_RE.search("**CAPTURE ERRORS: 42 row(s)** flagged").group(1) == "42"
    assert ce._GATE_RE.search("CAPTURE ERRORS: some rows") is None


def test_live_repository_passes_the_gate() -> None:
    """The real check, against the real manifest: every errored capture in the
    repository is flagged against the question that asked for it."""
    ce = _module()
    assert ce.main([]) == 0
