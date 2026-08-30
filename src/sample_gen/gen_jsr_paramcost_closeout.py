"""OQ-JSRPARAMCOST closeout batch (2026-08-30). Recomputing live against the
current engine (per the "review open questions... full depth" standing rule,
CLAUDE.md) surfaced two real, previously-invisible threads -- the manifest's
stored predicted_bytes/delta columns predate the b_cost/output_param wiring
and were badly stale, masking both:

1. **n=1 anomaly**: `jsr_paramcount_n01_r01000` (the only real n=1 point) is
   over-predicted by +4004 across 1000 calls, ~4.0 bytes/call -- suspiciously
   exactly `jsr_param_cost.b_base` (4). Real evidence the flat +4 base term
   in `b_cost(n)=b_base+b_per_param*n` may not apply at n=1. Never actually
   tested before (the model's "confirmed exact at n=5,8,10" claim never
   covered n=1). This residual is clearly PER-CALL (scales with rung count),
   unlike (2) below -- needs a same-n cross-check at a different rung count
   to confirm it's real and not a one-off capture artifact.

2. **Small flat n-dependent residual, NOT explained by the model**: n=2,3,4,
   6,8,12 each show a tiny (+4 to +8 byte) residual that is IDENTICAL at
   both rung counts already captured for a given n (e.g. n=8 is +8 at both
   r=100 and r=1000) -- i.e. rung-count-INDEPENDENT, a one-time-per-file
   effect, not a per-call rate error. n=5 and n=10 (the two points the
   b_cost linear fit was solved from) are the ONLY exact points -- the
   "confirmed exact at n=5,8,10" claim in constants.py's JsrParamCostModel
   docstring is stale/wrong (n=8 is off by +8, live-verified). Sub-0.02% of
   file total, well within this project's own "logic sizing is a guess at
   best, not held to the exact-tier tolerance bar" convention (OQ-TOLERANCE)
   -- but James asked to close this at 100%, so mapping the actual shape of
   this small offset as a function of n (not just shrugging at it as noise)
   is the goal. Since it's rung-count-independent, a dense n-sweep at a
   CHEAP rung count (r=10) is far more efficient than more rung-count
   variation -- rung count doesn't move this residual at all, already
   demonstrated by the existing n=5/8/10 dual-rung-count points.

Five files, each isolating exactly one open thread -- not padded to any
floor (James, 2026-08-25: "The 60-file floor is not a quota to pad toward"):

  A. jsr_paramcount_n01_r00100 -- n=1 cross-check at a different rung count.
     If the anomaly is truly ~4/call, delta here should be ~400 (not ~8,
     which is what a flat one-time effect like group B's would predict).

  B. jsr_paramcount_n07/n09/n15_r00010 -- dense n-sweep at cheap r=10,
     filling the gaps around the existing n=6/8/10/12 points and directly
     testing whether "residual is exactly 0 at n=5 and n=10" is a genuine
     multiples-of-5 periodicity (n=15 should also land at 0 if so) or
     coincidence from only 2 zero-points on file.

  C. jsr_multiret_n02_r01000 -- 2 conditional-RET points instead of the
     existing jsr_multiret_n04's 4, same rung count, same 1-in/2-out shape.
     Isolates whether the existing +332 residual on jsr_multiret_n04 scales
     with RET-point-count (confirming RET costs like any other repeated
     instruction, per the original James ask) or is itself a flat
     output-param effect unrelated to RET count.

Run: python -m sample_gen.gen_jsr_paramcost_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
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


def _paramcount_file(n: int, rung_count: int) -> None:
    caller_args = [f"JIn{i}" for i in range(n)]
    callee_locals = [f"LIn{i}" for i in range(n)]
    caller_tags = "\n".join(tag_xml(t, "DINT") for t in caller_args + callee_locals)
    routine_name = f"JsrCloseoutN{n}R{rung_count}"
    sub_xml = _sub_routine_xml(routine_name, callee_locals)

    call_args = ",".join([str(n)] + caller_args)
    fn = lambda i, call_args=call_args, routine_name=routine_name: f"JSR({routine_name},{call_args});"
    rungs = rungs_xml(rung_count, fn)
    l5x = build_l5x(target_name=f"JsrCloseoutN{n}R{rung_count}", tags_xml=caller_tags,
                     extra_rungs_xml=rungs, extra_routines_xml=sub_xml)
    _write(
        f"jsr_paramcount_n{n:02d}_r{rung_count:05d}",
        l5x,
        f"{rung_count} rungs of JSR to a subroutine with {n} pure-input params -- "
        f"OQ-JSRPARAMCOST closeout point",
    )


def group_n01_crosscheck() -> int:
    # n=1 at r=100 instead of the existing r=1000 -- if the ~4/call
    # over-prediction seen at r=1000 (+4004 total) is real and per-call,
    # this file should land at roughly +400, not +8 (which is what a flat
    # one-time effect like group_dense_n_sweep's would predict instead).
    _paramcount_file(1, 100)
    return 1


def group_dense_n_sweep() -> int:
    n = 0
    for param_count in [7, 9, 15]:
        _paramcount_file(param_count, 10)
        n += 1
    return n


def group_multiret_retcount_isolation() -> int:
    # Same shape as gen_jsr_sbr_ret.py's group_multiple_ret (1 input param,
    # 2 output/return params) but 2 conditional RET points instead of 4 --
    # same rung count (1000) as the existing jsr_multiret_n04 real capture,
    # so the two files differ ONLY in RET-point-count.
    cond_tags = [f"Cond{i}" for i in range(1)]
    out_locals = ["LOutA", "LOutB"]
    caller_out_args = ["JOutA", "JOutB"]
    in_arg = "JIn0"
    in_local = "LIn0"
    rung_count = 1000

    tags_xml_body = "\n".join(
        [tag_xml(in_arg, "DINT")] + [tag_xml(a, "DINT") for a in caller_out_args]
        + [tag_xml(c, "BOOL") for c in cond_tags]
        + [tag_xml(in_local, "DINT")] + [tag_xml(t, "DINT") for t in out_locals]
    )

    sub_rungs = [rung_xml(0, f"SBR({in_local})NOP();")]
    for i, cond in enumerate(cond_tags):
        sub_rungs.append(rung_xml(i + 1, f"XIC({cond})RET({','.join(out_locals)});"))
    sub_rungs.append(rung_xml(len(cond_tags) + 1, f"RET({','.join(out_locals)});"))
    sub_xml = (
        '<Routine Name="JsrMultiRetN2Target" Type="RLL">'
        f'<RLLContent>{chr(10).join(sub_rungs)}</RLLContent>'
        "</Routine>"
    )

    call_args = ",".join(["1", in_arg] + caller_out_args)
    fn = lambda i: f"JSR(JsrMultiRetN2Target,{call_args});"
    rungs = rungs_xml(rung_count, fn)
    l5x = build_l5x(target_name="JsrMultiRetN2", tags_xml=tags_xml_body, extra_rungs_xml=rungs,
                     extra_routines_xml=sub_xml)
    _write(
        f"jsr_multiret_n02_r{rung_count:05d}",
        l5x,
        f"{rung_count} rungs of JSR to a subroutine with 1 input param and 2 RET points "
        f"(1 conditional XIC(cond)RET(...); + 1 final unconditional RET(...);) -- "
        f"OQ-JSRPARAMCOST RET-point-count isolation, matches jsr_multiret_n04 exactly except "
        f"RET-point-count (4->2), tests whether the existing +332 residual scales with RET count",
    )
    return 1


def main() -> None:
    total = 0
    for fn in [group_n01_crosscheck, group_dense_n_sweep, group_multiret_retcount_isolation]:
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
