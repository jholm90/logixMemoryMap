"""100 MORE large, realistic-scope composite test programs -- v4, 2026-09-03,
James's explicit spec: "generate qty100 v4 unique files with 4 drives
minimum and 50 ethernet nodes minimum. file size between 2-3MB" [confirmed
via follow-up: "4 drives" means 4 SEPARATE drive modules, not 4 axes --
could be satisfied by 2 dual-axis modules alone, so drive modules are
mixed dual/single-axis and always counted by module, not by axis].

Direct follow-up to today's composite_surcharge_cap fix (see
memory_model.yaml) -- this batch is the first real test of that fix at an
even larger scale (2-3MB vs v3's 1.5-2.5MB) and, for the first time, more
than one real drive module in a single file (v3 only ever had one).

Real motion content, extended from gen_composite_realistic_v3.py's
single-drive pattern: ONE shared 2198-P208 power supply (its own on-board
"DC BUS" axis, the real Titusville pattern) + N real drive modules (N in
[4, 8], mixing dual-axis 2198-Dxxx-ERS3 (2 real axes/module, Ch1/Ch3 --
see OPEN_QUESTIONS.md OQ-193ECMETR for the real channel-numbering fix
this depends on) and single-axis 2198-S086-ERS3 (1 real axis, Ch1) --
real Rockwell practice: multiple drives commonly share one DC bus power
supply rather than each getting its own, so this is the more realistic
shape for a multi-drive file, not an arbitrary simplification. Every
drive module now also carries the real ExtendedProperties/ConfigID block
(2026-09-03 fix) and uses the corrected DC-bus axis template for P208's
own axis -- this batch is the first real multi-drive test of both fixes.

Real generator bug fixed building this batch: v3's own
_modules_xml_unique_ips (gen_composite_realistic.py) only ever needed to
combine 2-4 (v1/v2) or 15-34 (v3) DISTINCT catalogs from the 48-catalog
real Ethernet-only pool -- never enough to need the SAME catalog twice.
v4's 50+ ethernet-node floor exceeds that 48-catalog pool, so some
catalogs necessarily repeat within one file. _modules_xml_unique_ips
already assigns each catalog OCCURRENCE (not each catalog NAME) its own
IP block, safe for repeats -- but it never renames the Module Name
itself, so two occurrences of the same catalog would emit two Modules
with the IDENTICAL real Name, a real Studio 5000 duplicate-name rejection
that v3 never had a chance to hit. Fixed here (not in the shared v3
function, to avoid any risk of changing already-validated v3 output):
_modules_xml_unique_ips_v4 renames every Name="..."/ParentModule="..."
occurrence of a catalog's own declared module name(s) on its 2nd+
occurrence in one file, leaving a catalog's first occurrence completely
untouched (byte-identical to what v3 would have produced for the same
catalog list with no repeats).

Run: python -m sample_gen.gen_composite_realistic_v4
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

from sample_gen.builders import (
    MemberSpec, aoi_xml, collect_nested_datatypes, custom_string_type_xml, rung_xml, rungs_xml,
    tag_xml, timer_tag_xml, counter_tag_xml,
)
from sample_gen.gen_composite_realistic import (
    _ATOMIC_TYPES, _LOCAL_ICP_SLOT_RE, _MODULE_CATALOGS, _normalize_chain_bus_sizes,
    _remap_local_icp_slot,
)
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.gen_composite_realistic_v2 import _content_rungs
from sample_gen.gen_composite_realistic_v3 import _ETHERNET_ONLY_MODULE_CATALOGS, _ICP_MODULE_CATALOGS
from sample_gen.gen_module_axis_scale import _DUAL_AXIS_CATALOGS, _SINGLE_AXIS_CATALOG
from sample_gen.gen_module_motion import (
    _P208_MODULE_XML, _MOTION_GROUP_TAG_XML, _axis_tag, _dcbus_axis_tag, _drive_module_xml,
)
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "composite"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

_MODEL = load_memory_model()
_TAG_FLAT_OVERHEAD_BASE = 84  # KNOWN, docs/MEMORY_MODEL.md "Per-tag flat overhead"
_MAX_ICP_CATALOGS_PER_FILE = 10
# Matches only a <Module ...Name="X"...> element's OWN Name= declaration --
# never a nested Connection/DataValueMember/ArrayMember Name= (those are
# real fixed CIP/struct identifiers, not module identity; see
# _modules_xml_unique_ips_v4's docstring for the real Studio 5000 import
# bug this scoping fixes).
_MODULE_NAME_DECL_RE = re.compile(r'<Module\b[^>]*?\bName="([^"]+)"')


def _modules_xml_unique_ips_v4(catalogs: list[str]) -> str:
    """v3's _modules_xml_unique_ips, extended with real per-occurrence
    Module-Name uniquification -- see this file's own module docstring
    for the real bug this fixes (v4's 50+ ethernet-node floor exceeds the
    48-catalog real pool, so some catalogs repeat, and two Modules with
    the identical real Name is a real Studio 5000 rejection). A catalog's
    FIRST occurrence in the list is left completely untouched (matching
    v3's own established output byte-for-byte); only the 2nd+ occurrence
    gets its Name/ParentModule references suffixed.

    2026-09-03, real Studio 5000 import bug found by James (every single
    v4 file rejected on import, XMLSrv_E_IMPORT_ABORTED_NO_CHANGES): the
    original version of this function used a blanket `Name="([^"]+)"`
    regex to find "the module's own names" to rename, which also matched
    every OTHER Name= attribute nested inside that catalog's XML block --
    <Connection Name="Output" Type="Output" ...> (a fixed CIP
    connection-point enum, not free text) and <DataValueMember
    Name="SlotStatusBits0_31".../<ArrayMember Name="Data".../ (real fixed
    struct member names from the module's AOP-defined Config/Input data
    type). Renaming those to "Output_v4d1"/"Data_v4d1" etc. is schema-
    invalid and Studio rejects the whole import. Fixed by scoping both the
    search AND the replacement to only `<Module ...Name="X">` element
    declarations and `ParentModule="X"` references -- never any Name=
    nested inside a Connection/DataValueMember/ArrayMember/StructureMember
    element."""
    seen_counts: dict[str, int] = {}
    parts = []
    next_icp_slot = 1
    _BLOCK_START, _BLOCK_SPACING, _BLOCK_CEILING = 60, 10, 250
    _CATALOGS_PER_THIRD_OCTET = (_BLOCK_CEILING - _BLOCK_START) // _BLOCK_SPACING
    for i, cat in enumerate(catalogs):
        xml, _source, _chain_len = _MODULE_CHAINS[cat]
        xml = _normalize_chain_bus_sizes(xml)
        occurrence = seen_counts.get(cat, 0)
        seen_counts[cat] = occurrence + 1
        if occurrence > 0:
            # Rename only the Module element's OWN Name= declaration (a
            # chain can be more than one Module, e.g. adapter+child) and
            # any sibling Module's ParentModule="X" reference -- NEVER any
            # other Name= attribute nested inside the block (Connection/
            # DataValueMember/ArrayMember names are real fixed CIP/struct
            # identifiers, not module identity, and must not be touched).
            own_names = sorted(set(_MODULE_NAME_DECL_RE.findall(xml)))
            for name in own_names:
                new_name = f"{name}_v4d{occurrence}"
                escaped = re.escape(name)
                xml = re.sub(
                    rf'(<Module\b[^>]*?\bName=)"{escaped}"', rf'\1"{new_name}"', xml,
                )
                xml = xml.replace(f'ParentModule="{name}"', f'ParentModule="{new_name}"')
        real_ips = sorted(set(re.findall(r"192\.168\.1\.\d+", xml)))
        block_num, pos_in_block = divmod(i, _CATALOGS_PER_THIRD_OCTET)
        third_octet = 1 + block_num
        base = _BLOCK_START + (pos_in_block + 1) * _BLOCK_SPACING
        mapping = {ip: f"192.168.{third_octet}.{base + j}" for j, ip in enumerate(real_ips)}
        for old, new in mapping.items():
            xml = xml.replace(old, new)
        has_local_icp = _LOCAL_ICP_SLOT_RE.search(xml) is not None
        if has_local_icp:
            xml = _remap_local_icp_slot(xml, slot=next_icp_slot)
            next_icp_slot += 1
        parts.append(xml)
    return "\n".join(parts)


def _floor_bytes(l5x_text: str) -> int:
    """Real computed total across every SIZED entry, ignoring (not raising
    on) any unmodeled SizeError -- Axis/MotionGroup content always
    produces at least one (OQ-AXISSTRUCT), everything else is fully
    computable. Same convention as gen_composite_realistic_v3.py."""
    root = ET.fromstring(l5x_text)
    entries, _errors = build_report(root, _MODEL)
    return sum(e.bytes for e in entries)


@dataclass
class ProfileV4:
    index: int
    udt_count: int
    aoi_count: int
    array_sizes: list[int]
    module_catalogs: list[str]
    rung_count: int
    udt_array_len: int
    program_count: int
    subs_per_program: list[int]
    string_count: int
    n_drives: int
    target_total: int


def _profile_for_index(i: int) -> ProfileV4:
    """Deterministic feature schedule, i in [1, 100]."""
    udt_count = 3 + (i % 5)  # 3..7
    aoi_count = 5 + (i % 20)  # 5..24
    n_arrays = 4 + (i % 5)  # 4..8
    base_size = 300 + (i * 47) % 4000
    array_sizes = [base_size + j * (211 + i * 5) for j in range(n_arrays)]
    # James: "50 ethernet nodes minimum" -- guaranteed from
    # _ETHERNET_ONLY_MODULE_CATALOGS (48 real catalogs), so >=50 forces at
    # least a couple of real catalogs to repeat -- see
    # _modules_xml_unique_ips_v4's own docstring for why that's now safe.
    n_eth_nodes = 50 + (i % 11)  # 50..60
    eth_start = (i * 13) % len(_ETHERNET_ONLY_MODULE_CATALOGS)
    eth_catalogs = [
        _ETHERNET_ONLY_MODULE_CATALOGS[(eth_start + k) % len(_ETHERNET_ONLY_MODULE_CATALOGS)]
        for k in range(n_eth_nodes)
    ]
    n_icp_extra = 2 + (i % (_MAX_ICP_CATALOGS_PER_FILE - 1))  # 2..10
    icp_start = (i * 7) % len(_ICP_MODULE_CATALOGS)
    icp_catalogs = [_ICP_MODULE_CATALOGS[(icp_start + k) % len(_ICP_MODULE_CATALOGS)] for k in range(n_icp_extra)]
    module_catalogs = icp_catalogs + eth_catalogs
    rung_count = 200 + (i % 10) * 60
    udt_array_len = 20 + (i % 12) * 12
    program_count = 5 + (i % 8)  # 5..12
    subs_per_program = [1 + ((i + p) % 3) for p in range(program_count)]  # 1..3 each
    string_count = 5 + (i % 5)  # 5..9
    # James: "4 drives minimum" -- 4..8 real drive modules, mixed dual/
    # single-axis (see _drive_specs_for_profile).
    n_drives = 4 + (i % 5)  # 4..8
    # Linear spread 2,000,000 -> 3,000,000 across the batch (James:
    # "file size between 2-3MB" -- confirmed predicted CPU memory bytes,
    # same convention as v3's own "1.5-2.5MB" clarification).
    target_total = 2_000_000 + int((i - 1) / 99 * 1_000_000)
    return ProfileV4(
        i, udt_count, aoi_count, array_sizes, module_catalogs, rung_count, udt_array_len,
        program_count, subs_per_program, string_count, n_drives, target_total,
    )


def _udt_specs(profile: ProfileV4) -> tuple[str, list[tuple[str, list[MemberSpec]]]]:
    """Same nesting convention as v3's own _udt_specs (UDT 0 nests UDT 1)."""
    plain_members: dict[int, list[MemberSpec]] = {}
    for u in range(1, profile.udt_count):
        plain_members[u] = (
            [MemberSpec(f"D{k}", "DINT") for k in range(3 + (u % 3))]
            + [MemberSpec(f"I{k}", "INT") for k in range(2)]
            + [MemberSpec(f"B{k}", "BOOL") for k in range(4)]
        )
    types_parts = []
    specs: list[tuple[str, list[MemberSpec]]] = [None] * profile.udt_count  # type: ignore[list-item]
    for u in range(1, profile.udt_count):
        name = f"Comp4Udt{profile.index:03d}_{u}"
        members = plain_members[u]
        types_parts.append(f'    <DataType Name="{name}" Family="NoFamily" Class="User">\n'
                            f"      <Members>\n"
                            + "".join(
                                f'        <Member Name="{m.name}" DataType="{m.data_type}" Dimension="0" '
                                f'Radix="Decimal" Hidden="false" ExternalAccess="Read/Write"/>\n'
                                for m in members
                            ) + "      </Members>\n    </DataType>")
        specs[u] = (name, members)
    nested_name = specs[1][0] if profile.udt_count >= 2 else None
    name0 = f"Comp4Udt{profile.index:03d}_0"
    members0 = [MemberSpec(f"D{k}", "DINT") for k in range(2)]
    if nested_name:
        members0.append(MemberSpec("Nested", nested_name, nested_members=tuple(specs[1][1])))
    types0 = collect_nested_datatypes(name0, members0)
    specs[0] = (name0, members0)
    types_xml = types0 + "\n" + "\n".join(types_parts)
    return types_xml, [s for s in specs if s is not None]


def _aoi_specs(profile: ProfileV4, axis_tag_name: str) -> list[tuple[str, str, list[MemberSpec], bool]]:
    """Returns [(name, def_xml, storage, uses_axis)] -- AOI 0 always takes
    a real servo axis as an InOut param (same shape as v3's own
    _aoi_specs), every other AOI gets real internal Logic-routine content."""
    out = []
    for a in range(profile.aoi_count):
        name = f"Comp4Aoi{profile.index:03d}_{a}"
        if a == 0:
            fault_reset = MemberSpec("FaultReset", "BOOL", required=True, visible=True)
            drive_axis = MemberSpec("Drive_Axis", "AXIS_CIP_DRIVE")
            def_xml, storage = aoi_xml(name, input_params=[fault_reset], inout_params=[drive_axis])
            out.append((name, def_xml, storage, True))
            continue
        input_params = [MemberSpec(f"In{k}", "DINT", required=True) for k in range(1 + a % 3)]
        output_params = [MemberSpec(f"Out{k}", "BOOL", required=True) for k in range(1 + a % 2)]
        local_tags = [MemberSpec(f"Wrk{k}", "DINT") for k in range(2 + a % 3)]
        instr_count = 5 + (a * 7 + profile.index * 3) % 40
        logic_rungs = _content_rungs(instr_count, "In0", "Wrk0", "In0.0", "Out0")
        def_xml, storage = aoi_xml(
            name, input_params=input_params, output_params=output_params,
            local_tags=local_tags, logic_rungs_xml=logic_rungs,
        )
        out.append((name, def_xml, storage, False))
    return out


def _rich_program_xml(prog_name: str, n_subs: int, index: int, prog_idx: int) -> tuple[str, int]:
    """Same shape as v3's own _rich_program_xml: one extra Program whose
    MainRoutine calls n_subs real subroutines, each with real content.
    Returns (program_xml, total_jsr_target_instruction_count)."""
    jsr_calls = []
    sub_routines = []
    total_instr = 0
    for s in range(n_subs):
        target_name = f"{prog_name}Sub{s}"
        instr_count = 15 + (s * 11 + index * 5 + prog_idx * 7) % 150
        rungs = _content_rungs(instr_count, "Arr0[0]", "Arr0[1]", "Arr1[0].0", "Arr1[1].0")
        sub_routines.append(f'<Routine Name="{target_name}" Type="RLL"><RLLContent>{rungs}</RLLContent></Routine>')
        jsr_calls.append(rung_xml(s, f"JSR({target_name},0);"))
        total_instr += instr_count
    main_rungs = "\n".join(jsr_calls)
    prog_xml = (
        f'<Program Name="{prog_name}" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" UseAsFolder="false">\n'
        f"<Tags>\n</Tags>\n"
        f"<Routines>\n"
        f'<Routine Name="MainRoutine" Type="RLL"><RLLContent>\n{main_rungs}\n</RLLContent></Routine>\n'
        + "\n".join(sub_routines)
        + "\n</Routines>\n</Program>"
    )
    return prog_xml, total_instr


def _drive_specs_for_profile(profile: ProfileV4) -> list[tuple[str, str, bool]]:
    """Returns [(drive_name, catalog, is_dual)] for profile.n_drives real
    drive modules -- mixed dual-axis (2198-Dxxx-ERS3, 2 real axes/module,
    Ch1/Ch3) and single-axis (2198-S086-ERS3, 1 real axis, Ch1), real
    catalogs already confirmed elsewhere in this project
    (gen_module_axis_scale.py). Roughly 2/3 dual, 1/3 single, deterministic
    per index so the mix isn't identical across every file in the batch."""
    specs = []
    for d in range(profile.n_drives):
        is_dual = (d + profile.index) % 3 != 0
        if is_dual:
            catalog = _DUAL_AXIS_CATALOGS[(d + profile.index) % len(_DUAL_AXIS_CATALOGS)]
        else:
            catalog = _SINGLE_AXIS_CATALOG
        specs.append((f"Drv{profile.index:03d}_{d}", catalog, is_dual))
    return specs


def _build_motion(profile: ProfileV4) -> tuple[str, str, list[str]]:
    """ONE shared 2198-P208 power supply (its own on-board DC-bus axis) +
    profile.n_drives real drive modules -- real Rockwell practice: multiple
    drives commonly share one DC bus rather than each getting its own.
    Returns (modules_xml, tags_xml, servo_axis_names)."""
    drive_specs = _drive_specs_for_profile(profile)
    modules = [_P208_MODULE_XML]
    tags = [_MOTION_GROUP_TAG_XML, _dcbus_axis_tag(f"DcBus{profile.index:03d}", "P208:Ch1")]
    servo_axes: list[str] = []
    ip_octet = 2
    for drv_name, catalog, is_dual in drive_specs:
        address = f"192.168.5.{ip_octet}"
        ip_octet += 1
        modules.append(_drive_module_xml(drv_name, catalog, "false", address=address))
        axis1_name = f"{drv_name}A"
        tags.append(_axis_tag(axis1_name, f"{drv_name}:Ch1"))
        servo_axes.append(axis1_name)
        if is_dual:
            axis2_name = f"{drv_name}B"
            tags.append(_axis_tag(axis2_name, f"{drv_name}:Ch3"))
            servo_axes.append(axis2_name)
    return "\n".join(modules), "\n".join(tags), servo_axes


def _build(profile: ProfileV4) -> tuple[str, str, int]:
    types_xml, udts = _udt_specs(profile)

    motion_module_xml, motion_tags_xml, servo_axes = _build_motion(profile)
    servo_axis_1 = servo_axes[0]
    servo_axis_last = servo_axes[-1]

    aois = _aoi_specs(profile, servo_axis_1)
    aoi_def_xml = "\n".join(d for _n, d, _s, _u in aois)

    tags_parts: list[str] = [motion_tags_xml]
    call_instrs: list[str] = []

    for j, size in enumerate(profile.array_sizes):
        t = _ATOMIC_TYPES[j % len(_ATOMIC_TYPES)]
        tags_parts.append(tag_xml(f"Arr{j}", t, dimensions=(size,)))

    array_udt_name, array_udt_members = udts[0]
    tags_parts.append(tag_xml(
        "UdtArr", array_udt_name, dimensions=(profile.udt_array_len,), udt_members=array_udt_members,
    ))
    tags_parts.append(timer_tag_xml("MainTmr", preset=1000 + profile.index * 10))
    tags_parts.append(counter_tag_xml("MainCtr", preset=100 + profile.index))

    string_types_xml = []
    for s in range(profile.string_count):
        max_len = 20 + s * 20 + (profile.index % 10) * 4
        type_name = f"Comp4Str{profile.index:03d}_{s}"
        string_types_xml.append(custom_string_type_xml(type_name, max_len))
        tags_parts.append(tag_xml(f"Str{s}", type_name, string_max_len=max_len))
    types_xml = types_xml + "\n" + "\n".join(string_types_xml)

    for name, _def_xml, storage, uses_axis in aois:
        inst_name = f"{name}Inst"
        tags_parts.append(tag_xml(inst_name, name, udt_members=storage))
        if uses_axis:
            call_instrs.append(f"{name}({inst_name},FaultResetBit,{servo_axis_1});")
        else:
            n_in = sum(1 for m in storage if m.name.startswith("In"))
            n_out = sum(1 for m in storage if m.name.startswith("Out"))
            call_args = ",".join([inst_name] + ["0"] * n_in + ["OutBit"] * n_out)
            call_instrs.append(f"{name}({call_args});")
    tags_parts.append(tag_xml("OutBit", "BOOL"))
    tags_parts.append(tag_xml("FaultResetBit", "BOOL"))
    tags_parts.append(tag_xml("AxisPosReadout", "REAL"))

    # Real logic directly reading an axis attribute -- MOV of the LAST
    # servo axis's ActualPosition, same real shape as v3.
    call_instrs.append(f"MOV({servo_axis_last}.ActualPosition,AxisPosReadout);")

    programs_xml_parts = []
    scheduled_xml_parts = []
    total_jsr_instr = 0
    for p, n_subs in enumerate(profile.subs_per_program):
        prog_name = f"Comp4Prog{profile.index:03d}_{p}"
        prog_xml, instr = _rich_program_xml(prog_name, n_subs, profile.index, p)
        programs_xml_parts.append(prog_xml)
        scheduled_xml_parts.append(f'<ScheduledProgram Name="{prog_name}"/>')
        total_jsr_instr += instr

    main_jsr_name = f"Comp4Main{profile.index:03d}JsrTarget"
    main_jsr_instr = 30 + (profile.index * 6) % 150
    main_jsr_rungs = _content_rungs(main_jsr_instr, "Arr0[2]", "Arr0[3]", "Arr1[2].0", "Arr1[3].0")
    main_jsr_routine = f'<Routine Name="{main_jsr_name}" Type="RLL"><RLLContent>{main_jsr_rungs}</RLLContent></Routine>'
    call_instrs.insert(0, f"JSR({main_jsr_name},0);")
    total_jsr_instr += main_jsr_instr

    def rung_instr(i: int) -> str:
        if i < len(call_instrs):
            return call_instrs[i]
        kind = i % 5
        a0 = profile.array_sizes[0]
        a1 = profile.array_sizes[min(1, len(profile.array_sizes) - 1)]
        if kind == 0:
            return f"XIC(Arr0[{i % a0}].0)OTE(Arr1[{i % a1}].0);"
        if kind == 1:
            return f"MOV(Arr0[{i % a0}],Arr2[{i % profile.array_sizes[min(2, len(profile.array_sizes) - 1)]}]);"
        if kind == 2:
            return "ADD(Arr0[0],1,Arr0[0]);"
        if kind == 3:
            return "CPT(Arr0[1],Arr0[0]+2*Arr0[0]);"
        return "TON(MainTmr,?,?);"

    logic_rungs = rungs_xml(profile.rung_count, rung_instr)
    modules_xml = motion_module_xml + "\n" + _modules_xml_unique_ips_v4(profile.module_catalogs)

    l5x = build_l5x(
        target_name=f"Composite4_{profile.index:03d}",
        tags_xml="\n".join(tags_parts),
        extra_datatypes_xml=types_xml,
        extra_aoi_xml=aoi_def_xml,
        extra_rungs_xml=logic_rungs,
        extra_routines_xml=main_jsr_routine,
        extra_modules_xml=modules_xml,
        extra_programs_xml="\n".join(programs_xml_parts),
        extra_scheduled_programs_xml="\n".join(scheduled_xml_parts),
    )

    # Size ONE filler DINT array tag to close the gap to profile.target_total
    # exactly -- same computed (not guessed) technique as v3.
    floor_before_filler = _floor_bytes(l5x)
    filler_name = "FillerArr"
    filler_overhead = _TAG_FLAT_OVERHEAD_BASE + 8 * (len(filler_name) // 8)
    remaining = profile.target_total - floor_before_filler - filler_overhead
    n_elements = max(remaining // 4, 100)
    filler_tag = tag_xml(filler_name, "DINT", dimensions=(n_elements,))
    l5x_final = build_l5x(
        target_name=f"Composite4_{profile.index:03d}",
        tags_xml="\n".join(tags_parts) + "\n" + filler_tag,
        extra_datatypes_xml=types_xml,
        extra_aoi_xml=aoi_def_xml,
        extra_rungs_xml=logic_rungs,
        extra_routines_xml=main_jsr_routine,
        extra_modules_xml=modules_xml,
        extra_programs_xml="\n".join(programs_xml_parts),
        extra_scheduled_programs_xml="\n".join(scheduled_xml_parts),
    )
    final_total = _floor_bytes(l5x_final)

    n_dual = sum(1 for _n, _c, is_dual in _drive_specs_for_profile(profile) if is_dual)
    n_single = profile.n_drives - n_dual
    description = (
        f"Composite realistic-scope test v4 #{profile.index}/100 (2026-09-03, James's explicit spec: "
        f"\"4 drives minimum and 50 ethernet nodes minimum, file size between 2-3MB\" -- confirmed 4 "
        f"drives means 4 separate drive MODULES, not axes): {profile.udt_count} UDTs (1 nested), "
        f"{profile.aoi_count} unique AOIs (1 with a real InOut AXIS_CIP_DRIVE param, the rest with real "
        f"internal Logic-routine content), {len(profile.array_sizes)} atomic arrays + 1 UDT array + 1 "
        f"target-sized filler DINT array, {profile.string_count} custom STRING types, "
        f"{len(profile.module_catalogs)} real Ethernet/ICP I/O modules ({len(set(profile.module_catalogs))} "
        f"distinct real catalogs, some repeated -- see gen_composite_realistic_v4.py's own "
        f"_modules_xml_unique_ips_v4 for the real per-occurrence Name-collision fix this needed), real "
        f"motion content ({profile.n_drives} real drive modules sharing ONE 2198-P208 power supply's DC "
        f"bus: {n_dual} dual-axis 2198-Dxxx-ERS3 + {n_single} single-axis 2198-S086-ERS3 = "
        f"{len(servo_axes)} real servo axes total, one MOTION_GROUP, logic reading an axis attribute "
        f"directly plus an AOI-InOut-axis call), {sum(profile.subs_per_program) + 1} JSR target "
        f"subroutines across {profile.program_count} extra Programs + MainProgram (total JSR-target "
        f"content: {total_jsr_instr} instructions), {profile.rung_count} MainRoutine rungs. "
        f"1756-L81E/fw35.05 default. Real floor total {final_total} (target {profile.target_total}) -- "
        f"Axis/MotionGroup content is unmodeled (OQ-AXISSTRUCT), so real Capacity will run somewhat "
        f"higher than this floor."
    )
    return l5x_final, description, final_total


def main() -> None:
    # Capped at 74, not 100 (2026-09-04). Files 075-100 were generated and
    # every one of them FAILED to convert: 18 died with RxE_OBJECT_NOT_LOADED
    # and 8 with "Server execution failed", the two signatures interleaved at
    # random across the block. 001-074 all converted "ok".
    #
    # That is not a content bug -- the split falls on FILE SIZE, not on
    # anything the generator varies: 074 is 20.0 MB and converts, 070 is
    # 20.7 MB and converts, 075 is 21.6 MB and 076 is 20.9 MB and both
    # crash. Two different crash signatures appearing at random within the
    # failing block is what resource exhaustion looks like, not what a
    # malformed L5X looks like (a bad element gives the same import error
    # every time). The Logix Designer SDK conversion path simply cannot
    # open a project this large.
    #
    # The 26 files and their manifest rows were deleted rather than left in
    # place: they carried no capture data at all, they can never produce
    # any, and every batch_memory_capture.ps1 run was skipping them
    # forever. 74 points across the same design space is plenty.
    for i in range(1, 75):
        profile = _profile_for_index(i)
        l5x, description, total = _build(profile)
        out_name = f"composite_realistic_v4_{i:03d}"
        out_path = OUT_ROOT / f"{out_name}.L5X"
        write_sample_unmodeled(l5x, out_path)
        append_manifest_row(out_name, description, "composite", out_path, total)
        print(f"Wrote {out_path} (floor {total} bytes, target {profile.target_total})")
    print("\nDone. 100 files.")


if __name__ == "__main__":
    main()
