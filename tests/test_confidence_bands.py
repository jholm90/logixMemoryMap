"""Confidence must report MEASURED ACCURACY, not a provenance tag.

The old UI printed a provenance tier as if it were a confidence, so every
routine read "0% measured" -- because compiled ladder size can never be
KNOWN, by CLAUDE.md's ground-truth constraint. That says something about
Rockwell's file format, not about this model's error, and it read as an
admission of ignorance about numbers that reproduce captures to the byte.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from l5x_memory_analyzer.sizing.confidence import (  # noqa: E402
    KNOWN_EXACT_CALLS, PROVENANCE_BAND, ZERO_PARAM_JSR, band_for_error,
    instruction_band, refine_opcodes, rung_band, weakest,
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
    # A parameterised JSR is the weakest measured instruction -- its files
    # carry the open per-caller shell question -- and must not claim a bound
    # it has not earned. (This used to name MAPC, whose only entry came from a
    # buggy build; its corrected captures measure it exactly.)
    assert instruction_band("JSR", TABLE).pct <= 75


def test_a_rung_is_only_as_good_as_its_worst_instruction():
    good = rung_band(["MOV", "XIC"], TABLE)
    mixed = rung_band(["MOV", "XIC", "JSR"], TABLE)
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


# ---------------------------------------------------------------------------
# A 0-parameter JSR is EXACT. Pinned, because this is a named exception to the
# rule that compiled logic always reads as estimated, and an unpinned
# exception is one refactor away from silently reverting.
#
# The measurement: one distinct 0-parameter target plus its call costs exactly
# 368 bytes, over eight independent intervals in two separately built
# generators, zero residual at every one. The 280-byte whole-file residual on
# that family belongs to jsr_fixed_base_per_routine, a per-routine shell
# constant that does not move with call count, target count or name length.
# ---------------------------------------------------------------------------

ZERO_PARAM = [("Tgt", 0, 0)]


def test_zero_parameter_jsr_is_exact():
    assert KNOWN_EXACT_CALLS[ZERO_PARAM_JSR] == "EXACT"
    assert instruction_band(ZERO_PARAM_JSR, TABLE).key == "EXACT"
    assert instruction_band(ZERO_PARAM_JSR, TABLE).pct == 100


def test_refine_promotes_only_an_all_zero_parameter_rung():
    assert refine_opcodes(["JSR"], ZERO_PARAM) == [ZERO_PARAM_JSR]
    assert refine_opcodes(["JSR"], [("Tgt", 2, 0)]) == ["JSR"]
    assert refine_opcodes(["JSR"], [("Tgt", 0, 1)]) == ["JSR"]
    # One parameterised call anywhere in scope holds the whole scope back:
    # a single band is being claimed over all of them.
    assert refine_opcodes(["JSR"], [("A", 0, 0), ("B", 3, 0)]) == ["JSR"]
    # No call list parsed -> no promotion. Never guess.
    assert refine_opcodes(["JSR"], []) == ["JSR"]
    assert refine_opcodes(["JSR"], None) == ["JSR"]
    # Nothing else is touched.
    assert refine_opcodes(["MOV", "XIC"], ZERO_PARAM) == ["MOV", "XIC"]


def test_a_parameterised_jsr_stays_on_the_fitted_weight():
    """jsr_paramtype_* still misses by thousands of bytes on UDT and STRING
    parameters, so a JSR that carries them must not claim the exact band."""
    assert instruction_band("JSR", TABLE).key != "EXACT"


def test_a_rung_of_pure_zero_parameter_dispatch_is_exact():
    assert rung_band(refine_opcodes(["JSR"], ZERO_PARAM), TABLE).key == "EXACT"
    # And a mixed rung is still only as good as its worst instruction.
    mixed = refine_opcodes(["JSR", "XIC"], ZERO_PARAM)
    assert rung_band(mixed, TABLE).key == "MEASURED"


def test_a_refined_key_falls_back_to_its_base_mnemonic():
    """A shape suffix must never demote an instruction to Unverified just
    because the accuracy table is keyed on the bare mnemonic."""
    table = {"MOV": {"samples": 3, "mean_pct": 0.01, "worst_pct": 0.02}}
    assert instruction_band("MOV/0", table).key == "MEASURED"


def test_mapc_is_exact():
    """MAPC's per-call cost is the measured step between 1 and 10 rungs,
    260.000 exactly; its files are storage-dominated, so the whole-file table
    alone never priced it."""
    assert instruction_band("MAPC", TABLE).key == "EXACT"


def test_storage_dominated_instructions_are_measured_not_unverified():
    """The slope arm of derive_instruction_accuracy.py measures instructions
    whose files are mostly tag storage. Before it, every motion instruction
    read Unverified despite exact captures."""
    for op in ("MAFR", "MASD", "MASR", "MDW", "MGSD", "MGSR", "MCCP"):
        assert instruction_band(op, TABLE).key == "MEASURED", op
