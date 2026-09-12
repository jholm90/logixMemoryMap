"""Dense count sweeps for the ZERO-OPERAND (non-tag) ladder instructions.
2026-09-12, OQ-VERIFINSTR.

Asked directly: were NOP, AFI, TND, UID and UIE tested? Partly, and the two
halves are in very different states.

  NOP and AFI: SOLVED. Five count points each (n = 10 / 50 / 100 / 1,000 /
  5,000) and every one reconciles at a flat -8 against the current engine --
  the universal per-file residual, not an instruction error. NOP = 16,
  AFI = 4 bytes each, confirmed over a 500x range.

  TND, UID, UIE and MCR: weights RIGHT but resting on TWO POINTS each.
  `instrfirst_<x>` and `instrfirst_<x>_x10` are all there is -- n = 1 and
  n = 10. Their slopes are exact at those two points (TND 216 bytes over 9
  extra instructions = 24 each; UID and UIE 360 over 9 = 40 each; MCR 144
  over 9 = 16 each, all matching the wired weights and the real bytes
  exactly), and all four sit at a flat -12 rather than a growing residual,
  so nothing is visibly wrong. But two points cannot distinguish a genuine
  per-instruction constant from a first-pass offset plus a different slope,
  and none of them has ever been measured above 10 instructions while NOP and
  AFI were checked to 5,000. That asymmetry is the gap, not a suspected bug.

Two groups, 25 files. A third was written and withdrawn -- see the section
marked NOT BUILT ON PURPOSE below, which is the more useful half of the answer.

  A. group_dense_counts -- TND, UID, UIE and MCR at the SAME count points NOP
     and AFI already have (10 / 50 / 100 / 1,000 / 5,000). This is the direct
     fix: it takes each from 2 points to 7 and over the same 500x range, so a
     weight that is really a first-pass artifact separates from a true
     per-instruction constant.

     5,000 is not arbitrary padding -- it is the count at which NOP and AFI
     were confirmed, so including it makes the two halves directly
     comparable rather than nearly comparable.

  B. group_uid_uie_paired -- UID and UIE measured as a PAIR.

     Group A sweeps them separately because that is how the existing two
     points were taken, but a bare UID with no matching UIE is not how either
     instruction is ever used: they bracket an uninterruptible region, and
     Studio may treat an unmatched one differently from a matched pair. If
     the paired cost is not simply UID + UIE then the separate sweeps are
     measuring something real Logix never does, and the corpus has no data
     either way. Swept at matched counts, plus one file with real
     instructions INSIDE the bracket to check the region's contents are not
     charged differently for being protected.

  C. EOT, SFR, SFP and IOT: real instructions, no weights entry, priced at
     zero today -- and NOT built here. See the NOT BUILT ON PURPOSE section in
     the code for why inventing their rung shapes would have shipped files
     that error.

Run: python -m sample_gen.gen_nontag_instruction_sweep
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, rungs_xml, tag_xml
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

# Same pool shape the instrfirst_* files use, so a new count point differences
# cleanly against the existing n=1/n=10 pair instead of against a new baseline.
_POOL_TAGS_XML = "\n".join([
    "\n".join(tag_xml(f"D{i}", "DINT") for i in range(4)),
    "\n".join(tag_xml(f"B{i}", "BOOL") for i in range(4)),
])

# The counts NOP and AFI were confirmed at.
DENSE_COUNTS = (10, 50, 100, 1000, 5000)


def _write(l5x: str, out_name: str, description: str) -> int:
    lint_or_raise(l5x, out_name)
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 1


def _file(instr: str, count: int, out_name: str, description: str,
          extra_tags: str = "") -> int:
    rungs = (rung_xml(0, instr) if count == 1
             else rungs_xml(count, lambda i, instr=instr: instr))
    tags = _POOL_TAGS_XML + ("\n" + extra_tags if extra_tags else "")
    l5x = build_l5x(target_name="NonTagSweep", tags_xml=tags, extra_rungs_xml=rungs)
    return _write(l5x, out_name, description)


# ---------------------------------------------------------------------------
# A. TND / UID / UIE / MCR at NOP and AFI's own count points
# ---------------------------------------------------------------------------

# (label, rung text, wired weight, what the existing 2 points already show)
DENSE_INSTRUCTIONS = (
    ("tnd", "TND();", 24,
     "216 bytes over 9 extra instructions = 24 each, matching the wired weight"),
    ("uid", "UID();", 40,
     "360 bytes over 9 extra instructions = 40 each, matching the wired weight"),
    ("uie", "UIE();", 40,
     "360 bytes over 9 extra instructions = 40 each, matching the wired weight"),
    ("mcr", "MCR();", 16,
     "144 bytes over 9 extra instructions = 16 each, matching the wired weight"),
)


def group_dense_counts() -> int:
    n = 0
    for label, instr, weight, evidence in DENSE_INSTRUCTIONS:
        for count in DENSE_COUNTS:
            n += _file(
                instr, count, f"ntag_{label}_n{count:05d}",
                f"{count} rungs of `{instr.rstrip(';')}`, nothing else -- OQ-VERIFINSTR "
                f"non-tag instruction density. {label.upper()}'s wired weight of {weight} "
                f"bytes rests on exactly TWO real points, instrfirst_{label} (n=1) and "
                f"instrfirst_{label}_x10 (n=10): {evidence}, and both sit at a flat -12 "
                f"residual rather than a growing one, so nothing looks wrong. Two points "
                f"still cannot separate a true per-instruction constant from a first-pass "
                f"offset plus a different slope. NOP and AFI were each confirmed at five "
                f"points out to n=5,000 and reconcile at a flat -8 across that whole 500x "
                f"range; these counts are deliberately the same ones so the two halves "
                f"become directly comparable")
    return n


# ---------------------------------------------------------------------------
# B. UID/UIE as the matched pair they really are
# ---------------------------------------------------------------------------

PAIR_COUNTS = (1, 10, 100, 1000)


def group_uid_uie_paired() -> int:
    n = 0
    for count in PAIR_COUNTS:
        # One rung per bracket: UID and UIE on the same rung is the smallest
        # matched form and keeps the rung count equal to the pair count.
        n += _file(
            "UID()UIE();", count, f"ntag_uidpair_n{count:05d}",
            f"{count} matched UID/UIE bracket(s), one pair per rung, nothing between them "
            f"-- OQ-VERIFINSTR UID/UIE pairing. Every existing point measures a BARE UID or "
            f"a bare UIE, which is not how either is used: they bracket an uninterruptible "
            f"region, and an unmatched one may well be treated differently from a matched "
            f"pair. If the paired cost is not simply UID + UIE ({40 + 40} bytes) then the "
            f"separate sweeps have been measuring a shape real Logix never contains. The "
            f"corpus has no data either way")
    n += _file(
        "UID()XIC(B0)OTE(B1)MOV(D0,D1)UIE();", 100, "ntag_uidpair_withbody_n00100",
        "100 matched UID/UIE brackets each enclosing real instructions (XIC/OTE/MOV) -- "
        "OQ-VERIFINSTR UID/UIE pairing, contents arm. Checks whether instructions inside an "
        "uninterruptible region cost the same as they do outside one. Differences against "
        "ntag_uidpair_n00100 (same 100 brackets, empty) isolate the body cost, and against "
        "the existing XIC/OTE/MOV count sweeps say whether being protected changes it")
    return n


# ---------------------------------------------------------------------------
# C. NOT BUILT ON PURPOSE: EOT, IOT, SFR, SFP
#
# These four are real Logix instructions, they have NO weights-table entry, and
# no sample in the corpus isolates any of them -- so every use costs zero today
# and that is a genuine gap. Files for them were written and then deliberately
# withdrawn, for a reason worth recording rather than rediscovering:
#
#   - lint.py rejects all four as unrecognized instructions, which is itself
#     accurate: the project has never verified a real rung containing one.
#   - SFR(routine, step) and SFP(routine, step) address an SFC routine BY NAME.
#     This project's builders produce no SFC routines, so a file using them
#     would name a routine that does not exist and Studio would reject the
#     rung -- and a rejected rung still imports the rest of the project and
#     still fills in actual_bytes, which is how a capture ends up measuring a
#     project missing part of its content.
#   - IOT's operand is a real output module reference, not a plain DINT, and
#     EOT's is an SFC storage bit. Both invented shapes are a guess.
#
# CLAUDE.md's rule is transplant, never compose -- a rung shape comes verbatim
# from a real or verified export, because inventing shapes has already cost this
# project time three times. So the correct next step for these four is a
# verified rung apiece, not a synthesized one. Recorded in
# docs/INSTRUCTION_COVERAGE.md.
#
# EVENT is separately excluded: it is the last unpriced instruction in the real
# corpus, it already has closeout files under OQ-EVENTTRIGGER, and a second set
# here would split one question's data across two batches.
# ---------------------------------------------------------------------------


def main() -> None:
    total = 0
    for fn in (group_dense_counts, group_uid_uie_paired):
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
