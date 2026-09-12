"""Why every DTR rung errors, four candidate causes, one capture to decide.

Written 2026-09-12. All three `unweighted_dtr_*` files captured with
`error_count` EXACTLY equal to the rung count -- 10 errors at n=10, 100 at
n=100, 1000 at n=1000 -- so it is one error per rung, a per-rung shape problem
rather than anything file-level. No error text was recorded (every errored row
in the manifest predates the 2026-09-10 error-log reader), so the cause has to
be isolated by construction.

DTR is a COMPARISON: it conditions the rung instead of writing to it, so it
needs a terminating output the way EQU and LES do. That is already handled --
the committed rung text is `DTR(D0,-1,D1)NOP();` and has been since the file
was built, so a missing terminator is NOT the cause and adding one changes
nothing. Worth stating plainly because it is the obvious first guess.

What differs from the ONE real DTR rung in the corpus
(`Sorter1_20260722r00.L5X`, the only real call site on file):

    DTR(THG._2_RxAsyncBuf.HeartbeatCounter,-1,THGComms_RxAsync_Buf_HeartbeatCounter)
    OTE(THGHeartbeatPulse)TON(THGHeartbeatTmr,?,?);

Three differences, each a candidate, and the sweep separates them:

  1. TERMINATOR. The real rung ends in `OTE`, not `NOP`. NOP is accepted as a
     terminator elsewhere in this project, but "elsewhere" is not DTR.
  2. SHARED REFERENCE. DTR's third operand is its own stored-value slot, not a
     plain destination -- it holds the previous scan's masked source so the
     next scan can compare against it. n rungs all naming `D1` may be the same
     class of error as two OTEs driving one bit. This is the leading suspect
     precisely because the error count tracks the rung count exactly.
  3. MASK LITERAL. `-1` as a decimal literal where a real project writes a
     mask. Least likely -- the real call also uses `-1` -- so it is the control
     that keeps the other two honest rather than a serious candidate.

ARMS, all against the same fixed tag pool as the original sweep so any
capture differences straight against `unweighted_dtr_n00010`:

    dtrnop_n{010,100}     the committed shape, unchanged. Reproduces the error,
                          or shows the original capture was environmental.
    dtrote_n{010,100}     OTE terminator, shared Reference. Isolates (1).
    dtruniq_n{010,100}    OTE terminator, its OWN Reference element per rung.
                          Isolates (2). If this one builds clean and dtrote
                          does not, the answer is the shared slot.
    dtrreal_n010          the real rung transplanted whole, TON and all. The
                          end-to-end control: if even this errors, the problem
                          is not the rung at all and the generator's tag pool
                          or the file shell is implicated.

Two counts on the three main arms so that whichever one builds clean also
yields DTR's per-rung weight immediately, rather than needing a second round.

Run: python -m sample_gen.gen_dtr_variants
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import (
    control_tag_xml,
    rungs_xml,
    string_array_tag_xml,
    tag_xml,
    timer_tag_xml,
)
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

COUNTS = (10, 100)
MAX_RUNGS = max(COUNTS)

# The original sweep's pool, plus what the variants need: a Reference ARRAY big
# enough to give every rung its own element, and a TIMER for the real
# transplant. Everything the original pool had stays, unchanged, so the shared
# storage cancels in any difference against unweighted_dtr_n00010.
_POOL = "\n".join([
    *(tag_xml(f"D{i}", "DINT") for i in range(4)),
    *(tag_xml(f"R{i}", "REAL") for i in range(6)),
    *(tag_xml(f"B{i}", "BOOL") for i in range(3)),
    tag_xml("ARR0", "DINT", dimensions=(20,)),
    control_tag_xml("CTRL0", length=12, position=0),
    string_array_tag_xml("STRPOOL", 2),
    tag_xml("STR0", "STRING", string_max_len=82),
    tag_xml("STR1", "STRING", string_max_len=82),
    tag_xml("DtrRef", "DINT", dimensions=(MAX_RUNGS,)),
    timer_tag_xml("DtrTmr", preset=1000),
])

_ARMS = {
    "dtrnop": (
        lambda i: "DTR(D0,-1,D1)NOP();",
        "the committed shape, unchanged -- the control that reproduces the error (or shows the "
        "original capture was environmental). DTR is a comparison and already HAS its terminating "
        "NOP, so a missing output is not the cause and this arm is what proves that rather than "
        "asserting it",
    ),
    "dtrote": (
        lambda i: "DTR(D0,-1,D1)OTE(B0);",
        "OTE terminator instead of NOP, Reference still shared. The one real DTR rung in the "
        "corpus ends in OTE, so this isolates whether NOP is simply not an acceptable terminator "
        "for DTR specifically",
    ),
    "dtruniq": (
        lambda i: f"DTR(D0,-1,DtrRef[{i}])OTE(B0);",
        "OTE terminator AND its own Reference element per rung. DTR's third operand is its stored "
        "previous-scan value, not a plain destination, so n rungs sharing one may be the same class "
        "of error as two OTEs driving one bit -- the leading suspect, because the error count "
        "tracks the rung count exactly",
    ),
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    for arm, (rung_fn, why) in _ARMS.items():
        for n in COUNTS:
            l5x = build_l5x(target_name=f"DtrVar{arm[3:].title()}{n:04d}"[:24],
                            tags_xml=_POOL,
                            extra_rungs_xml=rungs_xml(n, lambda i: rung_fn(i)))
            name = f"{arm}_n{n:05d}"
            out = OUT / f"{name}.L5X"
            bytes_ = write_sample(l5x, out)
            append_manifest_row(
                name,
                f"{n} DTR rungs: {why}. All three unweighted_dtr_* files captured with "
                f"error_count EXACTLY equal to the rung count, so it is one error per rung -- a "
                f"per-rung shape problem, not a file-level one -- and no error text was recorded "
                f"because every errored row in the manifest predates the 2026-09-10 error-log "
                f"reader. Same fixed tag pool as the original sweep, so this differences straight "
                f"against unweighted_dtr_n{n:05d}. Two counts so whichever arm builds clean also "
                f"yields DTR's per-rung weight in the same round. OQ-VERIFINSTR.",
                "logic_instr", out, bytes_,
            )
            written += 1

    # The real rung, transplanted whole. One count: this is a yes/no control on
    # whether the rung is implicated at all, not a slope measurement.
    l5x = build_l5x(
        target_name="DtrVarReal0010", tags_xml=_POOL,
        extra_rungs_xml=rungs_xml(10, lambda i: f"DTR(D0,-1,DtrRef[{i}])OTE(B0)TON(DtrTmr,?,?);"),
    )
    out = OUT / "dtrreal_n00010.L5X"
    bytes_ = write_sample(l5x, out)
    append_manifest_row(
        "dtrreal_n00010",
        "10 DTR rungs in the shape of the ONE real DTR call site in the corpus "
        "(Sorter1_20260722r00.L5X): DTR then OTE then TON, with a unique Reference per rung. The "
        "end-to-end control -- if even this errors, the problem is not the rung and the tag pool "
        "or file shell is implicated instead. TON already has a measured weight, so it subtracts "
        "back out cleanly. OQ-VERIFINSTR.",
        "logic_instr", out, bytes_,
    )
    written += 1
    print(f"Total: {written}")


if __name__ == "__main__":
    main()
