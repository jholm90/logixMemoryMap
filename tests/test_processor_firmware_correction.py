"""Per-family firmware correction, OQ-BASELINE-PROCFW.

One global firmware ladder cannot fit every processor family: on a bare-baseline
file -- one processor, one firmware, no content -- the residual IS the baseline
error, and those residuals are constant within a firmware band while the bands
differ by family.
"""

from __future__ import annotations

from l5x_memory_analyzer.sizing.constants import load_memory_model

MODEL = load_memory_model()


def _c(processor: str, revision: str) -> int:
    return MODEL.processor_firmware_correction.correction_for(processor, revision)[0]


def test_no_1756_l8x_correction_at_any_firmware() -> None:
    """The L8x fwmatrix rows DO sit at +16 on v34/v35, and correcting that here
    is wrong. Every generated test file in this project is a 1756-L81E at v35,
    so a -16 baseline correction moved 787 previously-exact captures to -16 and
    dropped the corpus exact rate from 32.9% to 6.6%. The +16 is a
    firmware-dependent CONTENT gap (the real MainRoutine drops to 0 bytes on
    v34+ while this engine still predicts 16), not a baseline one."""
    for rev in ("31.01", "32.02", "33.01", "34.01", "35.11", "38.01"):
        assert _c("1756-L81E", rev) == 0, rev
        assert _c("1756-L83ES", rev) == 0, rev


def test_l3100_is_matched_before_l310() -> None:
    """Load-bearing ordering: "5069-L3100ERM" also starts with "5069-L310", so
    if the L306/L310/L320 pattern is tried first the L3100 family silently takes
    its numbers (+48/+32 instead of +8/-8/+32)."""
    assert _c("5069-L3100ERM", "33.01") == 8
    assert _c("5069-L3100ERM", "38.01") == 32
    assert _c("5069-L310ERS2", "33.01") == 48
    assert _c("5069-L310ERS2", "38.01") == 32


def test_5069_small_and_large_families_differ() -> None:
    assert _c("5069-L320ER", "35.11") == 32
    assert _c("5069-L330ER", "35.11") == -8


def test_unknown_processor_and_firmware_get_no_correction() -> None:
    assert _c("9999-NOT-REAL", "35.11") == 0
    assert _c("1756-L81E", "") == 0
    assert _c(None, "35.11") == 0
    # A real family at a firmware with no captured baseline falls through to 0
    # rather than borrowing a neighbouring band's number.
    assert _c("1756-L81E", "99.01") == 0
