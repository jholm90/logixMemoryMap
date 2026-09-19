"""Whether a series output instruction after the first is cheaper -- OQ-SERIESOUTPUT.

Written (capture-batch segment 5). Two captured single-shape sweeps
say the engine over-charges a rung that holds more than one OUTPUT instruction in
series, by exactly 12 bytes per output beyond the first:

    UID()UIE();                                      2 outputs   -12.000/rung
    XIC(Bit0)MOV(1,Dst0)ADD(Dst0,1,Dst0)OTE(Bit1);   3 outputs   -24.000/rung

Both slopes are exact across three orders of magnitude of rung count, and the
one-output control shapes are exact: `XIC(B0)OTE(B1);` reads 0 over 1,000 rungs,
`MOV(0,D0);`, `ADD(D0,D1,D2);` and `OTE(B0);` each read the universal +8 at 10
through 5,000 rungs. So the per-instruction weights are right in isolation and
something about a series cascade is not.

WHY IT IS NOT WIRED, and this is the whole reason this batch exists. Applying
-12 per extra series output to the sixteen real programs takes mean absolute
error from 2.07% to 2.90%, and every one of the sixteen gets worse -- they
already under-predict, and this correction predicts less. Counting outputs at
bracket depth 0 only (so parallel branch legs are exempt, which
`[XIC(B0),XIC(B1)]OTE(B2);` and the whole branchdepth family confirm they are)
does not save it: the real files still go 2.07% -> 2.90%. Counting branch
contents too is worse still, 4.51%.

That is a law that is exact on two generated shapes and rejected by the only
files that matter. Something the two shapes share is not present in real ladder,
and until it is named this must not be fitted. The candidates, and the group that
tests each:

  A. The COUNT is not really linear at 12. Two points (1 extra, 2 extra) cannot
     tell 12-per-extra from "12 for the second output and nothing after", or
     from a cap.
  B. Every rung in both sweeps is BYTE-IDENTICAL, thousands of times over, and
     addresses the same operand tags in every rung. Real rungs differ from each
     other. One-output shapes are exact under the same repetition
     (`instr_mov_n05000` is 5,000 identical rungs), so repetition alone is not
     it -- but repetition PLUS a cascade is untested.
  C. Series versus parallel. Branches are already known exempt, but never at
     matched output counts against a series arm in the same batch.
  D. Whether the outputs are the same instruction repeated or different types.
     Both sweeps repeat within the rung (UID/UIE are two distinct zero-operand
     instructions; MOV/ADD/OTE are three distinct ones), so this is not
     separated either.

GROUP A -- `srout_ote_k{01..08}_n01000`, 8 files. One XIC condition and k OTE
    outputs in series, each to its own bit, 1,000 identical rungs. OTE is the
    right instrument: its isolated weight is confirmed exact at five counts from
    10 to 5,000, and it takes one operand, so nothing but the output count moves.
    Eight consecutive counts read the shape of the law instead of two points on
    it -- linear at 12, a one-time step, or a cap.

GROUP B -- `srout_oteuniq_k{02,04,08}_n00200`, 3 files. The same cascade, but
    every rung writes its OWN distinct bits, so no two rungs are identical and no
    tag is addressed twice. 200 rungs rather than 1,000 keeps the tag count
    sane (k x 200). Against group A at the same k this is a direct test of
    candidate B: if the discount is deduplication of repeated rung structure it
    disappears here, and if it survives it is a genuine per-rung layout rule.

GROUP C -- `srout_branch_k{02,04,08}_n01000`, 3 files. The same k outputs in
    PARALLEL branch legs instead of in series, same tags, same rung count, so
    the series and parallel arms differ in nothing else. The branchdepth families
    already say branches are exact, but never against a matched series arm.

GROUP D -- `srout_mixed_k04_n01000` and `srout_same_k04_n01000`, 2 files. Four
    outputs of four DIFFERENT types against four OTEs, at the same count. If the
    discount tracks distinct types rather than output count these two split.

16 files. Every rung shape here is built from instructions whose isolated weight
is already confirmed exact against a real capture (XIC, OTE, MOV, ADD, CLR), and
cascaded outputs and parallel output branches are both ordinary ladder that the
real corpus uses throughout -- no invented shapes.

Run: python -m sample_gen.gen_seriesoutput_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
CATEGORY = "series_output"

SHARED_K = (1, 2, 3, 4, 5, 6, 7, 8)
UNIQ_K = (2, 4, 8)
BRANCH_K = (2, 4, 8)
SHARED_RUNGS = 1000
UNIQ_RUNGS = 200


def _write(name: str, l5x: str, description: str) -> None:
    out = OUT / f"{name}.L5X"
    append_manifest_row(name, description, CATEGORY, out, write_sample(l5x, out))


def _build(tags: list[str], rungs: list[str]) -> str:
    return build_l5x(
        target_name="SeriesOutProbe",
        tags_xml="\n".join(tags),
        extra_rungs_xml="\n".join(rung_xml(i, text) for i, text in enumerate(rungs)),
    )


def _group_a() -> int:
    for k in SHARED_K:
        tags = [tag_xml("Cond", "BOOL")] + [tag_xml(f"Out{i}", "BOOL") for i in range(k)]
        text = "XIC(Cond)" + "".join(f"OTE(Out{i})" for i in range(k)) + ";"
        _write(
            f"srout_ote_k{k:02d}_n{SHARED_RUNGS:05d}",
            _build(tags, [text] * SHARED_RUNGS),
            f"One XIC condition and {k} OTE outputs in series, each to its own bit, "
            f"{SHARED_RUNGS} identical rungs. Group A of the series-output closeout: "
            f"OTE's isolated weight is confirmed exact at five counts from 10 to 5,000 "
            f"and it takes one operand, so the output COUNT is the only thing moving "
            f"across the eight files. Two captured shapes -- UID()UIE() at 2 outputs "
            f"and XIC(Bit0)MOV(1,Dst0)ADD(Dst0,1,Dst0)OTE(Bit1) at 3 -- say the engine "
            f"over-charges 12 per output beyond the first, exactly, but applying that "
            f"takes the sixteen real programs from 2.07% to 2.90% mean absolute error "
            f"and makes every one of them worse. Eight consecutive counts say whether "
            f"the law is linear at 12, a one-time step, or capped. OQ-SERIESOUTPUT.",
        )
    return len(SHARED_K)


def _group_b() -> int:
    for k in UNIQ_K:
        tags = [tag_xml("Cond", "BOOL")]
        rungs = []
        for r in range(UNIQ_RUNGS):
            names = [f"U{r:03d}b{i}" for i in range(k)]
            tags += [tag_xml(n, "BOOL") for n in names]
            rungs.append("XIC(Cond)" + "".join(f"OTE({n})" for n in names) + ";")
        _write(
            f"srout_oteuniq_k{k:02d}_n{UNIQ_RUNGS:05d}",
            _build(tags, rungs),
            f"The same {k}-OTE series cascade as srout_ote_k{k:02d}, but every one of "
            f"the {UNIQ_RUNGS} rungs writes its OWN distinct bits, so no two rungs are "
            f"byte-identical and no tag is addressed twice. Group B of the series-output "
            f"closeout, and the candidate most likely to explain why a law that is exact "
            f"on two generated shapes is rejected by all sixteen real programs: both of "
            f"those shapes repeat one identical rung thousands of times over the same "
            f"operands, and real ladder does not. One-output shapes are exact under the "
            f"same repetition (instr_mov_n05000 is 5,000 identical rungs), so repetition "
            f"alone is not it -- repetition plus a cascade is what is untested. Differences "
            f"straight against group A at the same k. OQ-SERIESOUTPUT.",
        )
    return len(UNIQ_K)


def _group_c() -> int:
    for k in BRANCH_K:
        tags = [tag_xml("Cond", "BOOL")] + [tag_xml(f"Out{i}", "BOOL") for i in range(k)]
        legs = ",".join(f"OTE(Out{i})" for i in range(k))
        text = f"XIC(Cond)[{legs}];"
        _write(
            f"srout_branch_k{k:02d}_n{SHARED_RUNGS:05d}",
            _build(tags, [text] * SHARED_RUNGS),
            f"The same {k} OTE outputs as srout_ote_k{k:02d}, in PARALLEL branch legs "
            f"instead of in series -- same tags, same {SHARED_RUNGS} rungs, same "
            f"condition, so the two arms differ in nothing but series versus parallel. "
            f"Group C of the series-output closeout. The branchdepth families already "
            f"read exactly 0 for parallel legs, but never against a matched series arm "
            f"in the same batch, and the whole question is whether the 12-per-extra-output "
            f"discount is about cascading specifically. OQ-SERIESOUTPUT.",
        )
    return len(BRANCH_K)


def _group_d() -> int:
    common = [tag_xml("Cond", "BOOL"), tag_xml("Out0", "BOOL")]
    common += [tag_xml(f"Dst{i}", "DINT") for i in range(3)]
    mixed = "XIC(Cond)OTE(Out0)MOV(1,Dst0)ADD(Dst0,1,Dst1)CLR(Dst2);"
    same_tags = [tag_xml("Cond", "BOOL")] + [tag_xml(f"Out{i}", "BOOL") for i in range(4)]
    same = "XIC(Cond)" + "".join(f"OTE(Out{i})" for i in range(4)) + ";"
    _write(
        f"srout_mixed_k04_n{SHARED_RUNGS:05d}", _build(common, [mixed] * SHARED_RUNGS),
        f"Four series outputs of four DIFFERENT types (OTE, MOV, ADD, CLR) under one XIC "
        f"condition, {SHARED_RUNGS} identical rungs. Group D of the series-output "
        f"closeout: paired with srout_same_k04, which holds the count at four and makes "
        f"them all OTE. Both captured shapes that show the 12-per-extra-output discount "
        f"use distinct instructions within the rung, so distinct-type and output-count "
        f"are not separated anywhere in the corpus. Every weight here is confirmed exact "
        f"in isolation. OQ-SERIESOUTPUT.",
    )
    _write(
        f"srout_same_k04_n{SHARED_RUNGS:05d}", _build(same_tags, [same] * SHARED_RUNGS),
        f"Four series OTE outputs -- the same COUNT as srout_mixed_k04 with one repeated "
        f"instruction type instead of four distinct ones, {SHARED_RUNGS} identical rungs. "
        f"Group D of the series-output closeout; see srout_mixed_k04. OQ-SERIESOUTPUT.",
    )
    return 2


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    total = _group_a() + _group_b() + _group_c() + _group_d()
    print(f"Total: {total}")


if __name__ == "__main__":
    main()
