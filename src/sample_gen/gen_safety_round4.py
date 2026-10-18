"""OQ-SAFETYPARTITION, round 4: what rounds 1-3 left open that needs no Studio seed.

Spec: TASKS 0x. Same platform, plant and builder as rounds 2 and 3 (gen_safety_round2
.build), so each file differences against round 1's captured safe_n00 or a control in
its own family, except the twins and bases, which are the platform under test.

  safe_map_<n>                  n standard -> safety tag-mapping pairs over 200 + 200 DINTs
  safe_lock_trial               safe_n00 with SafetyLocked="true": does a locked project
                                import, and does locking move either reading
  safe_aoi_<inst|call>_<n>      safety AOI instances and calls at 5 and 60 (20 in round 3)
  safe_aoi_p<k>_def             safety AOIs with 6 and 12 parameters (4 in round 3)
  safe_aoi_r10_def, _l9_def     10 internal rungs and no locals; 9 locals and one rung
  safe_rtn_name<k>              one uncalled safety routine named with 16/24/40 characters
  safe_lg_<atan2|cop|fll>_100   the three corrected instructions at a second count
  safe_sref2_*                  standard MOV from a scalar safety DINT, and its control
  safetwin_*                    1756-L81E twins of safe_udt_s_def, safe_udt_l_def and
                                safe_sref_ctl: the safety controller's or the engine's
  SafeBase*                     the safety base and one content step on 5069-L330ERMS2 and
                                5069-L320ERMS2 at v35 and 1756-L81ES at v34 and v32

Safety I/O, signature: not here (Studio seeds; a signature cannot be generated).

Run: python -m sample_gen.gen_safety_round4 [--only REGEX]
"""

from __future__ import annotations

import argparse
import re

from sample_gen import gen_safety_partition as G
from sample_gen import gen_safety_round2 as R
from sample_gen import gen_safety_round3 as R3
from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OQ = "OQ-SAFETYPARTITION"


# --- builders ------------------------------------------------------------------------

def with_tag_map(l5x: str, pairs: list[tuple[str, str]]) -> str:
    """SafetyInfo carrying a SafetyTagMap: ' Std=Safety, Std2=Safety2', standard first."""
    if not pairs:
        return l5x
    text = " " + ", ".join(f"{std}={safe}" for std, safe in pairs)
    return re.sub(r"(<SafetyInfo [^>]*?)\s*/>", rf"\1>\n<SafetyTagMap>{text}</SafetyTagMap>\n</SafetyInfo>", l5x, count=1)


def safety_aoi(inputs: int = 1, outputs: int = 1, locals_: int = 0, rungs: list[str] | None = None) -> tuple[str, list]:
    """A Class="Safety" AOI with required BOOL inputs and outputs (round 3's shape at 1/1)."""
    ins = [MemberSpec("InA" if inputs == 1 else f"In{k}", "BOOL", required=True) for k in range(inputs)]
    outs = [MemberSpec("OutQ" if outputs == 1 else f"Out{k}", "BOOL", required=True) for k in range(outputs)]
    locs = [MemberSpec(f"Loc{k}", "BOOL") for k in range(locals_)]
    body = rungs or [f"XIC({ins[0].name})OTE({outs[0].name});"]
    xml, storage = aoi_xml(R3.SAFE_AOI, input_params=ins, output_params=outs, local_tags=locs,
                           logic_rungs_xml="\n".join(rung_xml(i, r) for i, r in enumerate(body)))
    return xml.replace(f'<AddOnInstructionDefinition Name="{R3.SAFE_AOI}"',
                       f'<AddOnInstructionDefinition Name="{R3.SAFE_AOI}" Class="Safety"', 1), storage


def build_twin(name: str, controller_tags: list[str] = (), datatypes_xml: str = "") -> str:
    """A 1756-L81E v35 standard project on the plant: the twin of a safety file's standard side."""
    arm = {"tags_xml": "\n".join(controller_tags)}
    if datatypes_xml:
        arm["extra_datatypes_xml"] = datatypes_xml
    return build_l5x(name, **with_baseline(**arm))


# (sample_id stem, ProcessorType, MajorRev, SoftwareRevision)
BASE_PLATFORMS = (("5069l330_v35", "5069-L330ERMS2", "35", "35.05"),
                  ("5069l320_v35", "5069-L320ERMS2", "35", "35.05"),
                  ("l81es_v34", "1756-L81ES", "34", "34.01"),
                  ("l81es_v32", "1756-L81ES", "32", "32.04"))


def build_base(name: str, processor: str, major: str, software: str, content: bool) -> str:
    """The safety File > New shell on the plant, on another platform or firmware; with
    content, 50 controller safety DINTs and 10 RIN rungs (both measured on L81ES v35)."""
    tags, rungs = G.instruction_pair("RIN", 10) if content else ([], [])
    ctl = [R.ctl_tag(f"SafeDint{i:04d}", "DINT") for i in range(50)] if content else []
    arm = {"extra_programs_xml": R._program(R.MAIN, tags, [("MainRoutine", rungs)]),
           "extra_tasks_xml": R._task([R.MAIN]), "tags_xml": "\n".join(ctl)}
    l5x = build_l5x(name, processor_type=processor, major_rev=major, software_revision=software,
                    safety_level="SIL2", **with_baseline(**arm))
    l5x = l5x.replace('ConfigureSafetyIOAlways="true"', 'ConfigureSafetyIOAlways="false"', 1)
    if processor.startswith("5069"):
        # A 5069 has no Local port 2; its Ethernet modules hang off port 4.
        l5x = l5x.replace('ParentModule="Local" ParentModPortId="2"', 'ParentModule="Local" ParentModPortId="4"')
    if int(major) < 33:
        # v32 exports carry neither attribute (gen_fw_catalog_matrix FIRMWARE_TABLE).
        l5x = l5x.replace(' AutoDiagsEnabled="true" WebServerEnabled="false"', "", 1)
    return l5x


# --- the roster --------------------------------------------------------------------------

def plan() -> list[tuple[str, str, dict]]:
    files: list[tuple[str, str, dict]] = []
    std = [f"StdMap{i:03d}" for i in range(200)]
    saf = [f"SafMap{i:03d}" for i in range(200)]
    map_tags = [tag_xml(n, "DINT") for n in std] + [R.ctl_tag(n, "DINT") for n in saf]
    files.append(("safe_map_0", "control for safe_map_*: 200 standard and 200 controller safety DINTs, unmapped",
                  {"kind": "safety", "controller_tags": map_tags, "map": []}))
    for n in (1, 10, 50, 200):
        files.append((f"safe_map_{n}", f"the same tags, {n} standard -> safety tag-mapping pair(s)",
                      {"kind": "safety", "controller_tags": map_tags, "map": list(zip(std[:n], saf[:n]))}))
    files.append(("safe_lock_trial", "safe_n00 with SafetyLocked=\"true\": a locked project, imported",
                  {"kind": "safety", "locked": True}))

    definition, storage = R3.safety_aoi()
    for n in (5, 60):
        width = 32 * -(-n // 32)
        insts = [f"SafeAoi_{i:03d}" for i in range(n)]
        tags = [R.prog_tag(t, R3.SAFE_AOI, udt_members=storage) for t in insts] + [
            R.prog_tag("AiIn", "BOOL", (width,)), R.prog_tag("AiOut", "BOOL", (width,))]
        calls = [f"{R3.SAFE_AOI}({t},AiIn[{i}],AiOut[{i}]);" for i, t in enumerate(insts)]
        files.append((f"safe_aoi_inst_prog{n}", f"round 3's safety AOI, {n} SafetyProgram instances and their I/O arrays",
                      {"kind": "safety", "aoi_defs_xml": definition, "programs": [R.main_program(tags)]}))
        files.append((f"safe_aoi_call_{n}", f"the same and {n} calls of the safety AOI",
                      {"kind": "safety", "aoi_defs_xml": definition, "programs": [R.main_program(tags, calls)]}))
    for k in (6, 12):
        xml, _ = safety_aoi(inputs=k // 2, outputs=k // 2)
        files.append((f"safe_aoi_p{k}_def", f"a safety AOI with {k // 2} BOOL inputs and {k // 2} outputs (+EnableIn/Out), "
                      "one rung, no instances", {"kind": "safety", "aoi_defs_xml": xml}))
    xml, _ = safety_aoi(rungs=["XIC(InA)OTE(OutQ);"] + ["XIC(InA)NOP();"] * 9)
    files.append(("safe_aoi_r10_def", "round 3's safety AOI with 10 internal rungs and no locals",
                  {"kind": "safety", "aoi_defs_xml": xml}))
    xml, _ = safety_aoi(locals_=9)
    files.append(("safe_aoi_l9_def", "round 3's safety AOI with 9 local BOOLs and one rung",
                  {"kind": "safety", "aoi_defs_xml": xml}))

    for k in (16, 24, 40):
        name = "SubRtn" + "X" * (k - 8) + "01"
        files.append((f"safe_rtn_name{k}", f"one uncalled safety routine named with {k} characters",
                      {"kind": "safety", "programs": [R.main_program(subs=[(name, [])])]}))

    for name, tpl in (("atan2", "ATAN2(LgRa[{i}],LgRb[{i}],LgRc[{i}]);"), ("cop", "COP(LgDa[{i}],LgDb[{i}],1);"),
                      ("fll", "FLL(0,LgDb[{i}],1);")):
        # The pool's REAL arrays hold 64: ATAN2's indices wrap (a REAL written twice; only
        # output bits are held to one write).
        rungs = [tpl.format(i=i % 64 if name == "atan2" else i) for i in range(100)]
        files.append((f"safe_lg_{name}_100", f"100 safety-routine rungs of {name.upper()} on the safe_lg_ctl pool",
                      {"kind": "safety", "programs": [R.main_program(R3._pool(), rungs)]}))

    sref2 = [R.ctl_tag(f"SRefSD{i:03d}", "DINT") for i in range(50)] + [tag_xml("StdD", "DINT", dimensions=(64,))]
    files.append(("safe_sref2_ctl", "control for safe_sref2_mov_50: 50 scalar controller safety DINTs, a standard DINT[64]",
                  {"kind": "safety", "controller_tags": sref2}))
    files.append(("safe_sref2_mov_50", "50 standard MainRoutine rungs MOV(scalar safety DINT, standard DINT element)",
                  {"kind": "safety", "controller_tags": sref2,
                   "standard_rungs": [f"MOV(SRefSD{i:03d},StdD[{i}]);" for i in range(50)]}))

    for size, (udt, members) in (("s", R.UDT_S), ("l", R.UDT_L)):
        files.append((f"safetwin_udt_{size}_def", f"1756-L81E twin of safe_udt_{size}_def: the {udt} definition alone",
                      {"kind": "twin", "datatypes_xml": udt_xml(udt, members)}))
    twin_ref = [tag_xml(n, t, dimensions=d) for n, t, d in (("SRefA", "BOOL", (64,)), ("SRefB", "BOOL", (64,)),
                                                          ("SRefD", "DINT", (64,)))]
    twin_ref += [tag_xml(f"SRefS{i:03d}", "BOOL") for i in range(50)]
    twin_ref += [tag_xml("StdIn", "BOOL", dimensions=(64,)), tag_xml("StdOut", "BOOL", dimensions=(64,)),
                 tag_xml("StdD", "DINT", dimensions=(64,))]
    files.append(("safetwin_sref_ctl", "1756-L81E twin of safe_sref_ctl: the same tags, all standard",
                  {"kind": "twin", "controller_tags": twin_ref}))

    for stem, processor, major, software in BASE_PLATFORMS:
        for content in (False, True):
            sid = f"safe_base_{stem}" + ("_content" if content else "")
            what = "50 controller safety DINTs and 10 RIN rungs on " if content else "the safety File > New shell on "
            files.append((sid, f"{what}{processor} v{major}, on the plant",
                          {"kind": "base", "processor": processor, "major": major, "software": software,
                           "content": content}))
    return [(sid, f"{OQ}: {desc}", kw) for sid, desc, kw in files]


def _name(sample_id: str, prefix: str) -> str:
    return prefix + "".join(w.capitalize() for w in sample_id.split("_")[2:])


def make(sample_id: str, kw: dict) -> str:
    kw = dict(kw)
    kind = kw.pop("kind")
    if kind == "twin":
        return build_twin(_name(sample_id, "Twin"), **kw)
    if kind == "base":
        return build_base(_name(sample_id, "SafeBase"), kw["processor"], kw["major"], kw["software"], kw["content"])
    pairs, locked = kw.pop("map", []), kw.pop("locked", False)
    l5x = R.build(sample_id, **kw)
    l5x = with_tag_map(l5x, pairs)
    if locked:
        l5x = l5x.replace('SafetyLocked="false"', 'SafetyLocked="true"', 1)
    return l5x


def _make(job: tuple[str, dict]) -> int:
    sample_id, kw = job
    return write_sample(make(sample_id, kw), G.OUT_ROOT / f"{sample_id}.L5X")


def main() -> None:
    from sample_gen.progress import run
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX", help="build only the sample_ids this matches")
    args = ap.parse_args()
    jobs = [(sid, desc, kw) for sid, desc, kw in plan() if not args.only or re.search(args.only, sid)]
    predicted = run(((sid, (sid, kw)) for sid, _, kw in jobs), _make, label="round4")
    for sample_id, description, _ in jobs:
        append_manifest_row(sample_id, description, G.CATEGORY, G.OUT_ROOT / f"{sample_id}.L5X", predicted[sample_id])


if __name__ == "__main__":
    main()
