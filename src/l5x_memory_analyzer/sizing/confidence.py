"""Two different questions, kept separate.

**Provenance** -- KNOWN / ASSUMED / FITTED / UNKNOWN -- says where a number
came from. It is what `weakest()` propagates and what the sizing code tags
itself with, and it is unchanged.

**Accuracy** -- how likely that number is to be RIGHT -- is a different
question, and reporting provenance in its place misled badly. Compiled ladder
size can never be KNOWN, because L5X does not reveal how Logix compiles rungs
(see CLAUDE.md's ground-truth constraint), so every logic weight is tagged
FITTED and a routine full of them reported "0% measured". That reads as "we
have no idea". The truth is the opposite: **292 of 298 captured isolation
files land within 0.1% of what the controller itself reported.**

So accuracy is a MEASUREMENT, taken from `instruction_accuracy` in
memory_model.yaml, which `scripts/derive_instruction_accuracy.py` regenerates
from captures. The bands below are the words the UI shows, and each one means
a stated error bound that was earned on real data rather than asserted.
"""

from __future__ import annotations

from dataclasses import dataclass

_ORDER = {"KNOWN": 0, "ASSUMED": 1, "FITTED": 2, "UNKNOWN": 3}


def weakest(*confidences: str) -> str:
    """Combining sizes propagates the least-confident tier involved."""
    return max(confidences, key=lambda c: _ORDER[c])


@dataclass(frozen=True)
class Band:
    key: str
    label: str
    pct: int              # the confidence number shown to the user
    bound: str            # what that number means, in bytes-terms
    blurb: str


# Ordered best to worst. `pct` is deliberately NOT a probability anyone
# measured -- it is a legend for the error bound beside it, which is. The
# bound is the claim; the percentage is how it is drawn.
BANDS = (
    Band("EXACT", "Exact", 100, "±0",
         "Calculated, not estimated. Atomic sizes and packing rules are "
         "published or directly derivable, and the capture agrees to the byte."),
    Band("MEASURED", "Measured", 98, "±0.1%",
         "Fitted, then confirmed against real controller readings. Every "
         "isolation file for this instruction landed inside 0.1%."),
    Band("CLOSE", "Close", 90, "±1%",
         "Confirmed against real readings, with a small residual that has "
         "not been explained away."),
    Band("APPROX", "Approximate", 75, "±5%",
         "Confirmed against real readings, but the spread is wide enough "
         "that a single rung could be visibly out."),
    Band("UNVERIFIED", "Unverified", 50, "unbounded",
         "A weight exists and is used, but no isolation file has ever tested "
         "this instruction on its own, so nothing bounds the error."),
    Band("UNPRICED", "Not counted", 0, "excluded",
         "No weight at all. These bytes are missing from the total, not "
         "estimated badly -- the number below them is a floor."),
)

_BY_KEY = {b.key: b for b in BANDS}

# Instructions that never get an isolation sweep because they ARE the
# scaffolding every other test rung is built from -- which makes them the
# most-tested weights in the model, not the least. NOP and the per-rung base
# come from the `emptyrungs` sweep; XIC/OTE are held fixed across the
# `rshape_arr_*` arrangement files, which captured byte-exact at every leg
# count on 2026-09-18.
SCAFFOLD_BAND = {"XIC": "MEASURED", "XIO": "MEASURED",
                 "OTE": "MEASURED", "NOP": "MEASURED"}


def band_for_error(worst_pct: float | None, samples: int = 0) -> Band:
    """The band a measured worst-case error earns."""
    if worst_pct is None or samples <= 0:
        return _BY_KEY["UNVERIFIED"]
    if worst_pct <= 0.1:
        return _BY_KEY["MEASURED"]
    if worst_pct <= 1.0:
        return _BY_KEY["CLOSE"]
    if worst_pct <= 5.0:
        return _BY_KEY["APPROX"]
    return _BY_KEY["UNVERIFIED"]


def instruction_band(opcode: str, accuracy_table: dict, has_weight: bool = True) -> Band:
    """How well this project can predict one instruction's cost."""
    if not has_weight:
        return _BY_KEY["UNPRICED"]
    if opcode in SCAFFOLD_BAND:
        return _BY_KEY[SCAFFOLD_BAND[opcode]]
    entry = (accuracy_table or {}).get(opcode)
    if not entry:
        return _BY_KEY["UNVERIFIED"]
    return band_for_error(entry.get("worst_pct"), entry.get("samples", 0))


def rung_band(opcodes, accuracy_table: dict, series_outputs: int = 1) -> Band:
    """A rung is only as predictable as its worst instruction.

    One MAM in an otherwise plain rung is near-certain; twenty mixed
    instructions are only as good as the least-known of them, which is what
    a user means by "how sure are you about THIS rung".

    The one shape that degrades a rung beyond its own instructions is more
    than one OUTPUT in series: OQ-SERIESOUTPUT measures a -12-byte-per-extra-
    output law that is exact on generated files at five counts and rejected
    by all seventeen real programs. Unresolved contradiction, so a rung that
    triggers it cannot claim better than Approximate.
    """
    bands = [instruction_band(op, accuracy_table) for op in opcodes] or [_BY_KEY["UNVERIFIED"]]
    worst = min(bands, key=lambda b: b.pct)
    if series_outputs > 1 and worst.pct > _BY_KEY["APPROX"].pct:
        return _BY_KEY["APPROX"]
    return worst


def band_by_key(key: str) -> Band:
    return _BY_KEY.get(key or "", _BY_KEY["UNVERIFIED"])


# Provenance tier -> the band it earns when no measurement applies. Data
# space is calculable exactly, so KNOWN really is exact; a FITTED weight with
# no isolation file behind it is genuinely unverified.
PROVENANCE_BAND = {
    "KNOWN": "EXACT",
    "ASSUMED": "APPROX",
    "FITTED": "UNVERIFIED",
    "UNKNOWN": "UNPRICED",
}
