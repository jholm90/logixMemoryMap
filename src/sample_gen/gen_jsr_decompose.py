"""Targeted 2-file follow-up (2026-08-26) to close OQ-JSRPARAMCOST's
fixed-vs-per-rung decomposition gap.

The clean rung_count=100 param-count sweep (n=2/3/4/6/8/12,
`gen_batch3_followups.py` group E) and the older rung_count=1000 sweep
(n=1/5/10, `gen_jsr_sbr_ret.py`) share zero overlapping param counts --
there's no way to solve for a rung-count-independent one-time term
(subroutine Parameters-block cost) separately from a per-call term without
at least one param count captured at both rung counts. n=5 and n=10 already
exist at rung_count=1000; this file adds the matching rung_count=100 points
so the 2x2 system (2 param counts x 2 rung counts) can be solved directly.
Not a new question -- see docs/OPEN_QUESTIONS.md OQ-JSRPARAMCOST.

Run: python -m sample_gen.gen_jsr_decompose
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

LOGIC_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

RUNG_COUNT = 100


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = LOGIC_OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "jsr_sbr_ret", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _sub_routine_xml(routine_name: str, in_locals: list[str]) -> str:
    sbr_rung = rung_xml(0, f"SBR({','.join(in_locals)})NOP();" if in_locals else "SBR()NOP();")
    ret_rung = rung_xml(1, "RET();")
    return (
        f'<Routine Name="{routine_name}" Type="RLL">'
        f"<RLLContent>{sbr_rung}\n{ret_rung}</RLLContent>"
        "</Routine>"
    )


def group_jsr_rungcount_overlap() -> int:
    n = 0
    for param_count in [5, 10]:
        caller_args = [f"JIn{i}" for i in range(param_count)]
        callee_locals = [f"LIn{i}" for i in range(param_count)]
        caller_tags = "\n".join(tag_xml(t, "DINT") for t in caller_args + callee_locals)
        routine_name = f"JsrDecomposeN{param_count}"
        sub_xml = _sub_routine_xml(routine_name, callee_locals)

        call_args = ",".join([str(param_count)] + caller_args)
        fn = lambda i, call_args=call_args, routine_name=routine_name: f"JSR({routine_name},{call_args});"
        rungs = rungs_xml(RUNG_COUNT, fn)
        l5x = build_l5x(target_name=f"JsrDecomposeN{param_count}Rung", tags_xml=caller_tags,
                         extra_rungs_xml=rungs, extra_routines_xml=sub_xml)
        _write(
            f"jsr_paramcount_n{param_count:02d}_r{RUNG_COUNT:05d}_decompose",
            l5x,
            f"{RUNG_COUNT} rungs of JSR to a subroutine with {param_count} pure-input params -- "
            f"OQ-JSRPARAMCOST rung-count-overlap point (matches existing n{param_count:02d}_r01000)",
        )
        n += 1
    return n


def group_jsr_third_disentangle_point() -> int:
    """2026-08-26: n=5/n=10 now have BOTH rung counts (100 and 1000) --
    real data resolves the fixed-vs-per-rung split cleanly: A(5)=204,
    B(5)=104/rung; A(10)=304, B(10)=204/rung. Both fit A(n)=104+20n,
    B(n)=4+20n exactly -- but from only 2 solved (n) points, a linear
    fit through 2 points is trivially exact and proves nothing about
    whether it generalizes. n=8 already has real r=100 data
    (jsr_paramcount_n08_r00100, existing group E) -- this adds the
    matching r=1000 point, the cheapest way to get a 3rd real (A,B)
    solve and confirm (or refute) the A(n)/B(n) linear-in-n pattern
    before trusting it."""
    param_count = 8
    rung_count = 1000
    caller_args = [f"JIn{i}" for i in range(param_count)]
    callee_locals = [f"LIn{i}" for i in range(param_count)]
    caller_tags = "\n".join(tag_xml(t, "DINT") for t in caller_args + callee_locals)
    routine_name = f"JsrDecomposeN{param_count}R{rung_count}"
    sub_xml = _sub_routine_xml(routine_name, callee_locals)

    call_args = ",".join([str(param_count)] + caller_args)
    fn = lambda i: f"JSR({routine_name},{call_args});"
    rungs = rungs_xml(rung_count, fn)
    l5x = build_l5x(target_name=f"JsrDecomposeN{param_count}R{rung_count}", tags_xml=caller_tags,
                     extra_rungs_xml=rungs, extra_routines_xml=sub_xml)
    _write(
        f"jsr_paramcount_n{param_count:02d}_r{rung_count:05d}_decompose",
        l5x,
        f"{rung_count} rungs of JSR to a subroutine with {param_count} pure-input params -- "
        f"OQ-JSRPARAMCOST 3rd disentangle point (matches existing n{param_count:02d}_r00100), "
        f"confirms whether A(n)=104+20n / B(n)=4+20n generalizes past the 2 points that produced it",
    )
    return 1


if __name__ == "__main__":
    total = group_jsr_rungcount_overlap()
    total += group_jsr_third_disentangle_point()
    print(f"\nTotal files: {total}")
