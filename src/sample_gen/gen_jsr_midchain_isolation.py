"""OQ-JSRPARAMCOST: does a mid-chain routine's own OUTBOUND JSR call(s)
cost anything, or does report.py's `is_jsr_target` branch silently drop
them? (2026-08-31, James: "the program points to a main routine that
normally calls subroutines but these subroutines can also be used to call
other subroutines.")

Real, code-level finding this isolates: report.py's per-routine loop
checks `if routine.is_jsr_target: ... continue` FIRST -- a routine that is
BOTH a JSR target (something else calls it) AND itself a JSR caller (it
calls something else) takes the is_jsr_target branch and `continue`s
before its own outbound JSR call(s) are ever priced. Real AccuTally data
(confidential, not committed) has 29 such mid-chain routines -- one
(`_C_00_GetProduct_D`) makes 10 real JSR calls of its own, all currently
contributing $0 beyond its own one-time A(n) declaration cost.

3-level real chain: MainRoutine -[JSR]-> RoutineA -[JSR]-> RoutineB -[RET].
RoutineA is exactly the mid-chain shape (target of Main, caller of B).
Holding every count (params=2, calls=1 each) at the smallest confirmed
values from the existing JSR corpus isolates the chain-position question
alone -- if RoutineA's real Capacity contribution differs at all from an
equivalent-shaped LEAF target (no outbound call), the B(n) mid-chain call
cost is real and currently unmodeled.

2 files: one 3-level real chain, one otherwise-identical LEAF-target
control (RoutineA calls nothing) to diff against directly.

Run: python -m sample_gen.gen_jsr_midchain_isolation
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

N_PARAMS = 2


def _sub_routine_xml(routine_name: str, in_locals: list[str], call_rung: str | None) -> str:
    sbr_rung = rung_xml(0, f"SBR({','.join(in_locals)})NOP();")
    rungs = [sbr_rung]
    if call_rung:
        rungs.append(rung_xml(1, call_rung))
        ret_idx = 2
    else:
        ret_idx = 1
    rungs.append(rung_xml(ret_idx, "RET();"))
    return (
        f'<Routine Name="{routine_name}" Type="RLL">'
        f"<RLLContent>{chr(10).join(rungs)}</RLLContent>"
        "</Routine>"
    )


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "jsr_sbr_ret", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _tags(prefix: str) -> tuple[str, list[str]]:
    names = [f"{prefix}{i}" for i in range(N_PARAMS)]
    return "\n".join(tag_xml(t, "DINT") for t in names), names


def group_midchain() -> None:
    a_locals = [f"AIn{i}" for i in range(N_PARAMS)]
    b_locals = [f"BIn{i}" for i in range(N_PARAMS)]
    a_call_args = ",".join([str(N_PARAMS)] + a_locals)  # A forwards its own params to B
    b_xml = _sub_routine_xml("JsrMidchainRoutineB", b_locals, None)
    a_xml = _sub_routine_xml("JsrMidchainRoutineA", a_locals, f"JSR(JsrMidchainRoutineB,{a_call_args});")

    main_tags, main_args = _tags("MIn")
    call_args = ",".join([str(N_PARAMS)] + main_args)
    main_call = rung_xml(0, f"JSR(JsrMidchainRoutineA,{call_args});")
    l5x = build_l5x(
        target_name="JsrMidchainReal", tags_xml=main_tags,
        extra_rungs_xml=main_call, extra_routines_xml=a_xml + "\n" + b_xml,
    )
    _write(
        "jsr_midchain_real_chain",
        l5x,
        "3-level real JSR chain: MainRoutine -> RoutineA (JSR target of Main, ALSO itself a JSR "
        "caller of RoutineB) -> RoutineB (leaf target). RoutineA is the mid-chain shape found in "
        "real AccuTally data (confidential, not committed) -- 29 real routines are both a JSR "
        "target and a JSR caller, and report.py's is_jsr_target branch currently drops a "
        "mid-chain routine's own outbound JSR call cost entirely. Predicted total here (18,972) "
        "minus jsr_midchain_leaf_control's predicted total (18,828) = 144, exactly RoutineB's own "
        "A(2)=104+20*2 declaration cost and NOTHING for RoutineA's own outbound call -- that's "
        "the current model's claim. If real Capacity's delta between the two files is anything "
        "OTHER than 144, that excess is the real, currently-unmodeled mid-chain call cost.",
    )


def group_leaf_control() -> None:
    a_locals = [f"AIn{i}" for i in range(N_PARAMS)]
    a_xml = _sub_routine_xml("JsrMidchainRoutineA", a_locals, None)  # RoutineA calls nothing

    main_tags, main_args = _tags("MIn")
    call_args = ",".join([str(N_PARAMS)] + main_args)
    main_call = rung_xml(0, f"JSR(JsrMidchainRoutineA,{call_args});")
    l5x = build_l5x(
        target_name="JsrMidchainLeafCtl", tags_xml=main_tags,
        extra_rungs_xml=main_call, extra_routines_xml=a_xml,
    )
    _write(
        "jsr_midchain_leaf_control",
        l5x,
        "Control for jsr_midchain_real_chain: byte-identical MainRoutine -> RoutineA (JSR "
        "target), but RoutineA is a plain LEAF target here (calls nothing further) instead of "
        "itself calling RoutineB. Isolates the mid-chain outbound-call cost by direct diff "
        "against jsr_midchain_real_chain.",
    )


def main() -> None:
    group_midchain()
    group_leaf_control()
    print("\nDone. 2 files.")


if __name__ == "__main__":
    main()
