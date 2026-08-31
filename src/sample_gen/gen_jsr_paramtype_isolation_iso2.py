"""OQ-JSRPARAMCOST STRING/UDT per-param surcharge isolation (2026-08-31,
James: "seems like you have lots of work to do with your errors on JSR
... if i get a test result that doesnt match my prediction i usually
check my existing work and devise new tests to fix it").

gen_jsr_paramtype_isolation.py's n=5 fixed-count probes found a real gap:
STRING and UDT-typed JSR params are both off by ~9.8% (~4,050-4,100 bytes
on a ~41,000-byte total) while atomic-typed (DINT/REAL) params in the same
batch land within 0.04%. That result can't isolate a clean per-param
surcharge on its own -- one data point per type only proves a gap exists,
not its shape (flat one-time cost vs. scales with param count).

This file varies N (param count) at N=1/3/5 for STRING and UDT separately,
holding rung_count=100 and every other structural element fixed identical
to the existing n=5 point -- same routine/tag naming pattern, same call
shape -- so a real per-param STRING/UDT surcharge shows up as the slope
between the 3 points, cleanly separable from any flat one-time term.

6 files total (3 N values x 2 types). Suffixed `_iso2` per James's request
to keep this follow-up round visually distinct from the original n=5
paramtype-isolation batch.

Run: python -m sample_gen.gen_jsr_paramtype_isolation_iso2
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, rung_xml, rungs_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

RUNG_COUNT = 100
N_VALUES = (1, 3, 5)


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


def _run(label: str, n: int, tags_xml: str, extra_datatypes_xml: str = "") -> None:
    caller_args = [f"JIn{i}" for i in range(n)]
    callee_locals = [f"LIn{i}" for i in range(n)]
    routine_name = f"JsrParamTypeIso2{label}N{n:02d}Target"
    sub_xml = _sub_routine_xml(routine_name, callee_locals)

    call_args = ",".join([str(n)] + caller_args)
    fn = lambda i: f"JSR({routine_name},{call_args});"
    rungs = rungs_xml(RUNG_COUNT, fn)
    l5x = build_l5x(target_name=f"JsrParamTypeIso2{label}N{n:02d}", tags_xml=tags_xml,
                     extra_rungs_xml=rungs, extra_routines_xml=sub_xml,
                     extra_datatypes_xml=extra_datatypes_xml)
    _write(
        f"jsr_paramtype_{label.lower()}_n{n:02d}_r{RUNG_COUNT:05d}_iso2",
        l5x,
        f"{RUNG_COUNT} rungs of JSR to a subroutine with {n} {label} params (input-only) -- "
        f"OQ-JSRPARAMCOST STRING/UDT per-param surcharge isolation (follow-up to the n=5-only "
        f"paramtype batch that found ~9.8% real gaps): param count is now the variable at fixed "
        f"type, so 3 points at n=1/3/5 isolate the real per-param slope from any flat term.",
    )


def group_udt() -> None:
    udt_name = "JsrParamTypeIso2Udt2Dint"
    members = [MemberSpec("M0", "DINT"), MemberSpec("M1", "DINT")]
    datatype_xml = udt_xml(udt_name, members)
    for n in N_VALUES:
        caller_args = [f"JIn{i}" for i in range(n)]
        callee_locals = [f"LIn{i}" for i in range(n)]
        tags = "\n".join(
            tag_xml(t, udt_name, udt_members=members) for t in caller_args + callee_locals
        )
        _run("Udt", n, tags, extra_datatypes_xml=datatype_xml)


def group_string() -> None:
    for n in N_VALUES:
        caller_args = [f"JIn{i}" for i in range(n)]
        callee_locals = [f"LIn{i}" for i in range(n)]
        tags = "\n".join(tag_xml(t, "STRING", string_max_len=82) for t in caller_args + callee_locals)
        _run("String", n, tags)


def main() -> None:
    group_udt()
    group_string()
    print("\nDone. 6 files.")


if __name__ == "__main__":
    main()
