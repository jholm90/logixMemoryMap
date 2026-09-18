"""Confidence must report MEASURED ACCURACY, not a provenance tag.

The old UI printed a provenance tier as if it were a confidence, so every
routine read "0% measured" -- because compiled ladder size can never be
KNOWN, by CLAUDE.md's ground-truth constraint. That says something about
Rockwell's file format, not about this model's error, and it read as "we have
no idea" about numbers that reproduce captures to the byte.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from l5x_memory_analyzer.sizing.confidence import (  # noqa: E402
    PROVENANCE_BAND, band_for_error, instruction_band, rung_band, weakest,
)
from l5x_memory_analyzer.sizing.constants import load_memory_model  # noqa: E402

TABLE = load_memory_model().instruction_accuracy


def test_provenance_ordering_is_unchanged():
    assert weakest("KNOWN", "FITTED") == "FITTED"
    assert weakest("KNOWN", "KNOWN") == "KNOWN"


def test_bands_come_from_the_measured_error():
    assert band_for_error(0.05, 4).key == "MEASURED"
    assert band_for_error(0.5, 4).key == "CLOSE"
    assert band_for_error(3.0, 4).key == "APPROX"
    assert band_for_error(40.0, 4).key == "UNVERIFIED"


def test_no_samples_is_unverified_not_confident():
    """Absence of evidence must never read as a bound."""
    assert band_for_error(None, 0).key == "UNVERIFIED"
    assert band_for_error(0.0, 0).key == "UNVERIFIED"
    assert instruction_band("NOSUCHOPCODE", TABLE).key == "UNVERIFIED"


def test_an_unpriced_instruction_is_not_merely_uncertain():
    """Its bytes are absent from the total, which is a different claim."""
    assert instruction_band("MOV", TABLE, has_weight=False).key == "UNPRICED"


def test_scaffold_instructions_are_measured_not_unknown():
    """XIC/XIO/OTE/NOP get no isolation sweep because they ARE the
    scaffolding -- that makes them the most-tested weights, not the least."""
    for op in ("XIC", "XIO", "OTE", "NOP"):
        assert instruction_band(op, TABLE).key == "MEASURED", op


def test_the_corpus_actually_backs_the_good_bands():
    """Guards against the table being regenerated into meaninglessness."""
    assert TABLE, "instruction_accuracy missing from memory_model.yaml"
    assert instruction_band("MOV", TABLE).key == "MEASURED"
    # MAPC is the worst-measured instruction in the corpus and must not
    # claim a bound it has not earned.
    assert instruction_band("MAPC", TABLE).pct <= 75


def test_a_rung_is_only_as_good_as_its_worst_instruction():
    good = rung_band(["MOV", "XIC"], TABLE)
    mixed = rung_band(["MOV", "XIC", "MAPC"], TABLE)
    assert good.pct > mixed.pct


def test_series_outputs_cap_a_rung_at_approximate():
    """OQ-SERIESOUTPUT is exact on generated files and rejected by all
    seventeen real programs. An unresolved contradiction is not confidence."""
    plain = rung_band(["MOV"], TABLE, series_outputs=1)
    cascade = rung_band(["MOV"], TABLE, series_outputs=3)
    assert plain.pct > cascade.pct
    assert cascade.key == "APPROX"


def test_fitted_provenance_does_not_map_to_a_confident_band():
    assert PROVENANCE_BAND["KNOWN"] == "EXACT"
    assert PROVENANCE_BAND["FITTED"] == "UNVERIFIED"
    assert PROVENANCE_BAND["UNKNOWN"] == "UNPRICED"
