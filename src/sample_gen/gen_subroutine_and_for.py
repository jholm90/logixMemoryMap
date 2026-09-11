"""Weights for the last three unpriced instructions a real file reaches.

SBR, RET and FOR are charged ZERO today, which is an absence of data
rather than a measurement. AccuTally alone calls RET 27 times and SBR 20,
so this is not a corner case: it is a silent under-charge on every real
program that uses subroutines, which is most of them.

Every other instruction in this project was fitted by differencing
consecutive count points so the shared per-file base cancels. These three
cannot use the plain single-rung-per-count shape that the rest of the
`verifinstr_*` batch uses, because none of them is a free-standing rung:

  SBR / RET  are the entry and exit markers of a SUBROUTINE routine. A
             routine has at most one SBR (first rung) and one RET, so
             "1,000 SBRs in a routine" is not a legal project. The count
             axis has to be the number of ROUTINES, not the number of
             rungs, and each added routine also drags in a routine shell
             whose cost is already separately KNOWN -- which is why this
             generator pairs every SBR/RET file with a routine-shell-only
             control at the same routine count. Differencing the pair
             cancels the shell and leaves the marker cost alone.

  FOR        is a loop header bound to a target routine, so a FOR file
             needs that routine to exist. Same treatment: paired against
             a control carrying the identical target routines and JSR-free
             shells, so the difference is the FOR instruction itself.

Three axes, each swept at 1/5/25/100 routines, on 1756-L81E v35.

GROUP A -- subrtn_sbronly_r{N} / subrtn_shell_r{N}
    N extra subroutine-type routines, each containing a single SBR rung,
    against N routines containing a single NOP. The difference is N SBRs.

GROUP B -- subrtn_sbrret_r{N}
    The same N routines carrying SBR and RET. Against group A the
    difference is N RETs; against the shell control it is N of the pair.
    Both readings are available, which is the cross-check.

GROUP C -- forloop_for_r{N} / forloop_ctl_r{N}
    N FOR rungs each targeting its own routine, against N JSR rungs
    targeting the identical routines. JSR is already priced exactly, so
    the difference isolates FOR against a known quantity rather than
    against zero.

Run: python -m sample_gen.gen_subroutine_and_for
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rungs_xml, tag_xml
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
COUNTS = (1, 5, 25, 100)
CATEGORY = "subroutine_for"


def _routine_xml(name: str, rungs: list[str], routine_type: str = "RLL") -> str:
    body = "".join(
        f'<Rung Number="{i}" Type="N"><Text><![CDATA[{text}]]></Text></Rung>\n'
        for i, text in enumerate(rungs)
    )
    return (
        f'<Routine Name="{name}" Type="{routine_type}">\n'
        f"<RLLContent>\n{body}</RLLContent>\n</Routine>\n"
    )


def _emit(out_name: str, description: str, *, routines_xml: str = "",
          rungs: str = "", tags_xml: str = "") -> int:
    l5x = build_l5x(
        target_name="".join(p.capitalize() for p in out_name.split("_")),
        tags_xml=tags_xml,
        extra_rungs_xml=rungs,
        extra_routines_xml=routines_xml,
    )
    out_path = OUT_ROOT / f"{out_name}.L5X"
    lint_or_raise(l5x, context=str(out_path))
    out_path.write_text(l5x, encoding="utf-8")
    append_manifest_row(out_name, description, CATEGORY, out_path, 0)
    print(f"Wrote {out_path}")
    return 1


def _routine_name(i: int) -> str:
    return f"SubR{i:03d}"


def group_a_sbr_and_shell() -> int:
    n = 0
    for count in COUNTS:
        shell = "".join(_routine_xml(_routine_name(i), ["NOP();"]) for i in range(count))
        shell2 = "".join(_routine_xml(_routine_name(i), ["NOP();", "NOP();"]) for i in range(count))
        n += _emit(
            f"subrtn_shell_r{count:03d}",
            f"{count} extra RLL routine(s), one NOP rung each, no SBR or RET -- the "
            f"routine-shell control. Its whole job is to be differenced away: the "
            f"routine shell cost is separately KNOWN, so subtracting this from "
            f"subrtn_sbronly_r{count:03d} leaves the SBR markers by themselves",
            routines_xml=shell,
        )
        # NOP terminates the rung, same rule DTR needed: a marker
        # instruction is a pure condition and cannot end a rung alone.
        # The control arm carries the identical NOP, so it cancels.
        sbr = "".join(_routine_xml(_routine_name(i), ["SBR();NOP();"]) for i in range(count))
        n += _emit(
            f"subrtn_sbronly_r{count:03d}",
            f"{count} extra RLL routine(s), a single SBR rung each. SBR is a routine "
            f"ENTRY marker, so the count axis has to be routines rather than rungs -- "
            f"a routine cannot hold two of them. Differenced against "
            f"subrtn_shell_r{count:03d} to remove the shell",
            routines_xml=sbr,
        )
    return n


def group_b_sbr_with_ret() -> int:
    n = 0
    for count in COUNTS:
        both = "".join(
            _routine_xml(_routine_name(i), ["SBR();NOP();", "RET();NOP();"])
            for i in range(count)
        )
        n += _emit(
            f"subrtn_sbrret_r{count:03d}",
            f"{count} extra RLL routine(s) carrying both SBR and RET. Two readings "
            f"come out of this: against subrtn_sbronly_r{count:03d} the difference is "
            f"{count} RETs, and against subrtn_shell_r{count:03d} it is {count} of the "
            f"pair. The two must agree, which is the cross-check on both weights",
            routines_xml=both,
        )
    return n


def group_c_for_loop() -> int:
    n = 0
    for count in COUNTS:
        targets = "".join(_routine_xml(f"Loop{i:03d}", ["NOP();"]) for i in range(count))
        for_rungs = rungs_xml(count, lambda i: f"FOR(Loop{i:03d},Idx,0,10,1);")
        jsr_rungs = rungs_xml(count, lambda i: f"JSR(Loop{i:03d},0);")
        n += _emit(
            f"forloop_ctl_r{count:03d}",
            f"{count} JSR rungs against {count} target routines -- the control arm. JSR "
            f"is already priced exactly, so differencing this from forloop_for_r"
            f"{count:03d} isolates FOR against a known quantity instead of against zero",
            routines_xml=targets, rungs=jsr_rungs, tags_xml=tag_xml("Idx", "DINT"),
        )
        n += _emit(
            f"forloop_for_r{count:03d}",
            f"{count} FOR rungs, each looping its own target routine 0..10 step 1. FOR "
            f"is a loop header bound to a routine, so the target routines have to exist "
            f"-- they are identical in the control arm and cancel on differencing",
            routines_xml=targets, rungs=for_rungs, tags_xml=tag_xml("Idx", "DINT"),
        )
    return n


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    total = 0
    for fn in (group_a_sbr_and_shell, group_b_sbr_with_ret, group_c_for_loop):
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
