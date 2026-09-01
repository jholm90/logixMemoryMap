"""OQ-JSRPARAMCOST: does JSR-target CONTENT cost actually stay folded into
jsr_fixed_base_per_routine at real scale? (2026-08-31, James: real AccuTally
review, "still out by 18%" -- and "if i get a test result that doesnt match
my prediction i usually check my existing work and devise new tests to
fix it.")

The "a JSR target routine's own CONTENT cost is already folded into the
caller's jsr_fixed_base_per_routine constant" finding (report.py,
confirmed 2026-08-22) is real, but EVERY JSR-target test file this project
has ever built (gen_jsr_sbr_ret.py, gen_jsr_decompose.py, gen_jsr_
paramcost_closeout.py, gen_jsr_paramtype_isolation*.py) calls its target
with a NONZERO param count (1/5/7/8/9/10/15) and always includes SBR/RET.
That's real and representative for the nonzero-param case: checked
against every real L5X already in samples/local/ (2,534 unique real JSR
targets across 8 genuine customer files), 126/128 nonzero-param targets
DO have a real SBR instruction.

James, 2026-08-31, real, caught in review: "if there was no jsr parameters
then there is no sbr/ret instructions inside the called subroutine." Also
confirmed against the same real corpus: 2,314/2,315 ZERO-param targets
have NO SBR at all, and 2,218/2,315 (95.8%) have no RET either. This
file's first draft called its target with 0 params but still forced
SBR()/RET() into it -- a real generator bug, not representative of any
real 0-param subroutine, now fixed by omitting both. This matters more
than it might look: AccuTally's real JSR calls are 77% zero-param
(117/152), and every one of its real 0-param targets has zero SBR/RET,
matching the corpus norm exactly.

4 files, target-routine instruction count as the only variable (10/50/
100/150 real instructions, a realistic mix matching AccuTally's own top
mnemonics: MOV/XIC/OTE/CLR/ADD/EQU), single call site, 0 params, no SBR/
RET (the representative real shape for a 0-param target), single distinct
target, everything else held fixed and minimal so any Capacity change is
unambiguously attributable to target content size alone. If target
content really is free beyond jsr_fixed_base_per_routine even in this
correctly-shaped case, current behavior is right and Capacity should stay
FLAT across this sweep; if it isn't free, Capacity should scale with the
target's own instruction count -- a real, currently-unmodeled cost this
project has silently zeroed out on every real project since 2026-08-22,
a plausible major piece of the 18% AccuTally gap since 10,488 real
unweighted instructions dwarfs every other open residual bucket combined.

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
#
# James, 2026-08-31, real, caught on his own re-conversion: "SINT/INT/DINT
# cannot be used for bit level instructions like XIO,XIC,OTE,OTU,OTL,ONS
# only bools and .Bits of SINT/INT/DINT" -- TC0-9 are all DINT (see
# tc_tags below), so the original "XIC({t}2)OTE({t}3)" referenced whole
# DINT tags with no bit subscript, invalid. Also: "conditional instructions
# like EQU with no operand at the end of the rung or a NOP() instruction"
# -- the original bare "EQU({t}8,{t}9)" had no output instruction, also
# invalid. Both fixed: XIC/OTE now bit-subscript (.0), EQU now ends in a
# real output instruction.
_MIX = ["MOV({t}0,{t}1)", "XIC({t}2.0)OTE({t}3.0)", "CLR({t}4)", "ADD({t}5,{t}6,{t}7)", "EQU({t}8,{t}9)OTE({t}3.0)"]


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = LOGIC_OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "jsr_sbr_ret", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def main() -> None:
    for instr_count in TARGET_INSTR_COUNTS:
        target_name = f"JsrTargetContentScale{instr_count:03d}Target"
        # No SBR, no RET -- the real, representative shape for a 0-param
        # JSR target (James, 2026-08-31; confirmed 99.96%/95.8% against
        # the real corpus in samples/local/). The target routine is just
        # ordinary logic rungs, same as any plain routine.
        pieces = []
        rung_idx = 0
        total = 0
        while total < instr_count:
            piece = _MIX[rung_idx % len(_MIX)]
            n_instr_this_piece = piece.count("(")
            text = piece.format(t="TC") + ";"
            pieces.append(rung_xml(rung_idx, text))
            total += n_instr_this_piece
            rung_idx += 1
        target_xml = (
            f'<Routine Name="{target_name}" Type="RLL">'
            f"<RLLContent>" + "\n".join(pieces) + "</RLLContent>"
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
            f"composition), single call site, 0 params, NO SBR/RET (the real, representative "
            f"shape for a 0-param target, James 2026-08-31 -- confirmed against the real corpus "
            f"in samples/local/, 99.96% of real 0-param targets have no SBR) -- OQ-JSRPARAMCOST "
            f"target-content-scale isolation: does the target's own logic content really stay "
            f"folded into the flat jsr_fixed_base_per_routine cost at real scale, or does "
            f"Capacity actually grow with target size (a real, currently-unmodeled cost this "
            f"project has silently zeroed out since 2026-08-22, confirmed only against trivial "
            f"SBR/NOP/RET stub targets with nonzero params)?",
        )


if __name__ == "__main__":
    main()
