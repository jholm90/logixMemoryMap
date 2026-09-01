"""50 MORE large, realistic-scope composite test programs -- v2, 2026-08-31.

Direct follow-up to gen_composite_realistic.py's 50-file batch. That batch's
own ~3% real residual was checked directly against the two fixes just wired
this session (JSR-target-content weighing, AOI-internal-logic weighing) and
found to be UNMOVED by either (see OPEN_QUESTIONS.md OQ-COMPOSITESCALE,
2026-08-31 correction) -- root cause: v1's AOIs all use the old hardcoded
empty `<Routine Name="Logic" Type="RLL"/>` shape (zero internal content) and
v1 never declares a JSR-target routine with real content, so neither newly-
wired formula is exercised at composite scale at all.

This batch fixes exactly that gap while reusing every other real, already-
validated ingredient from v1 (UDTs, AOI declaration shapes, arrays, real I/O
modules, orphaned-AOI coverage) unchanged -- imported directly from
gen_composite_realistic.py rather than duplicated, so the real bug fixes
already applied there (AOI Required=true, XIC/OTE bit-subscript, backplane
slot/IP collision remapping) automatically carry over:

  - Every REFERENCED AOI now gets real internal Logic-routine content (real
    MOV/XIC/OTE/ADD/EQU mix over its own Input/Output/Local params, not the
    empty stub) -- rung count scales with the AOI's own index so the batch
    covers a real range of internal-logic sizes, not one fixed size.
  - Each file also declares ONE JSR-target subroutine with real content
    (same mix, scaled by file index), called once from the main rung mix,
    0 params (the real, dominant real-corpus shape per OQ-JSRPARAMCOST).

Goal: does the combination of both newly-wired formulas, exercised together
with everything else at real composite scale, actually close the ~3%
residual v1 left unexplained? This is the direct test of that question, not
a guess -- see CLAUDE.md's north-star goal (<1% on any real file).

Run: python -m sample_gen.gen_composite_realistic_v2
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, rungs_xml, tag_xml, timer_tag_xml, counter_tag_xml
from sample_gen.gen_composite_realistic import (
    Profile,
    _ATOMIC_TYPES,
    _modules_xml_unique_ips,
    _profile_for_index,
    _udt_specs,
)
from sample_gen.manifest import append_manifest_row, write_sample, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "composite"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

# James, 2026-08-31, real, caught on his own re-conversion (of the FIRST
# v2 batch, before this fix): "SINT/INT/DINT cannot be used for bit level
# instructions like XIO,XIC,OTE,OTU,OTL,ONS only bools and .Bits of
# SINT/INT/DINT" and "conditional instructions like EQU with no operand
# at the end of the rung or a NOP() instruction." Both real, both fixed
# here -- unlike gen_jsr_target_content_scale.py/gen_aoi_internal_logic_
# isolation.py (same bug class, fixed the same day), this generator's two
# call sites (AOI-internal-logic, JSR-target-content) pass DIFFERENT real
# operand types for the condition/output slot (Out0 is BOOL in the AOI
# case, Arr1[...] is INT in the JSR case) -- a single hardcoded ".0"
# would be wrong for the BOOL case (bit-subscripting a BOOL is itself
# invalid). Fixed by having each CALLER pre-format its own cond/out
# operands correctly (bit-subscripted only when the underlying type
# actually needs it) rather than guessing in the shared template.
_MIX = ["MOV({a},{b})", "XIC({cond})OTE({out})", "ADD({a},{b},{a})", "EQU({a},{b})OTE({out})"]


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    try:
        bytes_ = write_sample(l5x, out_path)
        append_manifest_row(out_name, description, "composite", out_path, bytes_)
        print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    except RuntimeError as exc:
        write_sample_unmodeled(l5x, out_path)
        append_manifest_row(out_name, f"{description} (unmodeled module shape in this file's I/O mix)", "composite", out_path, 0)
        print(f"Wrote {out_path} (predicted N/A -- unmodeled module shape: {exc})")


def _content_rungs(instr_count: int, a: str, b: str, cond: str, out: str) -> str:
    """a/b: plain numeric operands (MOV/ADD/EQU) -- any atomic numeric type.
    cond/out: the caller's OWN pre-formatted bit-level operands for XIC/OTE
    (already ".N"-subscripted if the underlying tag is SINT/INT/DINT, left
    bare if it's already BOOL) -- see this module's _MIX comment for why
    that formatting can't be guessed here."""
    if instr_count <= 0:
        return ""
    pieces = []
    idx = 0
    total = 0
    while total < instr_count:
        piece = _MIX[idx % len(_MIX)].format(a=a, b=b, cond=cond, out=out)
        pieces.append(rung_xml(idx, piece + ";"))
        total += piece.count("(")
        idx += 1
    return "".join(pieces)


def _aoi_specs_with_logic(profile: Profile) -> list[tuple[str, str, list[MemberSpec]]]:
    """Same shape/param mix as v1's _aoi_specs, but every AOI also gets real
    internal Logic-routine content (OQ-AOIINTERNALLOGIC, wired 2026-08-31) --
    instruction count scales with the AOI's own index (5..45) so the batch
    covers a real range, not one fixed size."""
    total = profile.aoi_referenced_count + profile.aoi_orphaned_count
    out = []
    for a in range(total):
        name = f"Comp{profile.index:02d}V2Aoi{a}"
        input_params = [MemberSpec(f"In{k}", "DINT", required=True) for k in range(1 + a % 3)]
        output_params = [MemberSpec(f"Out{k}", "BOOL", required=True) for k in range(1 + a % 2)]
        local_tags = [MemberSpec(f"Wrk{k}", "DINT") for k in range(2 + a % 3)]
        instr_count = 5 + (a * 7 + profile.index * 3) % 40
        # In0 is DINT (needs a bit subscript for XIC); Out0 is BOOL (bare,
        # bit-subscripting a BOOL would itself be invalid).
        logic_rungs = _content_rungs(instr_count, "In0", "Wrk0", "In0.0", "Out0")
        def_xml, storage = aoi_xml(
            name, input_params=input_params, output_params=output_params,
            local_tags=local_tags, logic_rungs_xml=logic_rungs,
        )
        out.append((name, def_xml, storage))
    return out


def _jsr_target_xml(profile: Profile) -> tuple[str, str, str]:
    """Returns (routine_xml, target_name, call_instr) -- one 0-param JSR
    target subroutine per file, real content (no SBR/RET, the real
    corpus-dominant 0-param shape per OQ-JSRPARAMCOST), instruction count
    scaling with file index (20..220)."""
    target_name = f"Comp{profile.index:02d}V2JsrTarget"
    instr_count = 20 + (profile.index * 4) % 200
    # Arr1 is always INT (fixed j=1 position in _ATOMIC_TYPES's cycling,
    # every file) -- both bracket-indexed elements need a bit subscript.
    rungs = _content_rungs(instr_count, "Arr0[0]", "Arr0[1]", "Arr1[0].0", "Arr1[1].0")
    routine_xml = f'<Routine Name="{target_name}" Type="RLL"><RLLContent>{rungs}</RLLContent></Routine>'
    call_instr = f"JSR({target_name},0);"
    return routine_xml, target_name, call_instr


def _build(profile: Profile) -> tuple[str, str]:
    types_xml, udts = _udt_specs(profile)
    aois = _aoi_specs_with_logic(profile)
    jsr_routine_xml, jsr_target_name, jsr_call = _jsr_target_xml(profile)

    tags_parts: list[str] = []
    call_instrs: list[str] = [jsr_call]

    for j, size in enumerate(profile.array_sizes):
        t = _ATOMIC_TYPES[j % len(_ATOMIC_TYPES)]
        tags_parts.append(tag_xml(f"Arr{j}", t, dimensions=(size,)))

    array_udt_name, array_udt_members = udts[0]
    tags_parts.append(tag_xml(
        "UdtArr", array_udt_name, dimensions=(profile.udt_array_len,), udt_members=array_udt_members,
    ))

    tags_parts.append(timer_tag_xml("MainTmr", preset=1000 + profile.index * 10))
    tags_parts.append(counter_tag_xml("MainCtr", preset=100 + profile.index))

    referenced = aois[:profile.aoi_referenced_count]
    orphaned = aois[profile.aoi_referenced_count:]
    for name, _def_xml, storage in referenced:
        inst_name = f"{name}Inst"
        tags_parts.append(tag_xml(inst_name, name, udt_members=storage))
        n_in = sum(1 for m in storage if m.name.startswith("In"))
        n_out = sum(1 for m in storage if m.name.startswith("Out"))
        call_args = ",".join([inst_name] + ["0"] * n_in + ["OutBit"] * n_out)
        call_instrs.append(f"{name}({call_args});")
    tags_parts.append(tag_xml("OutBit", "BOOL"))

    aoi_def_xml = "\n".join(d for _n, d, _s in aois)

    def rung_instr(i: int) -> str:
        if i < len(call_instrs):
            return call_instrs[i]
        kind = i % 6
        if kind == 0:
            return f"XIC(Arr0[{i % profile.array_sizes[0]}].0)OTE(Arr1[{i % profile.array_sizes[1]}].0);"
        if kind == 1:
            return f"MOV(Arr0[{i % profile.array_sizes[0]}],Arr2[{i % profile.array_sizes[min(2, len(profile.array_sizes) - 1)]}]);"
        if kind == 2:
            return "ADD(Arr0[0],1,Arr0[0]);"
        if kind == 3:
            return "CPT(Arr0[1],Arr0[0]+2*Arr0[0]);"
        if kind == 4:
            return "TON(MainTmr,?,?);"
        return "CTU(MainCtr,?,?);"

    logic_rungs = rungs_xml(profile.rung_count, rung_instr)
    modules_xml = _modules_xml_unique_ips(profile.module_catalogs)

    l5x = build_l5x(
        target_name=f"Composite{profile.index:02d}V2",
        tags_xml="\n".join(tags_parts),
        extra_datatypes_xml=types_xml,
        extra_aoi_xml=aoi_def_xml,
        extra_rungs_xml=logic_rungs,
        extra_routines_xml=jsr_routine_xml,
        extra_modules_xml=modules_xml,
    )

    description = (
        f"Composite realistic-scope test v2 #{profile.index}/50 (2026-08-31 follow-up to "
        f"gen_composite_realistic.py -- direct test of whether the newly-wired JSR-target-content "
        f"and AOI-internal-logic formulas close v1's unexplained ~3% residual): same UDT/array/module/"
        f"AOI-declaration shape as v1 file #{profile.index}, but every referenced AOI now has real "
        f"internal Logic-routine content (5-45 real instructions) and the file declares one real "
        f"0-param JSR-target subroutine (20-220 real instructions, no SBR/RET -- the real corpus-"
        f"dominant 0-param shape) called once from the main rung mix. {profile.udt_count} UDTs "
        f"(1 nested), {profile.aoi_referenced_count} AOIs instantiated+called (WITH real logic), "
        f"{profile.aoi_orphaned_count} AOIs orphaned (also with real logic -- OQ-AOIORPHAN should "
        f"still show $0 real cost for these per the already-confirmed rule), {len(profile.array_sizes)} "
        f"atomic arrays + 1 UDT array, TIMER+COUNTER, {len(profile.module_catalogs)} real I/O modules "
        f"({', '.join(profile.module_catalogs)}), {profile.rung_count} rungs. 1756-L81E/fw35.05 default."
    )
    return l5x, description


def main() -> None:
    for i in range(1, 51):
        profile = _profile_for_index(i)
        l5x, description = _build(profile)
        _write(l5x, f"composite_realistic_v2_{i:02d}", description)
    print("\nDone. 50 files.")


if __name__ == "__main__":
    main()
