"""The two JSR parameter cases not yet measured on their own.

A parameterised JSR copies each input argument into the target's local
parameter on entry and each return value back on RET -- an atomic value like
MOV, a structure or STRING like COP. `jsr_paramtype_{udt,string}_*` measured
the structured INPUT: 8 more per argument per call than an atomic one, 12 more
once on the target (memory_model.yaml jsr_param_cost). Two edges rest on the
copy mechanism rather than on a file of their own:

  ret_{dint,udt}_n{1,3}      n RETURN values of DINT vs UDT type. The copy-back
                             mechanism says a UDT return costs what a UDT input
                             costs; 53 real return arguments are structured.
  in_{bare,member}_n{1,3}    n UDT inputs passed as a bare UDT tag vs as a
                             member of a wrapper UDT whose type is that UDT
                             (`W.S0`). The engine resolves only bare tags, so a
                             member argument is charged the atomic rate; 604 real
                             input arguments are member paths, indexed or literal.

100 calls per file, the shape of jsr_multiret_*: `JSR(T,1,JIn0,<returns>)` with
the target `SBR(LIn0)NOP();`, `XIC(Cond0)RET(...)`, `RET(...)`. Every file of an
arm declares the same tags and UDTs, so a pair differs only in call text. Each arm
differences its structured file against its atomic/bare partner at the same n,
and n=1 against n=3 gives the per-argument slope.

1756-L81E at firmware 35.

Run: python -m sample_gen.gen_jsr_param_edges
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, collect_nested_datatypes, rung_xml, rungs_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

CALLS = 100
N_VALUES = (1, 3)

_UDT = "JsrEdgeUdt2Dint"
_UDT_MEMBERS = [MemberSpec("M0", "DINT"), MemberSpec("M1", "DINT")]
_WRAP_MEMBERS = [MemberSpec(f"S{i}", _UDT, nested_members=tuple(_UDT_MEMBERS)) for i in range(3)]


def _target(name: str, in_locals: list[str], ret_locals: list[str]) -> str:
    ret = f"RET({','.join(ret_locals)});"
    body = "\n".join([
        rung_xml(0, f"SBR({','.join(in_locals)})NOP();"),
        rung_xml(1, f"XIC(Cond0){ret}"),
        rung_xml(2, ret),
    ])
    return f'<Routine Name="{name}" Type="RLL"><RLLContent>{body}</RLLContent></Routine>'


def _write(name: str, l5x: str, description: str) -> None:
    out = OUT_ROOT / f"{name}.L5X"
    predicted = write_sample(l5x, out)
    append_manifest_row(name, description, "jsr_sbr_ret", out, predicted)
    print(f"Wrote {out} (predicted {predicted} bytes)")


def arm_returns() -> int:
    for kind in ("dint", "udt"):
        for n in N_VALUES:
            target = f"JsrEdgeRet{kind.title()}N{n}"
            outs = [f"JOut{kind.title()}{i}" for i in range(n)]
            locs = [f"LOut{kind.title()}{i}" for i in range(n)]
            # The SAME inventory in all four files -- DINT and UDT return tags
            # for three returns each, and the UDT definition -- so a pair of
            # files differs only in the call and RET text.
            ret_tags = ([tag_xml(f"{p}Dint{i}", "DINT") for p in ("JOut", "LOut") for i in range(3)]
                        + [tag_xml(f"{p}Udt{i}", _UDT, udt_members=_UDT_MEMBERS)
                           for p in ("JOut", "LOut") for i in range(3)])
            datatypes = udt_xml(_UDT, _UDT_MEMBERS)
            tags = "\n".join([tag_xml("Cond0", "BOOL"), tag_xml("JIn0", "DINT"),
                              tag_xml("LIn0", "DINT")] + ret_tags)
            call = f"JSR({target},1,JIn0,{','.join(outs)});"
            l5x = build_l5x(target_name=target, tags_xml=tags,
                            extra_rungs_xml=rungs_xml(CALLS, lambda i: call),
                            extra_routines_xml=_target(target, ["LIn0"], locs),
                            extra_datatypes_xml=datatypes)
            _write(f"jsredge_ret_{kind}_n{n}_r{CALLS:05d}", l5x,
                   f"{CALLS} JSR calls passing one DINT input and {n} {kind.upper()} RETURN "
                   f"value(s), copied back on RET. Differenced against jsredge_ret_"
                   f"{'dint' if kind == 'udt' else 'udt'}_n{n}: does a structured return cost "
                   f"what a structured input costs (+8/call, +12 on the target)? See "
                   f"memory_model.yaml jsr_param_cost.")
    return 2 * len(N_VALUES)


def arm_member_inputs() -> int:
    datatypes = collect_nested_datatypes("JsrEdgeWrap", _WRAP_MEMBERS)
    for kind in ("bare", "member"):
        for n in N_VALUES:
            target = f"JsrEdgeIn{kind.title()}N{n}"
            args = [f"U{i}" for i in range(n)] if kind == "bare" else [f"W.S{i}" for i in range(n)]
            locs = [f"LIn{i}" for i in range(n)]
            tags = "\n".join(
                [tag_xml("Cond0", "BOOL"), tag_xml("W", "JsrEdgeWrap", udt_members=_WRAP_MEMBERS)]
                + [tag_xml(f"U{i}", _UDT, udt_members=_UDT_MEMBERS) for i in range(3)]
                + [tag_xml(f"LIn{i}", _UDT, udt_members=_UDT_MEMBERS) for i in range(3)])
            call = f"JSR({target},{n},{','.join(args)});"
            l5x = build_l5x(target_name=target, tags_xml=tags,
                            extra_rungs_xml=rungs_xml(CALLS, lambda i: call),
                            extra_routines_xml=_target(target, locs, []),
                            extra_datatypes_xml=datatypes)
            _write(f"jsredge_in_{kind}_n{n}_r{CALLS:05d}", l5x,
                   f"{CALLS} JSR calls passing {n} UDT input(s) as "
                   f"{'bare UDT tags' if kind == 'bare' else 'members of a wrapper UDT (W.S0)'}; "
                   f"identical tag inventory in both. Differenced against jsredge_in_"
                   f"{'member' if kind == 'bare' else 'bare'}_n{n}: does a member argument whose "
                   f"type is a UDT cost the structured rate? See memory_model.yaml jsr_param_cost.")
    return 2 * len(N_VALUES)


def main() -> None:
    n = arm_returns() + arm_member_inputs()
    print(f"\nDone. {n} files.")


if __name__ == "__main__":
    main()
