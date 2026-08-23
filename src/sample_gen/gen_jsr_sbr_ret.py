"""JSR/SBR/RET parameter-passing sweep (James, 2026-08-23): "the jsr/sbr/ret
pair of subroutine calls. We normally use JSR with no parameters other
than the subroutine it's calling. We can have parameters of tags for the
jsr that get passed to the sbr (always one instance as the first
instruction, never duplicated) and these will update 'local'/'temp' tags
that are used within the subroutine. As the last instruction (or
conditionally elsewhere as well with no limit on Qty used) it will pass
some local/temp tags back out to the jsr that called it. The jsr can have
many parameters but always has input parameters first and return
parameters at the end. Review sample project code and look for SBR/Ret
and how they relate to the calling JSR. This will need to be tested and
validated with deductions between 1/5/10 parameters on the jsr as
seperate files and then another test with multiple ret conditionally
placed"

Real syntax confirmed against the corpus (not guessed), from
samples/local/SJ_Gormley_20251112_r02.L5X, routines `_525_InputMapping_TS`
/`_525_OutputMapping_TS` (both RLL -- SBR/RET in ST routines exist too but
this project only ever needed the RLL shape) and their real call sites in
`_203_IncisorTop_EM203`:

  JSR(_525_InputMapping_TS,1,EM203_IncisorTop:I,IncisorTop_AxisInput)
  ...
  Routine "_525_InputMapping_TS":
    Rung 0: SBR(PF525_Generic_Dummy:I)NOP();      <- 1 param, matches JSR's "1"
    ... (mapping logic) ...
    last rung: RET(VFD_AOIAxisInput);              <- 1 param, the return value

  JSR(_525_OutputMapping_TS,1,IncisorTop_AxisOutput,EM203_IncisorTop:O)
  ...
  Routine "_525_OutputMapping_TS":
    Rung 0: SBR(VFD_AOIAxisOutput)NOP();
    ... (mapping logic) ...
    last rung: RET(PF525_Generic_Dummy:O);

Both examples decode the same way: `JSR(name, N_in, in_1..in_N,
out_1..out_M);` -- the second positional arg is the INPUT param count only
(matches James: "always has input parameters first and return parameters
at the end"), the input args fill SBR's own param list 1:1, and the
trailing args (beyond N_in) are where the routine's RET value(s) land back
in the CALLER's own tags. SBR's own param names and the JSR's input-arg
names are unrelated tags (positional mapping, not name matching) -- same
for RET vs the JSR's trailing output args. SBR is always the routine's
first rung, exactly once (James: "never duplicated") -- confirmed both
real examples put it at Rung 0 with nothing before it.

  A. group_param_count -- 1/5/10 pure INPUT params (no return), JSR called
     across 1000 identical rungs each, to see how JSR/SBR's combined
     marginal cost scales with parameter count (the original 244-file
     sweep's confirmed 72-blocks/rung JSR weight used JSR(SubTest,0) --
     zero params -- so this is new territory).
  B. group_mixed_io -- a realistic mixed shape (5 in + 2 out, matching the
     real corpus's in+out pattern) at the same 1000-rung scale, directly
     comparable against group A's pure-input n=5 point.
  C. group_multiple_ret -- James: "conditionally elsewhere as well with no
     limit on Qty used." A target subroutine with 3 conditional
     XIC(cond)RET(...); rungs plus one final unconditional RET(...);  --
     tests whether RET count itself costs like any other repeated
     instruction, and confirms the "no limit on qty" real shape builds
     clean.

Run: python -m sample_gen.gen_jsr_sbr_ret
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
RUNG_COUNT = 1000


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "jsr_sbr_ret", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _sub_routine_xml(routine_name: str, in_locals: list[str], out_locals: list[str]) -> str:
    sbr_rung = rung_xml(0, f"SBR({','.join(in_locals)})NOP();" if in_locals else "SBR()NOP();")
    ret_rung = rung_xml(1, f"RET({','.join(out_locals)});" if out_locals else "RET();")
    return (
        f'<Routine Name="{routine_name}" Type="RLL">'
        f"<RLLContent>{sbr_rung}\n{ret_rung}</RLLContent>"
        "</Routine>"
    )


def group_param_count() -> None:
    for n in [1, 5, 10]:
        caller_args = [f"JIn{i}" for i in range(n)]
        callee_locals = [f"LIn{i}" for i in range(n)]
        caller_tags = "\n".join(tag_xml(t, "DINT") for t in caller_args)
        sub_xml = _sub_routine_xml("JsrParamTarget", callee_locals, [])

        call_args = ",".join([f"{n}"] + caller_args)
        fn = lambda i, call_args=call_args: f"JSR(JsrParamTarget,{call_args});"
        rungs = rungs_xml(RUNG_COUNT, fn)
        l5x = build_l5x(target_name="JsrParamCount", tags_xml=caller_tags, extra_rungs_xml=rungs,
                         extra_routines_xml=sub_xml)
        out_name = f"jsr_paramcount_n{n:02d}_r{RUNG_COUNT:05d}"
        _write(l5x, out_name,
               f"{RUNG_COUNT} rungs of JSR to a subroutine with {n} pure-input params "
               f"(SBR({n} params)NOP(); RET();) -- JSR/SBR param-count scaling")


def group_mixed_io() -> None:
    n_in, n_out = 5, 2
    in_args = [f"JIn{i}" for i in range(n_in)]
    out_args = [f"JOut{i}" for i in range(n_out)]
    in_locals = [f"LIn{i}" for i in range(n_in)]
    out_locals = [f"LOut{i}" for i in range(n_out)]

    caller_tags = "\n".join(tag_xml(t, "DINT") for t in in_args + out_args)
    sub_xml = _sub_routine_xml("JsrMixedTarget", in_locals, out_locals)

    call_args = ",".join([f"{n_in}"] + in_args + out_args)
    fn = lambda i: f"JSR(JsrMixedTarget,{call_args});"
    rungs = rungs_xml(RUNG_COUNT, fn)
    l5x = build_l5x(target_name="JsrMixedIO", tags_xml=caller_tags, extra_rungs_xml=rungs,
                     extra_routines_xml=sub_xml)
    out_name = f"jsr_mixedio_{n_in}in_{n_out}out_r{RUNG_COUNT:05d}"
    _write(l5x, out_name,
           f"{RUNG_COUNT} rungs of JSR to a subroutine with {n_in} input + {n_out} return params "
           f"-- realistic mixed shape matching real corpus (SJ_Gormley _525_InputMapping_TS/_525_OutputMapping_TS)")


def group_multiple_ret() -> None:
    # James: RET can appear conditionally, anywhere, any quantity -- not
    # just once at the end. 3 conditional early-exit RETs + 1 final
    # unconditional RET, each returning a different local tag combination
    # (mirrors a realistic early-exit-on-fault subroutine pattern).
    cond_tags = [f"Cond{i}" for i in range(3)]
    out_locals = ["LOutA", "LOutB"]
    caller_out_args = ["JOutA", "JOutB"]
    in_arg = "JIn0"
    in_local = "LIn0"

    tags_xml_body = "\n".join(
        [tag_xml(in_arg, "DINT")] + [tag_xml(a, "DINT") for a in caller_out_args]
        + [tag_xml(c, "BOOL") for c in cond_tags]
    )

    sub_rungs = [rung_xml(0, f"SBR({in_local})NOP();")]
    for i, cond in enumerate(cond_tags):
        sub_rungs.append(rung_xml(i + 1, f"XIC({cond})RET({','.join(out_locals)});"))
    sub_rungs.append(rung_xml(len(cond_tags) + 1, f"RET({','.join(out_locals)});"))
    sub_xml = (
        '<Routine Name="JsrMultiRetTarget" Type="RLL">'
        f'<RLLContent>{chr(10).join(sub_rungs)}</RLLContent>'
        "</Routine>"
    )

    call_args = ",".join(["1", in_arg] + caller_out_args)
    fn = lambda i: f"JSR(JsrMultiRetTarget,{call_args});"
    rungs = rungs_xml(RUNG_COUNT, fn)
    l5x = build_l5x(target_name="JsrMultiRet", tags_xml=tags_xml_body, extra_rungs_xml=rungs,
                     extra_routines_xml=sub_xml)
    out_name = f"jsr_multiret_n04_r{RUNG_COUNT:05d}"
    _write(l5x, out_name,
           f"{RUNG_COUNT} rungs of JSR to a subroutine with 1 input param and 4 RET points "
           f"(3 conditional XIC(cond)RET(...); + 1 final unconditional RET(...);) -- "
           f"tests whether repeated/conditional RET costs like a normal repeated instruction")


def main() -> None:
    group_param_count()
    group_mixed_io()
    group_multiple_ret()
    print("\nDone. 5 files.")


if __name__ == "__main__":
    main()
