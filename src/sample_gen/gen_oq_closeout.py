"""Discriminating files for the open questions whose data is measured but
ambiguous. Written 2026-09-18 during the full open-questions review.

Every arm here exists because a law was measured EXACTLY and could not be
applied, not because coverage was thin. Each arm names the reading it rejects.

ARM A -- `sroutc_c*_k*`, OQ-SERIESOUTPUT. THE most important files in this
batch. The discount is byte-exact on all 16 `srout_*` rows (-12 per writing
instruction beyond the first, eight output counts, invariant to type, tag
uniqueness and series-vs-branch) and applying it takes the sixteen real
programs from 1.7036% to 3.2167% mean, every one moving the wrong way. Every
existing srout_* rung has exactly ONE condition instruction; real rungs carry
several. So this sweeps condition count against output count. If the discount
holds at every condition count the contradiction is elsewhere and the weights
themselves are suspect; if it decays as conditions rise, that is the missing
term and it is per-rung, not per-output.

ARM B -- `cpttri_*`, OQ-CMPCPTLAYOUT. A flat +4 per rung appears on six
measured shapes and not on five others, and the trigger is NOT identified:
tier-1 count, tier-2 count, total operators, parenthesisation, tier-transition
count and leading-tier-1 count have each been tested and each fails on at
least one shape. At k=3 operators there are 8 possible tier sequences; the
corpus holds 111, 112, 121, 122 and 222. These are the missing three, which
complete the truth table so the discriminant is read rather than guessed.
Plus one three-operator adjacent `**` point: adjacency is worth +40/rung at
two operators (p2 -16 vs p2_adjacent +24) and two points cannot separate the
adjacency effect from the operator-count effect.

ARM C -- `stc2_*`, OQ-STEXPR-OPERATOR. Every ST operator has a 1-operator and
a 4-operator point and the fit needs two parameters, so it is exactly
determined and unfalsifiable. These are the 2-operator midpoints for the four
operators that are wrong (AND/OR/XOR/** at DINT, * and ** at REAL). With three
counts the existing rows become the check instead of the fit.

ARM D -- `stcall_*`, OQ-STEXPR-OPERATOR's second half. One AOI call in an ST
routine reads a flat +268 at 10, 100 and 1000 statements, so it does not
interact with routine length -- but all three files hold exactly ONE call, so
per-call and once-per-routine fit identically. Two calls and five calls split
them.

Run: python -m sample_gen.gen_oq_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

LOGIC_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
INSTR_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "instructions"

RUNGS = 1000


def _emit(sample_id: str, l5x: str, out_root: Path, description: str, category: str) -> None:
    path = out_root / f"{sample_id}.L5X"
    predicted = write_sample(l5x, path)
    append_manifest_row(sample_id, description, category, path, predicted)


# ---------------------------------------------------------------- ARM A
# Condition count x output count. Conditions are XIC on distinct bits so no
# duplicate-operand effect can be mistaken for a condition effect; outputs are
# OTE on distinct bits for the same reason. Both dimensions use the shapes the
# existing srout_* files already use, so every cell differences against them.
COND_COUNTS = (1, 2, 4)
OUT_COUNTS = (1, 2, 4, 8)


def arm_a_condition_by_output() -> int:
    n = 0
    for c in COND_COUNTS:
        for k in OUT_COUNTS:
            sample_id = f"sroutc_c{c:02d}_k{k:02d}_n{RUNGS:05d}"
            conds = "".join(f"XIC(C{i});"[:-1] for i in range(c))
            outs = "".join(f"OTE(Q{i});"[:-1] for i in range(k))
            text = f"{conds}{outs};"
            tags = "\n".join(
                [tag_xml(f"C{i}", "BOOL") for i in range(c)]
                + [tag_xml(f"Q{i}", "BOOL") for i in range(k)]
            )
            l5x = build_l5x(
                target_name=f"SroutC{c:02d}K{k:02d}",
                tags_xml=tags,
                extra_rungs_xml=rungs_xml(RUNGS, lambda _i, t=text: t),
            )
            _emit(
                sample_id, l5x, LOGIC_ROOT,
                f"{c} XIC condition(s) and {k} OTE output(s) in series, {RUNGS} identical "
                f"rungs. Arm A of the OQ-SERIESOUTPUT contradiction batch: the -12-per-extra-"
                f"output discount is byte-exact on all 16 srout_* rows and takes the sixteen "
                f"real programs from 1.7036% to 3.2167% when applied. Every srout_* rung has "
                f"exactly ONE condition; this varies condition count against output count so "
                f"a discount that only holds at one condition is separable from one that holds "
                f"always. Differences against srout_ote_k{k:02d}_n01000 at c=1.",
                "logic_instr",
            )
            n += 1
    return n


# ---------------------------------------------------------------- ARM B
# The three k=3 tier sequences the corpus lacks, written WITHOUT parentheses so
# they difference directly against cpttier_k3_t1x3/t2x3/t1x2_t2x1/t1x1_t2x2,
# which are also unparenthesised. Tier 1 is +/-, tier 2 is */÷.
MISSING_K3 = {
    "t211": "L0*L1+L2-L3",
    "t212": "L0*L1+L2*L3",
    "t221": "L0*L1/L2+L3",
}


def arm_b_cpt_tier_truth_table() -> int:
    n = 0
    tags = "\n".join([tag_xml("Dest", "DINT")] + [tag_xml(f"L{i}", "DINT") for i in range(5)])
    for seq, expr in MISSING_K3.items():
        sample_id = f"cpttri_k3_{seq}_n{RUNGS:05d}"
        l5x = build_l5x(
            target_name=f"CptTri{seq.upper()}",
            tags_xml=tags,
            extra_rungs_xml=rungs_xml(RUNGS, lambda _i, e=expr: f"CPT(Dest,{e});"),
        )
        _emit(
            sample_id, l5x, LOGIC_ROOT,
            f"CPT(Dest,{expr}) x {RUNGS} rungs -- tier sequence {seq[1:]}, one of the three "
            f"k=3 sequences of 8 the corpus lacks. Arm B of the OQ-CMPCPTLAYOUT truth table: "
            f"six measured shapes carry a flat +4 per rung and five do not, and the trigger is "
            f"not identified (tier-1 count, tier-2 count, operator count, parenthesisation, "
            f"tier-transition count and leading-tier-1 count each fail on at least one shape). "
            f"Completing all 8 sequences at fixed operator count reads the discriminant off a "
            f"full table. Differences against cpttier_k3_* directly.",
            "logic_instr",
        )
        n += 1
    # three adjacent ** -- separates adjacency from operator count
    sample_id = f"cpttri_pow_p3_adjacent_n{RUNGS:05d}"
    l5x = build_l5x(
        target_name="CptTriPow3Adj",
        tags_xml=tags,
        extra_rungs_xml=rungs_xml(RUNGS, lambda _i: "CPT(Dest,L0**L1**L2**L3);"),
    )
    _emit(
        sample_id, l5x, LOGIC_ROOT,
        f"CPT(Dest,L0**L1**L2**L3) x {RUNGS} rungs -- THREE adjacent ** operators. Arm B of "
        f"OQ-CMPCPTLAYOUT: cptpow_p2 reads -16/rung and cptpow_p2_adjacent +24/rung, so "
        f"adjacency is worth +40 at two operators, and two points cannot separate the "
        f"adjacency effect from the operator-count effect. Tier 3 is deliberately still on "
        f"the tier-1 fallback until it can.",
        "logic_instr",
    )
    return n + 1


def main() -> None:
    a = arm_a_condition_by_output()
    b = arm_b_cpt_tier_truth_table()
    print(f"Arm A (OQ-SERIESOUTPUT condition x output): {a}")
    print(f"Arm B (OQ-CMPCPTLAYOUT tier truth table):   {b}")
    print(f"Total: {a + b}")


if __name__ == "__main__":
    main()
