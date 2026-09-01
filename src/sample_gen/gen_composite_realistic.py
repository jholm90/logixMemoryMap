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

All 50 stay on the wrapper's default processor (1756-L81E/fw35.05,
DEFAULT_PROCESSOR_TYPE in wrapper.py -- corrected 2026-08-31, this
docstring previously claimed "5069-L306ER" but build_l5x() below never
actually receives a processor_type override, so every file has always
really been on the default) -- the processor-family question (blocks vs
bytes) is already isolated separately by gen_blockbyte_l71.py/
OQ-BLOCKBYTE, and mixing that confound into this batch would make any
interaction-effect findings here ambiguous.

The composition scales across the 50 files via a deterministic index-based
schedule (documented in _profile_for_index below), not randomness -- every
file's exact feature mix is reproducible and auditable.

Run: python -m sample_gen.gen_composite_realistic
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from sample_gen.builders import (
    MemberSpec, aoi_xml, collect_nested_datatypes, counter_tag_xml, rung_xml, rungs_xml,
    tag_xml, timer_tag_xml, udt_xml,
)
from sample_gen.gen_module_sweep import _MODULE_CHAINS, _UNDIAGNOSED_RETEST_CATALOGS
from sample_gen.manifest import append_manifest_row, write_sample, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "composite"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

# James, 2026-08-31, real: composite_realistic_v2 regenerated the exact same
# already-known-bad-catalog import failures (5069-OB16/B, FANUC Robot
# R30iB Plus/A, etc. -- see gen_module_sweep.py's own
# _UNDIAGNOSED_RETEST_CATALOGS, the canonical list) because this pool
# still included them. "if its a known bug then why was it generated a
# second time? ... fix the generation script now." Fixed here at the
# source -- gen_composite_realistic_v2.py imports _MODULE_CATALOGS/
# _profile_for_index from this module, so excluding these catalogs from
# the pool fixes future generation from both. Note: composite_realistic
# _32's failure was NOT catalog-explained (no bad catalog in its mix --
# see OPEN_QUESTIONS.md/known_conversion_failures.csv), so this fix won't
# necessarily resolve that one; it remains separately tracked.
_MODULE_CATALOGS = sorted(set(_MODULE_CHAINS.keys()) - _UNDIAGNOSED_RETEST_CATALOGS)
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
    pattern already established in gen_axis_composite.py.

    Real bug caught in review before this batch was sent for testing: the
    "Nested" member on UDT 0 was built with only a bare data_type=<UDT 1's
    name> and no `nested_members` -- MemberSpec.nested_members is what
    _udt_structure_body_xml (builders.py) actually needs to recurse into a
    nested UDT's real Structure content when an INSTANCE of the containing
    UDT gets rendered; without it, that render path falls through to a
    bare "<!-- unsupported member ... -->" comment instead of real
    content. UDT 1's own member list has to exist BEFORE UDT 0's wrapper
    member can reference it here (build order matters), so UDT 1 (and
    every plain, non-nested UDT) is built first, then UDT 0 wraps it."""
    plain_members: dict[int, list[MemberSpec]] = {}
    for u in range(1, profile.udt_count):
        plain_members[u] = [
            MemberSpec(f"D{k}", "DINT") for k in range(3 + (u % 3))
        ] + [
            MemberSpec(f"I{k}", "INT") for k in range(2)
        ] + [
            MemberSpec(f"B{k}", "BOOL") for k in range(4)
        ]

    udt0_own_members = [
        MemberSpec("D0", "DINT"), MemberSpec("D1", "DINT"), MemberSpec("D2", "DINT"),
        MemberSpec("I0", "INT"), MemberSpec("I1", "INT"),
        MemberSpec("B0", "BOOL"), MemberSpec("B1", "BOOL"), MemberSpec("B2", "BOOL"), MemberSpec("B3", "BOOL"),
    ]
    if profile.udt_count >= 2:
        nested_name = f"Comp{profile.index:02d}Udt1"
        nested_target_members = plain_members[1]
        udt0_members = [MemberSpec("Nested", nested_name, nested_members=tuple(nested_target_members))] + udt0_own_members
    else:
        udt0_members = udt0_own_members

    udts: list[tuple[str, list[MemberSpec]]] = [(f"Comp{profile.index:02d}Udt0", udt0_members)]
    for u in range(1, profile.udt_count):
        udts.append((f"Comp{profile.index:02d}Udt{u}", plain_members[u]))

    types_xml_parts = [udt_xml(name, members) for name, members in udts]
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
            # REAL BUG FOUND 2026-08-31 (James, real Studio 5000 verify
            # error on composite_realistic_02/03.ACD, "Invalid number of
            # arguments for instruction" on every referenced-AOI call
            # rung): "Your AOIs have input and output parameters but they
            # need to be marked as required or visible to put them in the
            # ladder logic instance. if required then it needs a
            # hard-coded value or tag." MemberSpec defaults
            # required=False/visible=False -- _aoi_parameter_xml (see
            # builders.py) correctly renders that as Required="false"
            # Visible="false" for a plain (non-array) Input/Output
            # Parameter, which real Studio 5000 treats as HIDDEN from the
            # instruction's own call signature (not a real argument slot
            # at all). But _build() below always supplies a literal "0"/
            # tag "OutBit" argument for every In/Out param regardless,
            # so the actual call always has more operands than the real
            # (hidden) signature allows -- an argument-count mismatch.
            # Fixed with required=True, which real Studio 5000 accepts
            # either a hardcoded value or a tag reference for (matches
            # this file's own call-argument construction exactly).
            input_params=[MemberSpec(f"In{k}", "DINT", required=True) for k in range(1 + a % 3)],
            output_params=[MemberSpec(f"Out{k}", "BOOL", required=True) for k in range(1 + a % 2)],
            local_tags=[MemberSpec(f"Wrk{k}", "DINT") for k in range(2 + a % 3)],
        )
        out.append((name, def_xml, storage))
    return out


_LOCAL_ICP_SLOT_RE = re.compile(
    r'(ParentModule="Local".*?<Port Id="1" Address=")\d+("\s*Type="ICP"\s*Upstream="true"\s*/>)',
    re.DOTALL,
)


def _remap_local_icp_slot(xml: str, slot: int) -> str:
    """James, 2026-08-31, real Studio 5000 error on composite_realistic_07
    (module mix: 1794-OE4/B, 1794-OW8/A, 1794-VHSC/A): "Slot number in use
    by another module" + "Failed to set the 'ParentModule' property
    (Requested item could not be found.)" for the chain's downstream
    modules. Root cause: all three of those catalogs' _MODULE_CHAINS
    blocks were extracted from the SAME real reference export
    (RobbinsGrn_2026_05_13r00.L5X) and each one's own root module (a
    1756-CNB/D ControlNet bridge, ParentModule="Local") independently
    claims the identical real physical backplane slot that one customer's
    rack actually used (Address="3" on its ICP Port) -- correct for a
    single standalone catalog test, but a genuine collision the instant 2+
    such catalogs land in the same composite file, exactly like the IP
    collision _modules_xml_unique_ips (below) already fixes for Ethernet
    addresses. The downstream 'ParentModule not found' errors are a
    cascade: once the slot-colliding root module fails to import, its
    children (which reference it by name) can't resolve their parent
    either. Remaps ONLY the root module's own ICP-backplane Port Address
    to a given unique slot -- a catalog with no Local-parented ICP module
    at all (e.g. already Ethernet-only) is left untouched (no match, no
    collision risk)."""
    return _LOCAL_ICP_SLOT_RE.sub(rf"\g<1>{slot}\g<2>", xml, count=1)


def _modules_xml_unique_ips(catalogs: list[str]) -> str:
    """James, 2026-08-30, real bug caught by self-audit before any file was
    sent for testing: each catalog's block in gen_module_sweep.py's
    _MODULE_CHAINS was extracted from a real reference export assuming it's
    the ONLY networked device in its own file -- nearly all of them default
    to the same real "192.168.1.63" Ethernet address. Combining 2-4 real
    catalogs verbatim into one composite file (as this generator does)
    reused that identical IP across multiple distinct real devices in 33 of
    the first 50 files -- a genuine address collision, not something Studio
    5000 would ever accept from real hardware. Fixed by assigning each
    catalog in the file its own non-overlapping 192.168.1.x block (spaced
    10 apart, since the largest number of distinct real IPs any single
    catalog's own block legitimately uses is 2 -- e.g. 193-ECM-ETR/A/B) and
    remapping ONLY those literal address strings, preserving each catalog's
    own internal relative offset between its addresses (a 2-IP catalog
    keeps using two DIFFERENT addresses, just shifted to a block nobody
    else in the file is using) -- nothing else in any block is touched.

    2026-08-31: also remaps each catalog's own Local-parented ICP
    backplane slot to a unique value per catalog in the file -- see
    _remap_local_icp_slot's docstring for the real error this fixes."""
    parts = []
    for i, cat in enumerate(catalogs):
        xml, _source, _chain_len = _MODULE_CHAINS[cat]
        real_ips = sorted(set(re.findall(r"192\.168\.1\.\d+", xml)))
        base = 60 + (i + 1) * 10
        mapping = {ip: f"192.168.1.{base + j}" for j, ip in enumerate(real_ips)}
        for old, new in mapping.items():
            xml = xml.replace(old, new)
        xml = _remap_local_icp_slot(xml, slot=2 + i)
        parts.append(xml)
    return "\n".join(parts)


def _build(profile: Profile) -> tuple[str, str]:
    types_xml, udts = _udt_specs(profile)
    aois = _aoi_specs(profile)

    tags_parts: list[str] = []
    call_instrs: list[str] = []

    # Array tags (atomic types cycled)
    for j, size in enumerate(profile.array_sizes):
        t = _ATOMIC_TYPES[j % len(_ATOMIC_TYPES)]
        tags_parts.append(tag_xml(f"Arr{j}", t, dimensions=(size,)))

    # One array-of-UDT -- targets UDT 0 (the nested one, when udt_count >= 2)
    # so the nested-UDT instance render path (StructureMember recursing
    # into the Nested member's own real content) actually gets exercised,
    # not just declared and left unused.
    array_udt_name, array_udt_members = udts[0]
    tags_parts.append(tag_xml(
        f"UdtArr", array_udt_name, dimensions=(profile.udt_array_len,), udt_members=array_udt_members,
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
            # REAL BUG FOUND 2026-08-31 (James, real Studio 5000 verify
            # error on composite_realistic_02/03.ACD): "you can only have
            # OTE for BOOL or BIT within INT/DINT/SINT -- a OTE on a INT
            # is an ERROR." Arr0 is always DINT and Arr1 is always INT
            # (fixed j=0/j=1 position in _ATOMIC_TYPES's cycling, every
            # file) -- XIC/OTE directly on a whole DINT/INT array element
            # (no bit subscript) is invalid; both instructions need a
            # BOOL or a bit-level ".N" reference into an integer. Fixed
            # with an explicit ".0" bit subscript -- valid on both DINT
            # and INT regardless of which specific type Arr0/Arr1 land on.
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
        f"{profile.rung_count} rungs mixed XIC/OTE/MOV/ADD/CPT/TON/CTU/AOI-call. 1756-L81E/fw35.05 "
        f"(default processor, corrected 2026-08-31 -- see this file's module docstring; the "
        f"processor-family question is isolated separately, OQ-BLOCKBYTE)."
    )
    return l5x, description


# James, 2026-08-31: "confirm that you will have different filenames for
# the 50 tests and abandon the old ones" -- every one of the 50 original
# composite_realistic_NN files changed real content this session (AOI
# Required=true fix, XIC/OTE bit-subscript fix, and for 5 files the
# backplane-slot-collision fix), after James had already pushed a real
# l5x2acd/capture batch against the OLD names. Renamed with a "_r2" suffix
# (matching this project's established convention for a regenerated-after-
# real-bug-fix batch, e.g. modulesweep_2198_*_variant_4conn_r2) so his
# next batch run can't conflate the two. The old composite_realistic_NN.L5X
# files (no "_r2") are deleted -- zero of them ever had real actual_bytes
# captured (confirmed against manifest.csv before deleting), so nothing
# real is lost by abandoning them.
def main() -> None:
    for i in range(1, 51):
        profile = _profile_for_index(i)
        l5x, description = _build(profile)
        _write(l5x, f"composite_realistic_{i:02d}_r2", description)


if __name__ == "__main__":
    main()
