"""50 large, realistic-scope composite test programs -- James, 2026-08-30:
"How many claude generated programs are you going to generate for testing
processor capacity and where your calculations are wrong? I expect at
least 50 large programs with io and logic to test your generation
knowledge and test aois and udts. You need to do this to validate your
processing capabilities that are more than 20% error based on the last
test." Direct response to the real ~20%+ gap found reviewing a
confidential customer project: every prior calibration file in this
project isolated ONE feature at a time ("onesy twosy"), never combined
enough real-world complexity at once to catch interaction effects or
structural gaps like OQ-AOIORPHAN (orphaned AOI definitions) that only
show up in a big real project.

Each of the 50 files is a genuinely different composition, not the same
shape with a number swapped -- every file combines, at real-world scale:
  - Several UDT definitions, at least one nested (a UDT containing
    another UDT), varying member count/type mix.
  - Several AOI definitions, MOST referenced (instantiated + called from
    a rung) but always at least one deliberately ORPHANED (declared,
    never instantiated) -- more real data points for OQ-AOIORPHAN across
    different AOI complexity/count combinations, not just the one
    minimal pair already built.
  - Large atomic-type arrays (DINT/INT/REAL/SINT/BOOL, varying element
    counts) plus at least one array-of-UDT.
  - TIMER/COUNTER tags (real predefined structures already confirmed
    elsewhero in this project).
  - 2-4 real I/O modules, cycled from gen_module_sweep.py's own
    _MODULE_CHAINS (86 real, already-extracted catalog blocks) -- never
    fabricated module content.
  - A meaningful rung count (150-900, scaling with file index) mixing
    XIC/OTE/MOV/ADD/CPT/TON/CTU/AOI-call instructions, not just NOP
    filler.

All 50 stay on 5069-L306ER/fw35.11 (this project's dominant, most-tested
baseline) -- the processor-family question (blocks vs bytes) is already
isolated separately by gen_blockbyte_l71.py/OQ-BLOCKBYTE, and mixing that
confound into this batch would make any interaction-effect findings here
ambiguous.

The composition scales across the 50 files via a deterministic index-based
schedule (documented in _profile_for_index below), not randomness -- every
file's exact feature mix is reproducible and auditable.

Run: python -m sample_gen.gen_composite_realistic
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sample_gen.builders import (
    MemberSpec, aoi_xml, collect_nested_datatypes, counter_tag_xml, rung_xml, rungs_xml,
    tag_xml, timer_tag_xml, udt_xml,
)
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.manifest import append_manifest_row, write_sample, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "composite"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

_MODULE_CATALOGS = sorted(_MODULE_CHAINS.keys())
_ATOMIC_TYPES = ["DINT", "INT", "REAL", "SINT", "BOOL"]


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    try:
        bytes_ = write_sample(l5x, out_path)
        append_manifest_row(out_name, description, "composite", out_path, bytes_)
        print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    except RuntimeError as exc:
        # Some real I/O module shapes (rack-aliased, embedded, etc.) are
        # already-known unmodeled cases elsewhere in this project (see
        # gen_fw_catalog_matrix.py's _write) -- same convention here
        # rather than hand-picking only "safe" catalogs, which would bias
        # this batch's module coverage toward whatever's easiest.
        write_sample_unmodeled(l5x, out_path)
        append_manifest_row(out_name, f"{description} (unmodeled module shape in this file's I/O mix)", "composite", out_path, 0)
        print(f"Wrote {out_path} (predicted N/A -- unmodeled module shape: {exc})")


@dataclass
class Profile:
    index: int
    udt_count: int
    aoi_referenced_count: int
    aoi_orphaned_count: int
    array_sizes: list[int]
    module_catalogs: list[str]
    rung_count: int
    udt_array_len: int


def _profile_for_index(i: int) -> Profile:
    """Deterministic feature schedule -- i in [1, 50]. Scale ramps
    smoothly with i; feature mix (which UDT nesting depth, which AOI
    param shapes, which modules) cycles through fixed pools so every file
    is a distinct real combination, not a re-roll of the same one."""
    scale = i / 50.0  # 0.02 .. 1.0
    udt_count = 2 + (i % 5)  # 2..6
    aoi_referenced = 2 + (i % 4)  # 2..5
    aoi_orphaned = 1 + (i % 3)  # 1..3, always >= 1 (OQ-AOIORPHAN coverage)
    n_arrays = 3 + (i % 4)  # 3..6 array tags
    base_size = int(200 + scale * 15000)
    array_sizes = [base_size + j * (137 + i * 3) for j in range(n_arrays)]
    n_modules = 2 + (i % 3)  # 2..4
    start = (i * 7) % len(_MODULE_CATALOGS)
    module_catalogs = [_MODULE_CATALOGS[(start + k) % len(_MODULE_CATALOGS)] for k in range(n_modules)]
    rung_count = int(150 + scale * 750)
    udt_array_len = 20 + (i % 10) * 15
    return Profile(i, udt_count, aoi_referenced, aoi_orphaned, array_sizes, module_catalogs, rung_count, udt_array_len)


def _udt_specs(profile: Profile) -> tuple[str, list[tuple[str, list[MemberSpec]]]]:
    """Returns (combined DataTypes XML, [(name, members)]) for this
    profile's UDT count -- UDT 0 is always nested (contains UDT 1) when
    udt_count >= 2, matching the real-corpus "mixed and garbled" nesting
    pattern already established in gen_axis_composite.py."""
    types_xml_parts = []
    udts: list[tuple[str, list[MemberSpec]]] = []
    for u in range(profile.udt_count):
        name = f"Comp{profile.index:02d}Udt{u}"
        members = [
            MemberSpec(f"D{k}", "DINT") for k in range(3 + (u % 3))
        ] + [
            MemberSpec(f"I{k}", "INT") for k in range(2)
        ] + [
            MemberSpec(f"B{k}", "BOOL") for k in range(4)
        ]
        if u == 0 and profile.udt_count >= 2:
            # Nested: first member is the previous UDT built (UDT 1)
            nested_name = f"Comp{profile.index:02d}Udt1"
            members = [MemberSpec("Nested", nested_name)] + members
        udts.append((name, members))
        types_xml_parts.append(udt_xml(name, members))
    return "\n".join(types_xml_parts), udts


def _aoi_specs(profile: Profile) -> list[tuple[str, str, list[MemberSpec]]]:
    """Returns [(aoi_name, def_xml, storage_members)] for every AOI this
    profile declares (referenced + orphaned combined) -- caller decides
    which get instantiated."""
    total = profile.aoi_referenced_count + profile.aoi_orphaned_count
    out = []
    for a in range(total):
        name = f"Comp{profile.index:02d}Aoi{a}"
        def_xml, storage = aoi_xml(
            name,
            input_params=[MemberSpec(f"In{k}", "DINT") for k in range(1 + a % 3)],
            output_params=[MemberSpec(f"Out{k}", "BOOL") for k in range(1 + a % 2)],
            local_tags=[MemberSpec(f"Wrk{k}", "DINT") for k in range(2 + a % 3)],
        )
        out.append((name, def_xml, storage))
    return out


def _build(profile: Profile) -> tuple[str, str]:
    types_xml, udts = _udt_specs(profile)
    aois = _aoi_specs(profile)

    tags_parts: list[str] = []
    call_instrs: list[str] = []

    # Array tags (atomic types cycled)
    for j, size in enumerate(profile.array_sizes):
        t = _ATOMIC_TYPES[j % len(_ATOMIC_TYPES)]
        tags_parts.append(tag_xml(f"Arr{j}", t, dimensions=(size,)))

    # One array-of-UDT (last UDT defined)
    last_udt_name, last_udt_members = udts[-1]
    tags_parts.append(tag_xml(
        f"UdtArr", last_udt_name, dimensions=(profile.udt_array_len,), udt_members=last_udt_members,
    ))

    # TIMER/COUNTER tags
    tags_parts.append(timer_tag_xml("MainTmr", preset=1000 + profile.index * 10))
    tags_parts.append(counter_tag_xml("MainCtr", preset=100 + profile.index))

    # AOI instances -- referenced ones get a real instance tag + call rung;
    # orphaned ones get NEITHER (declared only).
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

    # Logic: base call rungs (one per referenced AOI) + a mixed-instruction
    # sweep filling out the target rung count.
    def rung_instr(i: int) -> str:
        if i < len(call_instrs):
            return call_instrs[i]
        kind = i % 6
        if kind == 0:
            return f"XIC(Arr0[{i % profile.array_sizes[0]}])OTE(Arr1[{i % profile.array_sizes[1]}]);"
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

    modules_xml = "\n".join(_MODULE_CHAINS[cat][0] for cat in profile.module_catalogs)

    l5x = build_l5x(
        target_name=f"Composite{profile.index:02d}",
        tags_xml="\n".join(tags_parts),
        extra_datatypes_xml=types_xml,
        extra_aoi_xml=aoi_def_xml,
        extra_rungs_xml=logic_rungs,
        extra_modules_xml=modules_xml,
    )

    description = (
        f"Composite realistic-scope test #{profile.index}/50 (James, 2026-08-30, response to real "
        f"~20%+ gap found on a real customer project -- 'at least 50 large programs with io and "
        f"logic to test your generation knowledge and test aois and udts'): {profile.udt_count} UDTs "
        f"(1 nested), {profile.aoi_referenced_count} AOIs instantiated+called, "
        f"{profile.aoi_orphaned_count} AOIs declared but ORPHANED (OQ-AOIORPHAN, more real data "
        f"points at varying AOI complexity), {len(profile.array_sizes)} atomic arrays "
        f"(sizes {profile.array_sizes}) + 1 UDT array ({profile.udt_array_len} elements), TIMER+COUNTER, "
        f"{len(profile.module_catalogs)} real I/O modules ({', '.join(profile.module_catalogs)}), "
        f"{profile.rung_count} rungs mixed XIC/OTE/MOV/ADD/CPT/TON/CTU/AOI-call. 5069-L306ER/fw35.11 "
        f"(processor-family question isolated separately, OQ-BLOCKBYTE)."
    )
    return l5x, description


def main() -> None:
    for i in range(1, 51):
        profile = _profile_for_index(i)
        l5x, description = _build(profile)
        _write(l5x, f"composite_realistic_{i:02d}", description)


if __name__ == "__main__":
    main()
