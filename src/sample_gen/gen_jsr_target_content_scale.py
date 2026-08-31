"""OQ-JSRPARAMCOST: does JSR-target CONTENT cost actually stay folded into
jsr_fixed_base_per_routine at real scale? (2026-08-31, James: real AccuTally
review, "still out by 18%" -- and "if i get a test result that doesnt match
my prediction i usually check my existing work and devise new tests to
fix it.")

The "a JSR target routine's own CONTENT cost is already folded into the
caller's jsr_fixed_base_per_routine constant" finding (report.py,
confirmed 2026-08-22) is real, but EVERY JSR-target test file this project
has ever built (gen_jsr_sbr_ret.py, gen_jsr_decompose.py, gen_jsr_
paramcost_closeout.py, gen_jsr_paramtype_isolation*.py) uses the exact
same trivial target shape: `SBR(...)NOP();RET();` -- 2-3 instructions,
nothing else. That confirmation has never been tested against a target
routine with REAL substantial logic content.

Real AccuTally data (confidential, not committed) makes this urgent: 123
of its 142 real JSR-target routines average 85 real instructions each (one
has 201) -- 10,488 total real instruction occurrences currently contribute
ZERO bytes beyond the flat one-time jsr_fixed_base_per_routine/A(n)
constants. If target content really is free beyond a certain point (e.g.
Logix compiles the subroutine's own logic into the SAME per-routine slot
regardless of size, unlike a plain routine), current behavior is right and
Capacity should stay FLAT across this sweep. If it isn't free, Capacity
should scale with the target's own instruction count, proving a real,
currently-unmodeled cost this project has been silently zeroing out on
every real project since 2026-08-22 -- a plausible major piece of the
18% AccuTally gap, since routine content this large dwarfs every other
open residual bucket combined.

4 files, target-routine instruction count as the only variable (10/50/
100/150 real instructions, a realistic mix matching AccuTally's own top
mnemonics: MOV/XIC/OTE/CLR/ADD/EQU), single call site, single distinct
target, everything else held fixed and minimal so any Capacity change is
unambiguously attributable to target content size alone.

Run: python -m sample_gen.gen_jsr_target_content_scale
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

LOGIC_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

TARGET_INSTR_COUNTS = (10, 50, 100, 150)

# Realistic mix matching AccuTally's own real top mnemonics (MOV/XIC/OTE/
# CLR/ADD/EQU dominate its 123 real JSR-target routines) -- cycled to hit
# the requested instruction count exactly.
_MIX = ["MOV({t}0,{t}1)", "XIC({t}2)OTE({t}3)", "CLR({t}4)", "ADD({t}5,{t}6,{t}7)", "EQU({t}8,{t}9)"]


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = LOGIC_OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "jsr_sbr_ret", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def main() -> None:
    for instr_count in TARGET_INSTR_COUNTS:
        target_name = f"JsrTargetContentScale{instr_count:03d}Target"
        sbr_rung = rung_xml(0, "SBR()NOP();")
        pieces = []
        rung_idx = 1
        total = 0
        while total < instr_count:
            piece = _MIX[(rung_idx - 1) % len(_MIX)]
            n_instr_this_piece = piece.count("(")
            text = piece.format(t="TC") + ";"
            pieces.append(rung_xml(rung_idx, text))
            total += n_instr_this_piece
            rung_idx += 1
        ret_rung = rung_xml(rung_idx, "RET();")
        target_xml = (
            f'<Routine Name="{target_name}" Type="RLL">'
            f"<RLLContent>{sbr_rung}\n" + "\n".join(pieces) + f"\n{ret_rung}</RLLContent>"
            "</Routine>"
        )

        tc_tags = "\n".join(tag_xml(f"TC{i}", "DINT") for i in range(10))
        call_rung = rung_xml(0, f"JSR({target_name},0);")
        l5x = build_l5x(
            target_name=f"JsrTargetContentScale{instr_count:03d}", tags_xml=tc_tags,
            extra_rungs_xml=call_rung, extra_routines_xml=target_xml,
        )
        _write(
            f"jsr_target_content_scale_{instr_count:03d}",
            l5x,
            f"JSR to a single target routine containing ~{instr_count} real instructions "
            f"(realistic MOV/XIC/OTE/CLR/ADD/EQU mix matching AccuTally's real JSR-target "
            f"composition), single call site, 0 params -- OQ-JSRPARAMCOST target-content-scale "
            f"isolation: does the target's own logic content really stay folded into the flat "
            f"jsr_fixed_base_per_routine cost at real scale, or does Capacity actually grow with "
            f"target size (a real, currently-unmodeled cost this project has silently zeroed out "
            f"since 2026-08-22, confirmed only against trivial SBR/NOP/RET stub targets)?",
        )


if __name__ == "__main__":
    main()
