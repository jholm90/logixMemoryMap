"""OQ-JSRPARAMCOST: extends gen_jsr_multi_distinct_targets.py (which only
covered N=1/3/5) to real-scale distinct-target COUNTS, and separately
isolates target-routine NAME LENGTH as its own variable -- both flagged as
missing by James, 2026-08-31: "You should have 5/10/15/20/50 subroutines
to test quantity and different routine name lengths in another test set
for validation of that data that was missed."

report.py's jsr_target_param_counts mechanism (dict keyed by target name,
each charged A(n) once) has no name-length term at all today -- unlike
tags/UDTs/AOI definitions, which all have a real, empirically-confirmed
name-length bucket cost (see memory_model.yaml aoi_definition.name_length_
bucket_bytes etc.). Whether JSR-target routine names carry the same kind
of real cost has never been tested, because every JSR calibration file
built to date (old corpus and this session's new ones) used short, roughly
fixed-length target names.

Two groups:

  A. group_quantity_scale -- N_TARGETS = 5/10/15/20/50 distinct 0-param
     leaf targets (same shape as gen_jsr_multi_distinct_targets.py: no
     SBR/RET, one JSR rung per target, single MainRoutine caller), name
     LENGTH held fixed across every file (a constant-width zero-padded
     template) so any Capacity change across this sweep is attributable
     to COUNT alone, continuing the straight-line check from N=1/3/5
     (18572/18932/19292, +180/target) out to real-project scale --
     AccuTally's busiest caller routines invoke well into double digits
     of distinct subroutines.

  B. group_name_length -- distinct-target COUNT held fixed at 10, target
     routine name LENGTH swept (4/8/16/32/48 chars) instead, isolating
     whether name length alone carries a real per-target cost the way it
     does for tags/UDTs/AOI definitions.

Run: python -m sample_gen.gen_jsr_multi_distinct_targets_scale
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

N_TARGETS_SCALE = (5, 10, 15, 20, 50)
NAME_LENGTHS = (4, 8, 16, 32, 48)
FIXED_COUNT_FOR_NAMELEN = 10


def _padded_name(prefix: str, i: int, total_length: int, index_width: int) -> str:
    # Valid Logix identifier: starts with a letter, only [A-Za-z0-9_].
    # Pads with filler to hit an EXACT total length so name-length is a
    # clean single variable, never guessed/approximate. The zero-padded
    # index is always kept INTACT (never truncated) so every name in a
    # group stays genuinely unique even at short total_length -- an
    # earlier draft truncated a longer "prefix+_+index" suffix down to
    # total_length, which silently collapsed all 10 length=4 names to
    # the identical string "T_00", producing a file with 10 duplicate
    # <Routine Name="T_00"> elements instead of 10 distinct routines
    # (caught by comparing predicted bytes: namelen04 didn't fit the
    # pattern of namelen08/16/32/48, which were all identical to each
    # other -- a real generator bug, not a modeling finding).
    idx = str(i).zfill(index_width)
    fill_len = max(total_length - len(prefix) - len(idx), 0)
    name = f"{prefix}{'X' * fill_len}{idx}"
    if len(name) > total_length:
        keep = max(total_length - len(idx), 1)
        name = f"{prefix[:keep]}{idx}"
    return name


def _target_xml(name: str) -> str:
    # 0-param leaf target, no SBR/RET -- real corpus norm for 0-param
    # targets (James, 2026-08-31; confirmed against samples/local/).
    return (
        f'<Routine Name="{name}" Type="RLL">'
        f"<RLLContent>{rung_xml(0, 'NOP();')}</RLLContent>"
        "</Routine>"
    )


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "jsr_sbr_ret", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_quantity_scale() -> None:
    for n in N_TARGETS_SCALE:
        target_names = [_padded_name("JsrScaleTgt", i, 16, index_width=2) for i in range(n)]
        targets_xml = "\n".join(_target_xml(t) for t in target_names)
        call_rungs = "\n".join(rung_xml(i, f"JSR({t},0);") for i, t in enumerate(target_names))
        l5x = build_l5x(
            target_name=f"JsrScaleN{n:02d}", tags_xml="",
            extra_rungs_xml=call_rungs, extra_routines_xml=targets_xml,
        )
        _write(
            f"jsr_multi_distinct_targets_n{n:02d}",
            l5x,
            f"MainRoutine calls {n} genuinely DISTINCT 0-param leaf subroutines, fixed 16-char "
            f"target name length across every file in this group -- OQ-JSRPARAMCOST distinct-"
            f"target-COUNT scale isolation (extends jsr_multi_distinct_targets_{{01,03,05}} out "
            f"to real-project scale, James 2026-08-31: 'test quantity ... in another test set "
            f"for validation of that data that was missed'). Straight-line check: does the "
            f"already-confirmed +180 bytes/target from N=1/3/5 keep holding at N={n}, or does "
            f"real Capacity diverge from linear at scale?",
        )


def group_name_length() -> None:
    for length in NAME_LENGTHS:
        target_names = [
            _padded_name("T", i, length, index_width=1) for i in range(FIXED_COUNT_FOR_NAMELEN)
        ]
        targets_xml = "\n".join(_target_xml(t) for t in target_names)
        call_rungs = "\n".join(rung_xml(i, f"JSR({t},0);") for i, t in enumerate(target_names))
        l5x = build_l5x(
            target_name=f"JsrNameLen{length:02d}", tags_xml="",
            extra_rungs_xml=call_rungs, extra_routines_xml=targets_xml,
        )
        _write(
            f"jsr_multi_distinct_targets_namelen{length:02d}",
            l5x,
            f"MainRoutine calls a FIXED {FIXED_COUNT_FOR_NAMELEN} genuinely distinct 0-param "
            f"leaf subroutines, target routine name length held at exactly {length} chars across "
            f"every file in this group (count is the only thing held constant here, unlike "
            f"group_quantity_scale) -- OQ-JSRPARAMCOST target-NAME-LENGTH isolation, James "
            f"2026-08-31: 'different routine name lengths in another test set for validation of "
            f"that data that was missed'. report.py's jsr_target_param_counts A(n) charge has no "
            f"name-length term today, unlike tags/UDTs/AOI definitions (all confirmed real "
            f"name-length bucket costs) -- tests whether that's a real, currently-unmodeled gap "
            f"or genuinely free the way routine logic content itself is not.",
        )


def main() -> None:
    group_quantity_scale()
    group_name_length()
    print("\nDone. 10 files.")


if __name__ == "__main__":
    main()
