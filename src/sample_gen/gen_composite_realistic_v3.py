"""50 MORE large, realistic-scope composite test programs -- v3, 2026-09-02,
James's explicit spec after reviewing a real production file's accuracy:
"generate another 50 unique files (v3) with these requirements:
1. 1.5-2.5MB target size (you making 10kb files makes the error much less
   noticeable) [clarified: 1,500,000-2,500,000 bytes of predicted CPU
   memory, not L5X file size]
2. 15+ ethernet nodes minimum
3. 2 servo axis minimum (sample per the titusville file with MotionGroup,
   one power supply with DCBUS axis, Motion Axis and logic using the axis
   tags)
4. 5+ logic programs with MAIN/Main routine and subroutine calls
5. 5+ unique AOI's
6. 5+ custom strings"

Direct follow-up to the real accuracy test on that production file: predicted
3,959,604 vs real 3,676,072 (+7.71%, outside the <2% target). Root-caused to
the 2026-09-02 composite-scale JSR/AOI surcharge (fit from v1/v2's 22 files,
each with exactly ONE JSR target) badly over-generalizing to a real file with
179 distinct JSR targets -- see OPEN_QUESTIONS.md OQ-COMPOSITESCALE. This
batch is designed to close that gap for real: EVERY file declares 5-12 extra
Programs, each with 1-3 real subroutines (so file-level JSR-target counts
span roughly 30-100+ across the batch, not always 1), giving the regression
enough real spread to tell whether the true relationship is linear per
instruction, flat per target, or saturating -- the same shape question
already answered for module_overhead's non-additive multi-module marginal
cost.

Real motion content added for the first time at composite scale (James: "2
servo axis minimum...sample per the titusville file"): one 2198-P208 power
supply with its own on-board axis (the real "DC BUS axis" pattern -- the
power supply's own AXIS_CIP_DRIVE tag) + one 2198-D012-ERS3 dual-axis drive
module (real "Motion Axis" x2, satisfying "2 servo axis minimum" off ONE
module, matching gen_module_motion.py's already-confirmed real shape) + a
MOTION_GROUP tag shared by all three. Real logic references the axis tags
directly (a MOV of Axis.ActualPosition into an ordinary REAL tag) AND via a
DriveAxis-shaped AOI taking the servo axis as an InOut parameter (real shape
from gen_axis_composite.py). Axis/MotionGroup content is a predefined
structure this project's engine can't size (OQ-AXISSTRUCT) -- every file
here is necessarily "unmodeled" in the write_sample_unmodeled sense, but
unlike the tiny axis-only isolation files elsewhere, the REST of this file
(arrays/UDTs/AOIs/modules/custom-strings/logic) is fully computable, so the
real floor total (not 0) is what gets logged and sized against the
1.5-2.5MB target -- true real Capacity will run somewhat higher than this
floor since the axis content itself isn't included.

Target total is hit by computing every REQUIRED structural element first,
measuring the resulting floor via this project's own sizing engine, then
sizing ONE filler DINT array tag to close the gap exactly (DINT array sizing
has zero packing ambiguity, already confirmed elsewhere in this project) --
not guessed, not padded with random content.

Run: python -m sample_gen.gen_composite_realistic_v3
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

from sample_gen.builders import (
    MemberSpec, aoi_xml, collect_nested_datatypes, custom_string_type_xml, rung_xml, rungs_xml,
    tag_xml, timer_tag_xml, counter_tag_xml,
)
from sample_gen.gen_axis_composite import _AXIS_TAG_XML
from sample_gen.gen_composite_realistic import (
    _ATOMIC_TYPES, _LOCAL_ICP_SLOT_RE, _MODULE_CATALOGS, _modules_xml_unique_ips,
)
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.gen_composite_realistic_v2 import _content_rungs
from sample_gen.gen_module_motion import _P208_MODULE_XML, _MOTION_GROUP_TAG_XML, _axis_tag, _drive_module_xml
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "composite"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

_MODEL = load_memory_model()
_TAG_FLAT_OVERHEAD_BASE = 84  # KNOWN, docs/MEMORY_MODEL.md "Per-tag flat overhead"

# 2026-09-02, real bug found generating this batch: v1/v2 only ever put 2-4
# module catalogs in one file, so nobody had hit this before -- the CPU's
# own default Local backplane only has 17 real ICP slots (_ICP_BUS_SIZE,
# wrapper.py), so a file whose full 15-24-module pool leans too heavily on
# ICP-Local-backplane catalogs genuinely overflows a real chassis (Studio
# 5000's own "Chassis size exceeds the allowable size" error, confirmed via
# this project's own chassis_size_exceeded lint check). Real ControlLogix
# plants don't put 15+ modules on one local rack either -- they distribute
# I/O across remote/networked adapters, which is exactly what most of
# James's real TitusvilleTrimmer file does (its own local ICP-backplane
# module count was small; almost everything else was Ethernet/rack-
# aliased). Partitioning the pool and capping the ICP share to a safe
# number below the real 17-slot limit is the structurally-realistic fix,
# not a workaround.
_ICP_MODULE_CATALOGS = [c for c in _MODULE_CATALOGS if _LOCAL_ICP_SLOT_RE.search(_MODULE_CHAINS[c][0])]
_ETHERNET_ONLY_MODULE_CATALOGS = [c for c in _MODULE_CATALOGS if c not in _ICP_MODULE_CATALOGS]
_MAX_ICP_CATALOGS_PER_FILE = 10


def _floor_bytes(l5x_text: str) -> int:
    """Real computed total across every SIZED entry, ignoring (not raising
    on) any unmodeled SizeError -- this file's Axis/MotionGroup content
    always produces at least one (OQ-AXISSTRUCT), but everything else
    (arrays/UDTs/AOIs/modules/custom-strings/logic) is fully computable and
    worth a real floor total, unlike write_sample_unmodeled's usual
    predicted_bytes=0 convention for axis-only isolation files that have
    nothing else worth summing."""
    root = ET.fromstring(l5x_text)
    entries, _errors = build_report(root, _MODEL)
    return sum(e.bytes for e in entries)


@dataclass
class ProfileV3:
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
    target_total: int


def _profile_for_index(i: int) -> ProfileV3:
    """Deterministic feature schedule, i in [1, 50]. Every count is spread
    across a real range (not held at James's stated floor) so this batch
    doubles as calibration data for the AOI/JSR-at-scale question, not just
    a structural checklist."""
    udt_count = 3 + (i % 4)  # 3..6
    aoi_count = 5 + (i % 20)  # 5..24
    n_arrays = 4 + (i % 5)  # 4..8
    base_size = 300 + (i * 47) % 4000
    array_sizes = [base_size + j * (211 + i * 5) for j in range(n_arrays)]
    # James: "15+ ethernet nodes minimum" -- guaranteed by drawing the base
    # count entirely from _ETHERNET_ONLY_MODULE_CATALOGS (each one's OWN
    # root module is ParentModPortId="2"/Ethernet-attached to Local, a real
    # network-addressed device). A handful of plain local-backplane cards
    # (_ICP_MODULE_CATALOGS -- ParentModPortId="1"/ICP, no Ethernet
    # presence of their own, e.g. 1756-IB16) are added ON TOP for realism/
    # diversity, not counted toward the 15+ floor, capped well under the
    # real 17-slot chassis limit.
    n_eth_nodes = 15 + (i % 10)  # 15..24
    eth_start = (i * 11) % len(_ETHERNET_ONLY_MODULE_CATALOGS)
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
    program_count = 5 + (i % 8)  # 5..12 (James: "5+ logic programs")
    subs_per_program = [1 + ((i + p) % 3) for p in range(program_count)]  # 1..3 each
    string_count = 5 + (i % 5)  # 5..9 (James: "5+ custom strings")
    # Linear spread 1,550,000 -> 2,450,000 across the batch, safely inside
    # James's 1.5-2.5MB band with margin for the filler-array rounding step.
    target_total = 1_550_000 + int((i - 1) / 49 * 900_000)
    return ProfileV3(
        i, udt_count, aoi_count, array_sizes, module_catalogs, rung_count, udt_array_len,
        program_count, subs_per_program, string_count, target_total,
    )


def _udt_specs(profile: ProfileV3) -> tuple[str, list[tuple[str, list[MemberSpec]]]]:
    """Same nesting convention as gen_composite_realistic.py's own
    _udt_specs (UDT 0 nests UDT 1), written locally so this generator isn't
    coupled to v1's Profile shape."""
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
        name = f"Comp3Udt{profile.index:02d}_{u}"
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
    name0 = f"Comp3Udt{profile.index:02d}_0"
    members0 = [MemberSpec(f"D{k}", "DINT") for k in range(2)]
    if nested_name:
        members0.append(MemberSpec("Nested", nested_name, nested_members=tuple(specs[1][1])))
    types0 = collect_nested_datatypes(name0, members0)
    specs[0] = (name0, members0)
    types_xml = types0 + "\n" + "\n".join(types_parts)
    return types_xml, [s for s in specs if s is not None]


def _aoi_specs(profile: ProfileV3, axis_tag_name: str) -> list[tuple[str, str, list[MemberSpec], bool]]:
    """Returns [(name, def_xml, storage, uses_axis)] -- AOI 0 always takes
    the servo axis as an InOut param (James: "logic using the axis tags"),
    real shape from gen_axis_composite.py's group_axis_aoi_inout. Every
    other AOI gets real internal Logic-routine content scaled by index,
    same OQ-AOIINTERNALLOGIC pattern already validated in v2."""
    out = []
    for a in range(profile.aoi_count):
        name = f"Comp3Aoi{profile.index:02d}_{a}"
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
    """One extra Program: MainRoutine calling n_subs real subroutines, each
    with real content (James: "5+ logic programs with MAIN/Main routine and
    subroutine calls"). Subroutine rungs reference Controller-scope Arr0/
    Arr1 (always present, see _build) -- no Program-local tags needed.
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


def _build(profile: ProfileV3) -> tuple[str, str, int]:
    types_xml, udts = _udt_specs(profile)

    # Motion: P208 power supply (its own on-board axis = the real "DC BUS
    # axis" pattern) + D012 dual-axis drive (2 real servo axes off one
    # module, matching gen_module_motion.py's confirmed real shape).
    motion_module_xml = _P208_MODULE_XML + "\n" + _drive_module_xml(
        f"D012_{profile.index:02d}", "2198-D012-ERS3", "false", address="192.168.5.2",
    )
    servo_axis_1 = f"Servo{profile.index:02d}A"
    servo_axis_2 = f"Servo{profile.index:02d}B"
    motion_tags_xml = "\n".join([
        _MOTION_GROUP_TAG_XML,
        _axis_tag(f"DcBus{profile.index:02d}", "P208:Ch1"),
        _axis_tag(servo_axis_1, f"D012_{profile.index:02d}:Ch1"),
        _axis_tag(servo_axis_2, f"D012_{profile.index:02d}:Ch2"),
    ])

    aois = _aoi_specs(profile, servo_axis_1)
    aoi_def_xml = "\n".join(d for _n, d, _s, _u in aois)

    tags_parts: list[str] = [motion_tags_xml]
    call_instrs: list[str] = []

    for j, size in enumerate(profile.array_sizes):
        t = _ATOMIC_TYPES[j % len(_ATOMIC_TYPES)]
        tags_parts.append(tag_xml(f"Arr{j}", t, dimensions=(size,)))
    # _rich_program_xml's subroutines always reference Arr0 (DINT-cycled at
    # j=0 above, per _ATOMIC_TYPES order) and Arr1 -- guaranteed present
    # since n_arrays >= 4 for every profile.

    array_udt_name, array_udt_members = udts[0]
    tags_parts.append(tag_xml(
        "UdtArr", array_udt_name, dimensions=(profile.udt_array_len,), udt_members=array_udt_members,
    ))
    tags_parts.append(timer_tag_xml("MainTmr", preset=1000 + profile.index * 10))
    tags_parts.append(counter_tag_xml("MainCtr", preset=100 + profile.index))

    # 5+ custom STRING types (James), each declared as its own DataType +
    # one Controller-scope tag of that type.
    string_types_xml = []
    for s in range(profile.string_count):
        max_len = 20 + s * 20 + (profile.index % 10) * 4
        type_name = f"Comp3Str{profile.index:02d}_{s}"
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

    # Real logic directly reading an axis attribute (James: "logic using
    # the axis tags") -- MOV is a real output instruction, no bit-level
    # subscript concern (ActualPosition is a REAL member of the axis
    # structure, referenced the same way any real corpus MAM/MAH call does).
    call_instrs.append(f"MOV({servo_axis_2}.ActualPosition,AxisPosReadout);")

    # 5+ extra logic Programs, each with MainRoutine + real subroutine
    # calls (James). MainProgram itself also gets one JSR target below, so
    # every program in the file (not just the extras) exercises the same
    # real shape.
    programs_xml_parts = []
    scheduled_xml_parts = []
    total_jsr_instr = 0
    for p, n_subs in enumerate(profile.subs_per_program):
        prog_name = f"Comp3Prog{profile.index:02d}_{p}"
        prog_xml, instr = _rich_program_xml(prog_name, n_subs, profile.index, p)
        programs_xml_parts.append(prog_xml)
        scheduled_xml_parts.append(f'<ScheduledProgram Name="{prog_name}"/>')
        total_jsr_instr += instr

    main_jsr_name = f"Comp3Main{profile.index:02d}JsrTarget"
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
    modules_xml = motion_module_xml + "\n" + _modules_xml_unique_ips(profile.module_catalogs)

    l5x = build_l5x(
        target_name=f"Composite3_{profile.index:02d}",
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
    # exactly -- DINT array sizing is zero-packing-ambiguity KNOWN (4 bytes/
    # element), tag flat overhead is KNOWN (84 + 8*floor(name_len/8)), so
    # this is computed, not guessed, and verified against the real engine.
    floor_before_filler = _floor_bytes(l5x)
    filler_name = "FillerArr"
    filler_overhead = _TAG_FLAT_OVERHEAD_BASE + 8 * (len(filler_name) // 8)
    remaining = profile.target_total - floor_before_filler - filler_overhead
    n_elements = max(remaining // 4, 100)
    filler_tag = tag_xml(filler_name, "DINT", dimensions=(n_elements,))
    l5x_final = build_l5x(
        target_name=f"Composite3_{profile.index:02d}",
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

    description = (
        f"Composite realistic-scope test v3 #{profile.index}/50 (2026-09-02, James's explicit spec "
        f"after the real TitusvilleTrimmer accuracy test found the composite-scale JSR/AOI surcharge "
        f"badly over-generalizes at real scale -- see OPEN_QUESTIONS.md OQ-COMPOSITESCALE): "
        f"{profile.udt_count} UDTs (1 nested), {profile.aoi_count} unique AOIs (1 with a real InOut "
        f"AXIS_CIP_DRIVE param, the rest with real internal Logic-routine content), {len(profile.array_sizes)} "
        f"atomic arrays + 1 UDT array + 1 target-sized filler DINT array, {profile.string_count} custom "
        f"STRING types, {len(profile.module_catalogs)} real Ethernet I/O modules, real motion content "
        f"(2198-P208 power supply with its own on-board 'DC BUS' axis + 2198-D012-ERS3 dual-axis drive "
        f"= 2 real servo axes, one MOTION_GROUP, logic reading an axis attribute directly plus an "
        f"AOI-InOut-axis call), {sum(profile.subs_per_program) + 1} JSR target subroutines across "
        f"{profile.program_count} extra Programs + MainProgram (total JSR-target content: {total_jsr_instr} "
        f"instructions), {profile.rung_count} MainRoutine rungs. 1756-L81E/fw35.05 default. Real floor "
        f"total {final_total} (target {profile.target_total}) -- Axis/MotionGroup content is unmodeled "
        f"(OQ-AXISSTRUCT), so real Capacity will run somewhat higher than this floor."
    )
    return l5x_final, description, final_total


def main() -> None:
    for i in range(1, 51):
        profile = _profile_for_index(i)
        l5x, description, total = _build(profile)
        out_name = f"composite_realistic_v3_{i:02d}"
        out_path = OUT_ROOT / f"{out_name}.L5X"
        write_sample_unmodeled(l5x, out_path)
        append_manifest_row(out_name, description, "composite", out_path, total)
        print(f"Wrote {out_path} (floor {total} bytes, target {profile.target_total})")
    print("\nDone. 50 files.")


if __name__ == "__main__":
    main()
