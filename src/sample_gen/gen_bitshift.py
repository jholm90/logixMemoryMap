"""BSR and BSL weights, the last unmeasured instruction a real routine reaches.

BSR is charged 60 bytes and nothing has ever tested it. In a real export it is
the single largest rung of the routine that uses it -- 1,192 bytes of one rung
and 636 of another, 58% of that routine's compiled size -- so the routine
reports "Unverified, unbounded" on the majority of its bytes. BSL shares the
weight and the same absence of evidence.

THE SHAPE IS THE REAL ONE. Transplanted from the only real call sites in the
corpus, with tag names substituted:

    BSR(LugsWithLostBoards[0],LostBoardBSR,Found_LostBoard,?)
              DINT[2] array    CONTROL tag    BOOL source   length

so an array element as the first operand, a CONTROL tag as the second, a BOOL
as the bit source, and an immediate length. Both real sites are DINT[2].

WHY A COUNT SWEEP AND NOT A PAIR. Every other instruction in this project was
fitted by differencing consecutive count points so the shared per-file base
cancels. A single file would measure the base and the instruction together, and
this project has been caught by exactly that before. Five counts, so the slope
is over-determined rather than fitted to two points.

WHAT EACH ARM DISCRIMINATES

  A  bitshift_bsr_n{N}     N BSR rungs sharing ONE control tag and one array,
                           so the ONLY thing that moves between counts is the
                           instruction. The slope against N is the BSR weight.
                           This is the one that closes the question.

  B  bitshift_bsl_n{N}     the same at the same counts with BSL. BSR and BSL
                           carry an identical 60 in the model; if the slopes
                           differ, that shared constant is wrong for one of
                           them and nothing on file would have shown it.

  C  bitshift_bsr_len{L}   N fixed, LENGTH operand swept 32/64/128/256 against
                           an array held fixed at DINT[8]. A bit-shift walks
                           its array, so the cost plausibly scales with the
                           length rather than being flat per call. The array
                           does NOT move with it: array storage is priced
                           exactly by the tag sizer already, and moving both
                           would measure their sum.

  D  bitshift_ctlper_n{N}   N BSR rungs with one CONTROL EACH, against arm A's
                           single shared control at the same N. A CONTROL is
                           storage the tag sizer prices exactly, so the pair at
                           equal N isolates whether a per-rung control costs
                           anything beyond its own declared storage.

                           The first cut of this generator had arm A declaring
                           a control per rung, which moved the tag inventory
                           with the instruction count -- two variables per
                           step. confound_check.py refused it, correctly.

Every file is 1756-L81E at firmware 35, per the platform rule.

Run: python -m sample_gen.gen_bitshift
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rungs_xml, tag_xml, tags_xml
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
CATEGORY = "logic_instr"
COUNTS = (10, 50, 100, 500, 1000)
# Real corpus length: both real BSR sites shift a DINT[2], which is 64 bits.
REAL_BITS = 64
BIT_LENGTHS = (32, 64, 128, 256)

OQ = ("OQ-BITSHIFT")


def _emit(out_name: str, description: str, tags: str, rungs: str) -> int:
    l5x = build_l5x(
        target_name="".join(p.capitalize() for p in out_name.split("_")),
        tags_xml=tags,
        extra_rungs_xml=rungs,
    )
    out_path = OUT_ROOT / f"{out_name}.L5X"
    lint_or_raise(l5x, context=str(out_path))
    out_path.write_text(l5x, encoding="utf-8")
    append_manifest_row(out_name, description, CATEGORY, out_path, 0)
    print(f"Wrote {out_path}")
    return 1


def _array_words(bits: int) -> int:
    """DINT words needed to hold `bits`, matching the real DINT[2] at 64."""
    return max(1, bits // 32)


def _tags(n_controls: int, bits: int) -> str:
    """The shift array, the source bit, and one CONTROL per rung."""
    parts = [
        tag_xml("ShiftArray", "DINT", (_array_words(bits),)),
        tag_xml("SourceBit", "BOOL"),
    ]
    parts.append(tags_xml([(f"Ctl{i:04d}", "CONTROL") for i in range(n_controls)]))
    return "\n".join(p for p in parts if p)


def group_a_bsr_count() -> int:
    n = 0
    for count in COUNTS:
        n += _emit(
            f"bitshift_bsr_n{count:05d}",
            f"{count} BSR rungs, one CONTROL tag each, shifting a DINT[{_array_words(REAL_BITS)}] "
            f"at {REAL_BITS} bits -- the real corpus shape. Arm A of the bit-shift sweep for "
            f"{OQ}: BSR is charged 60 bytes with no isolation file behind it, and it is 58% of "
            f"the compiled size of the one real routine that uses it. The slope against count "
            f"across 10/50/100/500/1000 is the weight; differencing consecutive counts cancels "
            f"the per-file base the way every other instruction in this project was fitted.",
            _tags(1, REAL_BITS),
            rungs_xml(count, lambda i: f"BSR(ShiftArray[0],Ctl0000,SourceBit,{REAL_BITS});"),
        )
    return n


def group_b_bsl_count() -> int:
    n = 0
    for count in COUNTS:
        n += _emit(
            f"bitshift_bsl_n{count:05d}",
            f"{count} BSL rungs, identical to bitshift_bsr_n{count:05d} in every respect but "
            f"the opcode. Arm B of the bit-shift sweep for {OQ}: the model carries a single "
            f"shared weight of 60 for BSR and BSL, which is an assumption nothing has tested. "
            f"Differenced against arm A at the same count, any non-zero result means that "
            f"shared constant is wrong for one of them.",
            _tags(1, REAL_BITS),
            rungs_xml(count, lambda i: f"BSL(ShiftArray[0],Ctl0000,SourceBit,{REAL_BITS});"),
        )
    return n


def group_c_array_length() -> int:
    n = 0
    count = 100
    for bits in BIT_LENGTHS:
        n += _emit(
            f"bitshift_bsr_len{bits:04d}",
            f"{count} BSR rungs with the LENGTH operand at {bits}, the array held fixed at "
            f"DINT[{_array_words(max(BIT_LENGTHS))}] across all four. Arm C of "
            f"the bit-shift sweep for {OQ}: a bit-shift walks its array, so its cost plausibly "
            f"scales with array length rather than being flat per call. Held at {count} rungs "
            f"while only the length moves, so the difference between these four is the length "
            f"term alone. If they are byte-identical, arm A's slope is the whole answer; if not, "
            f"arm A on its own would have been an average over one length.",
            _tags(1, max(BIT_LENGTHS)),
            rungs_xml(count, lambda i: f"BSR(ShiftArray[0],Ctl0000,SourceBit,{bits});"),
        )
    return n


def group_d_control_per_rung() -> int:
    n = 0
    # ONE file, not a sweep. Its whole job is to be differenced against arm A
    # at the same rung count, and a second file at a different count would move
    # the rung count and the control count together -- two variables between
    # two files that are never compared to each other anyway. confound_check
    # flagged exactly that and it was right to.
    for count in (1000,):
        n += _emit(
            f"bitshift_ctlper_n{count:05d}",
            f"{count} BSR rungs with one CONTROL tag EACH, against bitshift_bsr_n{count:05d} "
            f"which shares a single control across all of them. Arm D of the bit-shift sweep "
            f"for {OQ}: a CONTROL is storage the tag sizer prices exactly, so the pair at equal "
            f"count isolates whether a per-rung control costs anything beyond its own declared "
            f"storage. Differenced against arm A at the same count, never against each other.",
            _tags(count, REAL_BITS),
            rungs_xml(count, lambda i: f"BSR(ShiftArray[0],Ctl{i:04d},SourceBit,{REAL_BITS});"),
        )
    return n


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    total = (group_a_bsr_count() + group_b_bsl_count()
             + group_c_array_length() + group_d_control_per_rung())
    print(f"\n{total} bit-shift file(s) written to {OUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
