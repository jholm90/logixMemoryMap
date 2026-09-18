"""Price rung ARRANGEMENT at the shape real ladder actually has -- OQ-RUNGSHAPE.

Measured 2026-09-18 across all sixteen real programs (41,136 rungs, 255,027
instruction occurrences) against the 733 captured corpus files the logic
weights were fitted on (525,936 rungs):

                              real    fitted corpus
    rungs containing a branch  68.7%           9.4%
    single-instruction rungs      7%            62%
    three-or-more-instruction    70%            12%

Every instruction weight in the model is calibrated on essentially unbranched,
one-instruction rungs and then applied to a population where seven rungs in ten
branch and seven in ten carry three or more instructions. That is the largest
measured evidence gap in the project, and the residual it has to explain is
+653,678 bytes (+1.375%) across the sixteen.

WHAT IS ALREADY RULED OUT, so none of these files re-tests it. A constant error
per instruction occurrence is dead (CV 1.74 across the sixteen, 1.72 over the
top four instructions, 1.73 per rung), so this is not a uniform weight error.
Branch FRACTION is dead as the carrier too -- it is nearly flat across the
sixteen at 58.6%-76.1% and correlates at only r = -0.250. What does correlate,
at r = -0.732 against residual bytes, is the fraction of instructions sitting
INSIDE branches, which ranges 26.1%-45.2%. A two-term fit (+11 bytes per series
instruction, -15 per in-branch instruction) takes the sixteen from mean 1.5607%
to 1.0820%, and must not be wired: two free parameters against sixteen points,
per-unit CV 1.87 and 1.55, and no mechanism predicts a negative cost for being
inside a branch. These files exist to measure that split directly instead.

Also NOT tested here, because the claim that prompted it was withdrawn: there
is no per-instruction operand-count gap. That finding came from splitting
operands on every comma, which counts COP(Hist[0,0],Tmp[0,0],800) as five. With
bracket-aware splitting, 19 of the top 20 real instructions have operand counts
the corpus already covers exactly.

GROUP A -- `rshape_arr_legs{01,02,04,08}_n00500`, 4 files. Eight XIC conditions
    and one OTE, 500 rungs, the instruction multiset and every operand held
    byte-identical; the ONLY thing that moves is how the eight conditions are
    arranged -- all in series, then two legs of four, four of two, eight of one.
    This is the measurement the whole entry is about: at fixed inventory, what
    does arrangement cost? Differencing consecutive files cancels the
    instructions entirely and leaves the arrangement term alone.

GROUP B -- `rshape_pack_i{01,02,04,08,16}_n04000i`, 5 files. A fixed total of
    4,000 OTE instructions, packed 1, 2, 4, 8 and 16 to a rung -- 4,000 rungs
    down to 250. Instruction inventory is identical in all five (4,000 OTEs over
    4,000 distinct bits), so the per-rung term separates from the
    per-instruction term, which no existing family does: every single-shape
    sweep varies rung count and instruction count together. OTE is the right
    instrument because its isolated weight is confirmed exact at five counts
    from 10 to 5,000 and it takes one operand.

GROUP C -- `rshape_mix_{series,branch}_n00500`, 2 files. The real population's
    mix -- 70% of rungs carrying three or more instructions -- built once with
    those instructions in series and once with the same instructions in branch
    legs. Same multiset, same operands, same rung count. This is group A's
    question asked at a realistic rung composition rather than a uniform one,
    and it is the pair that tests the -0.732 correlate directly.

GROUP D -- `rshape_sub2d_{flat,2d}_n00500`, 2 files. The one real operand shape
    the corpus genuinely never builds: a 2-D array subscript. 2,364 of 254,703
    real operand references (0.93%) carry `[i,j]`; the corpus has zero across
    942,157. Paired against a flat `[i]` control at the same instruction count
    and the same element count, so only the subscript dimensionality moves.

13 files, every one 1756-L81E at v35, every instruction one whose isolated
weight is already confirmed exact against a real capture (XIC, OTE, MOV), and
every shape ordinary ladder that real programs use throughout. Verify with
`python scripts/confound_check.py --family '^rshape_'` -- every consecutive pair
within a group must vary exactly one dimension.

Run: python -m sample_gen.gen_rungshape
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
CATEGORY = "rung_shape"

ARR_RUNGS = 500
ARR_CONDS = 8
ARR_LEGS = (1, 2, 4, 8)

PACK_TOTAL = 4000
PACK_PER_RUNG = (1, 2, 4, 8, 16)

MIX_RUNGS = 500
SUB_RUNGS = 500
SUB_DIM = 20                      # 20x20 = 400 elements, same count both arms


def _write(name: str, l5x: str, description: str) -> None:
    out = OUT / f"{name}.L5X"
    append_manifest_row(name, description, CATEGORY, out, write_sample(l5x, out))


def _build(tags: list[str], rungs: list[str]) -> str:
    return build_l5x(
        target_name="RungShapeProbe",
        tags_xml="\n".join(tags),
        extra_rungs_xml="\n".join(rung_xml(i, t) for i, t in enumerate(rungs)),
    )


def _group_a() -> int:
    tags = [tag_xml(f"Cond{i}", "BOOL") for i in range(ARR_CONDS)] + [tag_xml("Out0", "BOOL")]
    for legs in ARR_LEGS:
        per = ARR_CONDS // legs
        if legs == 1:
            cond = "".join(f"XIC(Cond{i})" for i in range(ARR_CONDS))
        else:
            cond = "[" + ",".join(
                "".join(f"XIC(Cond{L * per + j})" for j in range(per)) for L in range(legs)
            ) + "]"
        _write(
            f"rshape_arr_legs{legs:02d}_n{ARR_RUNGS:05d}",
            _build(tags, [f"{cond}OTE(Out0);"] * ARR_RUNGS),
            f"{ARR_CONDS} XIC conditions and one OTE, {ARR_RUNGS} identical rungs, "
            f"arranged as {legs} parallel leg(s) of {per}. Group A of the rung-shape "
            f"sweep, and the core measurement of OQ-RUNGSHAPE: the instruction multiset "
            f"and every operand are byte-identical across all four files, so the ONLY "
            f"thing that moves is arrangement, and differencing consecutive files cancels "
            f"the instructions and leaves the arrangement term alone. The logic weights "
            f"were fitted on a corpus that is 9.4% branched against 68.7% in the sixteen "
            f"real programs, which is the largest measured evidence gap in the project. "
            f"A constant per-instruction error is already ruled out (CV 1.74) and branch "
            f"FRACTION is ruled out as the carrier (r = -0.250); what correlates at "
            f"r = -0.732 is the fraction of instructions INSIDE branches, which is "
            f"exactly what these four files sweep. OQ-RUNGSHAPE.",
        )
    return len(ARR_LEGS)


def _group_b() -> int:
    for per in PACK_PER_RUNG:
        n = PACK_TOTAL // per
        tags = [tag_xml(f"B{i:04d}", "BOOL") for i in range(PACK_TOTAL)]
        rungs = ["".join(f"OTE(B{r * per + j:04d})" for j in range(per)) + ";" for r in range(n)]
        _write(
            f"rshape_pack_i{per:02d}_n{PACK_TOTAL:05d}i",
            _build(tags, rungs),
            f"A fixed total of {PACK_TOTAL} OTE instructions over {PACK_TOTAL} distinct "
            f"bits, packed {per} to a rung -- {n} rungs. Group B of the rung-shape sweep. "
            f"The instruction inventory and the tag inventory are identical in all five "
            f"files, so rung COUNT is the only thing that moves and the per-rung term "
            f"separates from the per-instruction term. No existing family can do this: "
            f"every single-shape sweep varies rung count and instruction count together, "
            f"which is why the corpus is 62% single-instruction rungs against 7% in real "
            f"programs. OTE is the instrument because its isolated weight is confirmed "
            f"exact at five counts from 10 to 5,000 and it takes one operand. "
            f"OQ-RUNGSHAPE.",
        )
    return len(PACK_PER_RUNG)


def _mix_rungs(branched: bool) -> tuple[list[str], list[str]]:
    """The real population's composition: 70% of rungs carrying three or more
    instructions, against the corpus's 12%. Built once in series and once in
    branch legs from the identical multiset."""
    tags = [tag_xml(f"M{i:03d}", "BOOL") for i in range(24)] + [tag_xml("MOut", "BOOL")]
    rungs = []
    for r in range(MIX_RUNGS):
        k = (r % 10) + 1                       # 1..10 conditions, 70% at 3 or more
        names = [f"M{(r * 3 + j) % 24:03d}" for j in range(k)]
        if branched and k >= 2:
            half = k // 2
            body = ("[" + "".join(f"XIC({n})" for n in names[:half]) + ","
                    + "".join(f"XIC({n})" for n in names[half:]) + "]")
        else:
            body = "".join(f"XIC({n})" for n in names)
        rungs.append(f"{body}OTE(MOut);")
    return tags, rungs


def _group_c() -> int:
    for branched in (False, True):
        tags, rungs = _mix_rungs(branched)
        kind = "branch" if branched else "series"
        _write(
            f"rshape_mix_{kind}_n{MIX_RUNGS:05d}",
            _build(tags, rungs),
            f"{MIX_RUNGS} rungs at the REAL population's composition -- 1 to 10 XIC "
            f"conditions per rung, 70% of rungs carrying three or more, against a corpus "
            f"that is 12% -- with those conditions "
            f"{'split into two parallel legs' if branched else 'all in series'}. Group C "
            f"of the rung-shape sweep, and the pair that tests the r = -0.732 correlate "
            f"directly: the two files hold the instruction multiset, the operands and the "
            f"rung count identical and move only series versus parallel. Group A asks the "
            f"same question at a uniform 8-condition rung; this asks it at a realistic "
            f"mix, because a term that only appears at one rung width would be a fitting "
            f"artefact. OQ-RUNGSHAPE.",
        )
    return 2


def _group_d() -> int:
    """Three points, not two.

    A two-file flat/2-D pair cannot be differenced: changing the subscript
    forces the declaration to change with it, so the capture measures the
    declaration cost and the subscript cost added together, in two different
    categories. The middle file carries the 2-D DECLARATION while its rungs
    still address a flat scratch array, which splits the ladder:

        flat -> decl   only the declaration moves
        decl -> 2d     only the operand subscript moves
    """
    total = SUB_DIM * SUB_DIM
    flat = [tag_xml("ArrFlat", "DINT", dimensions=(total,)), tag_xml("Src", "DINT")]
    two_d = [tag_xml("Arr2D", "DINT", dimensions=(SUB_DIM, SUB_DIM)), tag_xml("Src", "DINT")]
    flat_rungs = [f"MOV(Src,ArrFlat[{r % total}]);" for r in range(SUB_RUNGS)]
    sub_rungs = [f"MOV(Src,Arr2D[{(r % total) // SUB_DIM},{(r % total) % SUB_DIM}]);"
                 for r in range(SUB_RUNGS)]
    common = (
        f"Group D of the rung-shape sweep, a three-point ladder. 2-D array subscripts "
        f"are the one real operand shape the corpus genuinely never builds: 2,364 of "
        f"254,703 real operand references (0.93%) carry a [i,j] and the corpus has ZERO "
        f"across 942,157, matching the tag survey in OQ-TAGSHAPE where 2-D arrays are "
        f"0.16% of real tags and 0.00% of corpus tags. A flat/2-D PAIR could not be "
        f"differenced -- changing the subscript forces the declaration to change with "
        f"it, so a two-file capture measures a declaration cost and a subscript cost "
        f"added together across two different categories. The middle file carries the "
        f"2-D declaration while its rungs still address the flat array, so flat->decl "
        f"isolates the declaration and decl->2d isolates the subscript. Element count, "
        f"instruction count and rung count are identical in all three. OQ-RUNGSHAPE."
    )
    _write(f"rshape_sub2d_a_flat_n{SUB_RUNGS:05d}", _build(flat, flat_rungs),
           f"{SUB_RUNGS} MOV rungs into a flat DINT[{total}] addressed with a "
           f"one-dimensional subscript -- the control. {common}")
    _write(f"rshape_sub2d_b_decl_n{SUB_RUNGS:05d}",
           _build(flat + [tag_xml("Arr2D", "DINT", dimensions=(SUB_DIM, SUB_DIM))], flat_rungs),
           f"The flat control's {SUB_RUNGS} rungs unchanged, plus an UNREFERENCED "
           f"DINT[{SUB_DIM},{SUB_DIM}] declaration -- the same {total} elements as the "
           f"flat array, declared two-dimensionally and addressed by nothing. Isolates "
           f"the declaration cost of a 2-D array from the cost of subscripting one. "
           f"{common}")
    _write(f"rshape_sub2d_c_ref_n{SUB_RUNGS:05d}",
           _build(flat + two_d[:1], sub_rungs),
           f"The same two declarations as the middle file, with the {SUB_RUNGS} MOV "
           f"rungs now addressing the 2-D array with a [i,j] subscript instead of the "
           f"flat one. Differenced against the middle file this is the subscript cost "
           f"alone, with the declaration already paid for. {common}")
    return 3


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    total = _group_a() + _group_b() + _group_c() + _group_d()
    print(f"Total: {total}")


if __name__ == "__main__":
    main()
