"""REAL-SCALE composite surcharge: the batch that targets the -12.4% miss on
the first real virgin file (James, 2026-09-04: "youve made some more unique
tests to fix this 12% error?").

Why this batch exists
---------------------
`Cardin_TrimSortStack_20260624r00` (1756-L83E, fw 35.13, never seen by this
project) predicted 7,162,455 against a real 8,178,556 -- 12.4% UNDER, the
honest North Star number. The measured cause is not a mystery: the file-wide
`logic_instructions.composite_surcharge_cap` (12,000 bytes) suppresses
1,551,065 bytes on that file alone. The cap was fitted against the synthetic
composite corpus, and that corpus cannot reach the regime a real program
lives in:

| file                       | aoi_instr | jsr_instr | uncapped surcharge | vs cap |
|----------------------------|----------:|----------:|-------------------:|-------:|
| REAL Cardin_TrimSortStack  |     6,255 |    30,595 |          1,563,065 | 130.3x |
| synthetic v4_074           |       450 |     1,899 |             98,253 |   8.2x |
| synthetic v2_25            |       111 |       120 |              7,860 |   0.7x |

So the cap is doing mild trimming on everything it was fitted against and
total annihilation on a real program. Capped gives -12.4%; fully uncapped
gives +6.5%. The value that lands exactly on that one file is ~66% of
uncapped -- ONE data point, which must NOT be fitted on its own (the
axis_scale lesson, see docs/TESTING_PLAN.md). What is needed is the SHAPE of
the law across the whole range, measured, and that is what this batch buys.

Design rule that makes this batch different
-------------------------------------------
Every file here is built from rung text taken VERBATIM from
gen_logic_sweep.INSTRUCTIONS against its shared `_POOL_TAGS_XML`. That is
deliberate, not convenience:

  * It is the only large-scale shape in this corpus with a proven
    error-free build -- `randommix_05_n27267rungs_23types` (27,267 rungs,
    error_count 0) and the whole `instr_*_n05000` sweep are built from it.
  * The previous attempt at this question, `jsr_target_content_scale_*`,
    used its own hand-rolled TC-tag mix and came back with 5/26/50/75 build
    errors, so none of its four rows is a valid fitting point. The cause of
    those errors is still genuinely undiagnosed -- this file does not guess
    at it, it routes around it by using shapes already proven at 5,000
    rungs. If these files ALSO error, that is itself the diagnostic: it
    would mean JSR-target/AOI-internal PLACEMENT is what Studio 5000
    objects to, not the instruction shapes, which is something no existing
    row can tell us apart.

GROUPS
------
A. group_jsr_placement_ladder (8 files) -- THE MAIN EVENT
   n rungs of `XIC(Bi)OTE(Bi+1)` moved out of MainRoutine and into a single
   JSR target, n = 10/50/100/1000/5000/10000/15000/22500. The first five n
   values are EXACTLY the counts of the existing `instr_xic_n*` sweep, all
   of which are valid error-free captures (e.g. instr_xic_n05000 = 122,944).
   That makes each of those five a genuine PAIRED measurement: identical
   rung text, identical tag pool, identical everything, the only difference
   being whether the rungs sit in MainRoutine or behind a JSR. The
   difference IS the JSR-target cost, measured directly, with no model in
   the middle. The top three extend the ladder to 45,000 target instructions
   -- past the real file's 30,595 -- so the law can be read at real scale
   instead of extrapolated to it. Uncapped surcharge spans 0.08x to 176x the
   12,000 cap.

B. group_jsr_target_count_split (3 files)
   The cap is modelled as FILE-WIDE over total surcharge-eligible
   instructions. Nothing has ever tested whether that is right, because
   every existing file has one target. These hold total target content
   fixed at 10,000 rungs / 20,000 instructions and split it across
   K = 10/50/250 distinct target routines. If the cost really is per
   instruction file-wide, all three land on group A's n=10000 file plus the
   already-exact +125/distinct-target term; if it is per routine, they
   diverge from it in proportion to K.

C. group_aoi_internal_ladder (6 files)
   The other half of the surcharge (`aoi_logic_composite_surcharge_per_instr`
   = 20/instr) has the identical problem and no real-scale data at all. One
   AOI, fixed parameter/local shape, single instance, internal Logic routine
   carrying n = 0/50/500/2000/6000/12000 rungs of the same proven XIC/OTE
   shape over BOOL locals. No JSR targets anywhere in these files, so the
   AOI term is isolated from the JSR term for the first time. n=6000
   (12,000 AOI instructions) brackets the real file's 6,255.

D. Structured Text -- MOVED OUT to gen_st_sizing.py, 2026-09-04.
   The first draft of this batch carried a naive ST ladder written from
   general knowledge with only its FOR shape copied from a real file.
   James, same day: "I hope you are going to be able to write st language
   based on your knowledge and skills, not just tossing lines and hope they
   stick... can you extract enough from the sample code like bender and
   some of the aois." Measuring the corpus first (297 real ST routines,
   24,017 lines across 23 files in samples/local/) showed that ladder was
   not representative of anything real -- 100% plain assignments, where
   real ST is ~36% control flow, ~29% comments, and calls the same
   instructions the ladder does. See gen_st_sizing.py, which replaces it
   and keeps the same realscale_st_n* file names.

Run: python -m sample_gen.gen_realscale_surcharge
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml
from sample_gen.gen_logic_sweep import INSTRUCTIONS, _POOL_TAGS_XML
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

LOGIC_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
AOI_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"

# Verbatim from gen_logic_sweep -- "XIC(Bi)OTE(Bi+1);", 2 instructions per
# rung, proven error-free at 5,000 rungs (instr_xic_n05000) and as part of
# the 27,267-rung randommix_05. Nothing here re-invents an operand shape.
_XIC_RUNG = INSTRUCTIONS["XIC"]


def _rungs(count: int, text_fn=_XIC_RUNG, start: int = 0) -> str:
    return "\n".join(rung_xml(i, text_fn(start + i)) for i in range(count))


def _write(out_dir: Path, out_name: str, l5x: str, category: str, description: str) -> None:
    out_path = out_dir / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, category, out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


# --- A. JSR-target placement ladder -----------------------------------------

# 10/50/100/1000/5000 are EXACTLY gen_logic_sweep.COUNTS, so each pairs with
# an existing valid instr_xic_n* capture; 10000/15000/22500 push past the
# real file's 30,595 JSR-target instructions (22500 rungs = 45,000).
_A_COUNTS = (10, 50, 100, 1000, 5000, 10000, 15000, 22500)


def group_jsr_placement_ladder() -> None:
    for n in _A_COUNTS:
        target = f'<Routine Name="XicTarget" Type="RLL"><RLLContent>{_rungs(n)}</RLLContent></Routine>'
        l5x = build_l5x(
            target_name=f"RsJsrPlace{n:05d}", tags_xml=_POOL_TAGS_XML,
            extra_rungs_xml=rung_xml(0, "JSR(XicTarget,0);"),
            extra_routines_xml=target,
        )
        _write(
            LOGIC_OUT, f"realscale_jsrtgt_xic_n{n:05d}", l5x, "jsr_sbr_ret",
            f"{n} rungs of XIC(Bi)OTE(Bi+1) -- byte-for-byte the same rung text and tag "
            f"pool as instr_xic_n{n:05d}, but moved OUT of MainRoutine and INTO a single "
            f"0-param JSR target called once. Paired difference against that existing valid "
            f"capture measures the real JSR-target content cost directly, with no model in "
            f"between. Uncapped composite surcharge here is {2 * n * 47:,} bytes vs the "
            f"12,000 file-wide cap ({2 * n * 47 / 12000:.2f}x) -- the ladder spans from below "
            f"the cap to well past the real Cardin_TrimSortStack file's 30,595 JSR-target "
            f"instructions, the regime that produced this project's -12.4% real-file miss.",
        )


# --- B. Same total content, split across K distinct targets -----------------

_B_TOTAL_RUNGS = 10000  # matches group A's n=10000 file exactly
_B_TARGET_COUNTS = (10, 50, 250)


def group_jsr_target_count_split() -> None:
    for k in _B_TARGET_COUNTS:
        per = _B_TOTAL_RUNGS // k
        routines = []
        calls = []
        for t in range(k):
            name = f"SplitTgt{t:04d}"
            routines.append(
                f'<Routine Name="{name}" Type="RLL"><RLLContent>'
                f"{_rungs(per, start=t * per)}</RLLContent></Routine>"
            )
            calls.append(rung_xml(t, f"JSR({name},0);"))
        l5x = build_l5x(
            target_name=f"RsJsrSplit{k:04d}", tags_xml=_POOL_TAGS_XML,
            extra_rungs_xml="\n".join(calls), extra_routines_xml="\n".join(routines),
        )
        _write(
            LOGIC_OUT, f"realscale_jsrsplit_k{k:04d}", l5x, "jsr_sbr_ret",
            f"{_B_TOTAL_RUNGS} rungs of XIC(Bi)OTE(Bi+1) ({2 * _B_TOTAL_RUNGS} instructions) "
            f"split evenly across {k} DISTINCT 0-param JSR targets ({per} rungs each), one "
            f"call site per target. Total target content is identical to "
            f"realscale_jsrtgt_xic_n{_B_TOTAL_RUNGS:05d}, so the only variable is how many "
            f"routines it is spread over. The composite surcharge is currently modelled as "
            f"per-instruction FILE-WIDE -- if that is right these land on the single-target "
            f"file plus the already-exact +125 bytes per additional distinct target; if the "
            f"real cost is per-ROUTINE they diverge in proportion to {k}.",
        )


# --- C. AOI internal-logic ladder -------------------------------------------

_C_COUNTS = (0, 50, 500, 2000, 6000, 12000)
# BOOL locals only, and the rung text is the same XIC/OTE shape as everywhere
# else in this file -- an AOI's internal logic can only reach its own
# Parameters/LocalTags, never the controller tag pool.
_AOI_LOCAL_BOOLS = 10


def _aoi_internal_rungs(count: int) -> str:
    def text(i: int) -> str:
        return f"XIC(Loc{i % _AOI_LOCAL_BOOLS})OTE(Loc{(i + 1) % _AOI_LOCAL_BOOLS});"
    return "".join(rung_xml(i, text(i)) for i in range(count))


def group_aoi_internal_ladder() -> None:
    # def_only (0 instances), the same shape as the existing aoi_logic_scale_*
    # ladder this extends -- its n=0 file is a valid error-free capture
    # (19,440) and the surcharge is computed from the DEFINITION's internal
    # logic, so an instance tag would only add unrelated storage cost.
    inputs = [MemberSpec("In0", "DINT"), MemberSpec("In1", "DINT"), MemberSpec("In2", "BOOL")]
    outputs = [MemberSpec("Out0", "BOOL")]
    locals_ = [MemberSpec(f"Loc{i}", "BOOL") for i in range(_AOI_LOCAL_BOOLS)]
    for n in _C_COUNTS:
        definition, _ = aoi_xml(
            "RsAoiInternal", inputs, outputs, [], locals_,
            logic_rungs_xml=_aoi_internal_rungs(n),
        )
        l5x = build_l5x(target_name=f"RsAoiInt{n:05d}", tags_xml="", extra_aoi_xml=definition)
        _write(
            AOI_OUT, f"realscale_aoiint_n{n:05d}", l5x, "aoi",
            f"One AOI definition, fixed 3-input/1-output/{_AOI_LOCAL_BOOLS}-BOOL-local "
            f"declaration shape, 0 instances, internal Logic routine carrying {n} rungs "
            f"({2 * n} instructions) of XIC(Loci)OTE(Loci+1) over its own BOOL locals. "
            f"NO JSR target anywhere in the file, so this isolates "
            f"aoi_logic_composite_surcharge_per_instr (20/instr, uncapped "
            f"{2 * n * 20:,} bytes = {2 * n * 20 / 12000:.2f}x the 12,000 file-wide cap) from "
            f"the JSR half for the first time. n=6000 brackets the real Cardin_TrimSortStack "
            f"file's 6,255 AOI-internal instructions; the existing aoi_logic_scale_* ladder "
            f"stopped at 100 instructions AND built with errors at every nonzero point, so "
            f"no valid AOI-content data point above zero exists today.",
        )


def main() -> None:
    group_jsr_placement_ladder()
    group_jsr_target_count_split()
    group_aoi_internal_ladder()
    print("\nDone. 17 files.")


if __name__ == "__main__":
    main()
