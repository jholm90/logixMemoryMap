"""OQ-JSRPARAMCOST param-TYPE isolation (2026-08-30). James: "Will this
accommodate data types for udt vs base data types like dints and reals?"

Real gap found answering that question: EVERY jsr_sbr_ret file ever built
(gen_jsr_sbr_ret.py, gen_jsr_decompose.py, gen_jsr_paramcost_closeout.py --
14 existing real captures plus the 5-file closeout batch just built) uses
DINT for every single JSR/SBR param, with zero exceptions. The sizing engine
itself (sizing/logic.py) charges `jsr_param_cost.b_cost(n_in)` purely off
the input-param COUNT -- it never looks at `tag_types` for a JSR call the
way it does for CPT/CMP operands (OQ-OPERANDTYPE), so right now the model
is silently assuming every param costs the same regardless of type. That
assumption was never tested, and the ORIGINAL real-corpus example that
motivated OQ-JSRPARAMCOST in the first place (SJ_Gormley_20251112_r02.L5X,
`_525_InputMapping_TS`/`_525_OutputMapping_TS`, see gen_jsr_sbr_ret.py's
docstring) passes `EM203_IncisorTop:I`, `PF525_Generic_Dummy:I`,
`IncisorTop_AxisInput`, `VFD_AOIAxisInput` -- all UDT/AOI-instance-typed
tags, NOT plain DINT. The entire dataset this formula is fitted from tests
a type the original motivating example doesn't even use.

Real Rockwell semantics this needs to isolate: an atomic scalar (DINT/REAL,
same 4-byte size, different register class) is very plausibly passed
differently at the compiled level than a structure (UDT), which is passed
by reference regardless of its own internal size -- if so, a UDT-typed
param's marginal JSR/SBR cost should look FLAT regardless of the struct's
member count (matching how AOI array-of-instances params are already
known to behave), not scale with struct size the way this project's other
per-member costs normally do.

3 files, param TYPE as the only variable -- n=5, rung_count=100 held fixed
identical to the existing exact DINT baseline (jsr_paramcount_n05_r00100_
decompose), so any delta isolates type alone:

  A. jsr_paramtype_real_n05_r00100 -- 5 REAL params (same 4-byte atomic
     size as the existing DINT baseline, different register class).

  B. jsr_paramtype_udt_n05_r00100 -- 5 params of a small 2-member
     (2xDINT, 8 bytes) UDT -- structure passed by reference, directly
     matching the real corpus's structure-typed JSR param shape.

  C. jsr_paramtype_string_n05_r00100 -- 5 STRING params (itself a
     predefined LEN+DATA structure, but built into the type system rather
     than a user UDT -- worth its own point in case it's handled
     differently than a plain user-defined UDT).

Run: python -m sample_gen.gen_jsr_paramtype_isolation
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, rung_xml, rungs_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

N = 5
RUNG_COUNT = 100


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "jsr_sbr_ret", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _sub_routine_xml(routine_name: str, in_locals: list[str]) -> str:
    sbr_rung = rung_xml(0, f"SBR({','.join(in_locals)})NOP();")
    ret_rung = rung_xml(1, "RET();")
    return (
        f'<Routine Name="{routine_name}" Type="RLL">'
        f"<RLLContent>{sbr_rung}\n{ret_rung}</RLLContent>"
        "</Routine>"
    )


def _run(label: str, tags_xml: str, extra_datatypes_xml: str = "") -> None:
    caller_args = [f"JIn{i}" for i in range(N)]
    callee_locals = [f"LIn{i}" for i in range(N)]
    routine_name = f"JsrParamType{label}Target"
    sub_xml = _sub_routine_xml(routine_name, callee_locals)

    call_args = ",".join([str(N)] + caller_args)
    fn = lambda i: f"JSR({routine_name},{call_args});"
    rungs = rungs_xml(RUNG_COUNT, fn)
    l5x = build_l5x(target_name=f"JsrParamType{label}", tags_xml=tags_xml,
                     extra_rungs_xml=rungs, extra_routines_xml=sub_xml,
                     extra_datatypes_xml=extra_datatypes_xml)
    _write(
        f"jsr_paramtype_{label.lower()}_n{N:02d}_r{RUNG_COUNT:05d}",
        l5x,
        f"{RUNG_COUNT} rungs of JSR to a subroutine with {N} {label} params (input-only) -- "
        f"OQ-JSRPARAMCOST param-type isolation, same n/rung_count as the exact DINT baseline "
        f"(jsr_paramcount_n05_r00100_decompose), type is the only variable",
    )


def group_real() -> None:
    caller_args = [f"JIn{i}" for i in range(N)]
    callee_locals = [f"LIn{i}" for i in range(N)]
    tags = "\n".join(tag_xml(t, "REAL") for t in caller_args + callee_locals)
    _run("Real", tags)


def group_udt() -> None:
    udt_name = "JsrParamTypeUdt2Dint"
    members = [MemberSpec("M0", "DINT"), MemberSpec("M1", "DINT")]
    datatype_xml = udt_xml(udt_name, members)

    caller_args = [f"JIn{i}" for i in range(N)]
    callee_locals = [f"LIn{i}" for i in range(N)]
    tags = "\n".join(
        tag_xml(t, udt_name, udt_members=members) for t in caller_args + callee_locals
    )
    _run("Udt", tags, extra_datatypes_xml=datatype_xml)


def group_string() -> None:
    caller_args = [f"JIn{i}" for i in range(N)]
    callee_locals = [f"LIn{i}" for i in range(N)]
    tags = "\n".join(tag_xml(t, "STRING", string_max_len=82) for t in caller_args + callee_locals)
    _run("String", tags)


def main() -> None:
    for fn in [group_real, group_udt, group_string]:
        fn()
    print("\nDone. 3 files.")


if __name__ == "__main__":
    main()
