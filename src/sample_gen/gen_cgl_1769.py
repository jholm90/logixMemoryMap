"""OQ-CGL1769: what the 1769 Compact GuardLogix programs (RS-11 to RS-16) cost, in both partitions.

In scope by the owner's decision of 2026-10-23, the one exception to 1769 being dead
architecture. On the engine of that morning the six read -5% to -12% standard and +28% to
+42% safety. The standard figure was mostly a missing baseline (a 1769 safety catalog had no
entry, so its empty project was priced at the L8x's), now provisionally wired from the
1769-L30ERM / L33ERM blank; the safety figure is unexplained, and the engine prices every
safety term at its 1756-L81ES v35 / 5069 value.

Two arms, the two catalogs at v32: 1769-L30ERMS and 1769-L33ERMS. The real programs run v30
(RS-11 to RS-13, RS-15) and v32 (RS-14, RS-16), and v32 is the floor -- the conversion tooling
cannot build a v30 project -- so each catalog also has a base alone at v35, the firmware step
on the safety catalog itself (and the 1769-L30ERM / L33ERM v35 blank the provisional baseline
came from). Each arm is the realism plant at 25%+ of its controller
(480 stations on the 1 MB L30ERMS, 960 on the 2 MB L33ERMS) with the safety task Studio's
File > New makes, and every other file in the arm is that base plus one step, differenced
against it. The L30ERMS density step (960 stations) carries the L33ERMS base's content, so
the catalogs difference directly.

  cgl_<arm>_base          the plant and the safety shell
  cgl_<arm>_plant2x       twice the plant's stations: the per-station rate on 1769
  cgl_<arm>_dint400       400 controller DINTs
  cgl_<arm>_udtdef20      20 unused UDT definitions of 14 mixed members
  cgl_<arm>_logic400      400 standard rungs (XIC XIO MOV OTE) on three arrays
  cgl_<arm>_progs10       10 standard programs, each a MainRoutine calling three routines
  cgl_<arm>_mods          a 1734 rack (4 IB8/C, 2 OB8E/C, IE2C/C), 3 1732E-IB16M12R/A,
                          a 1732E-OB16M12R/A and 2 EX260-SEN1/A: the real programs' module mix
  cgl_<arm>_safecontent   50 controller safety DINTs and 10 RIN rungs (round 4's step)
  cgl_<arm>_safertn8      8 safety routines called from the safety MainRoutine
  cgl_<arm>_saferung60    60 safety rungs: XIC XIO OTE, MOV, TON, ONS
  cgl_<arm>_safeinstr     4 DCS and 4 CROUT
  cgl_<arm>_sio_ib8s      a safety rack with 2 1734-IB8S/B, both connections
  cgl_<arm>_sio_ib8s1c    2 1734-IB8S/B, the SafetyInput connection only
  cgl_<arm>_sio_ob8s      1 1734-OB8S/A
  cgl_<arm>_sio_mix       one of each in one rack: additivity, the real programs' shape

and two 1756-L81ES v35 twins on the standard plant, against round 1's safe_n00, for the two
safety shapes no earlier round measured as such: safe_cgl_rung60 and safe_cgl_rtn8. The
Kinetix 5500 safety drive (RS-15) is built from its local template by
gen_safety_io --local, on l33v32 (safe_iol_cgl32_h008s_*).

Shape, from the real exports' structure (read only): Local ProductCode 176 / 177, Compact
bus Size 9 / 17, two Ethernet ports and the EthernetNetwork element; SafetyInfo at SIL3/PLe
and the controller's safety network number on its Ethernet port (the v32 exports); the
1734-AENTR/C at revision 6 below v35 (as round 4's v32 bases). Every name, address and safety network number is this project's.

Run: python -m sample_gen.gen_cgl_1769 [--only REGEX]
"""

from __future__ import annotations

import argparse
import re

from sample_gen import gen_safety_io as SIO
from sample_gen import gen_safety_partition as G
from sample_gen import gen_safety_round2 as R
from sample_gen.builders import MemberSpec, rung_xml, tag_xml, udt_xml
from sample_gen.gen_composite_realistic import _resize_slot_structure
from sample_gen.gen_fw_catalog_matrix import _1769_ETHERNET_XML
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OQ = "OQ-CGL1769"
OUT_ROOT = G.OUT_ROOT.parent / "cgl"
# (arm, ProcessorType, MajorRev, MinorRev, SoftwareRevision, plant stations). v32 is the floor:
# the conversion tooling cannot build a v30 project, so the four real programs at v30 are
# reached from v32 and the firmware movement the v35 bases read.
ARMS = (("l30v32", "1769-L30ERMS", "32", "13", "32.04", 480),
        ("l33v32", "1769-L33ERMS", "32", "13", "32.04", 960),
        ("l30v35", "1769-L30ERMS", "35", "11", "35.05", 480),
        ("l33v35", "1769-L33ERMS", "35", "11", "35.05", 960))
ARM = {a[0]: a[1:] for a in ARMS}
# The v35 arms are the base alone: the firmware step on the safety catalogs themselves, and the
# 1769-L30ERM / L33ERM v35 blank the provisional baseline came from.
BASE_ONLY = {"l30v35", "l33v35"}
CONTROLLER_SNN = "16#0000_1004_0001_0001"
AENTR_C_MAJOR_BELOW_V35 = "6"


# --- the 1769 shape -----------------------------------------------------------------------

def cgl_shape(l5x: str, major: str) -> str:
    """build_l5x's 1769 project in the shape the real 1769 safety exports have."""
    if int(major) < 33:
        # v32 exports carry neither attribute (gen_fw_catalog_matrix FIRMWARE_TABLE).
        l5x = l5x.replace(' AutoDiagsEnabled="true" WebServerEnabled="false"', "", 1)
    l5x, n = re.subn(r"<SafetyInfo [^>]*/>", '<SafetyInfo SafetyLocked="false" SignatureRunModeProtect="false" '
                     'ConfigureSafetyIOAlways="false" SafetyLevel="SIL3/PLe"/>', l5x, count=1)
    assert n == 1
    local = re.search(r'<Module Name="Local".*?</Module>', l5x, re.S).group(0)
    shaped = re.sub(r' SafetyNetwork="[^"]*"', "", local)
    shaped = shaped.replace('<Port Id="2" Type="Ethernet" Upstream="false">',
                            f'<Port Id="2" Type="Ethernet" Upstream="false" SafetyNetwork="{CONTROLLER_SNN}">', 1)
    assert CONTROLLER_SNN in shaped
    l5x = l5x.replace(local, shaped, 1)
    l5x, n = re.subn(r"<EthernetPorts>.*?</EthernetPorts>\n", _1769_ETHERNET_XML, l5x, count=1, flags=re.S)
    assert n == 1
    if int(major) < 35:
        l5x = re.sub(r'(CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196") Major="7"',
                     rf'\1 Major="{AENTR_C_MAJOR_BELOW_V35}"', l5x)
    return l5x


def controller_name(sample_id: str) -> str:
    return "Cgl" + "".join(w.capitalize() for w in sample_id.split("_")[1:])


def build_arm(sample_id: str, arm: str, stations: int | None = None, controller_tags: list[str] = (),
              standard_rungs: list[str] = (), datatypes_xml: str = "", programs_xml: str = "",
              scheduled: list[str] = (), modules: list[str] = (), safety_tags: list[str] = (),
              safety_routines: list[tuple[str, list[str]]] | None = None) -> str:
    processor, major, minor, software, base_stations = ARM[arm]
    routines = safety_routines or [("MainRoutine", [])]
    arm_kw = {
        "tags_xml": "\n".join(controller_tags),
        "extra_programs_xml": "\n".join(p for p in (programs_xml, R._program(R.MAIN, list(safety_tags), routines)) if p),
        "extra_tasks_xml": R._task([R.MAIN]),
        "extra_rungs_xml": "\n".join(rung_xml(i, r) for i, r in enumerate(standard_rungs)),
        "extra_scheduled_programs_xml": "\n".join(f'<ScheduledProgram Name="{p}"/>' for p in scheduled),
        "extra_modules_xml": "\n".join(modules),
    }
    if datatypes_xml:
        arm_kw["extra_datatypes_xml"] = datatypes_xml
    l5x = build_l5x(controller_name(sample_id), processor_type=processor, major_rev=major, minor_rev=minor,
                    software_revision=software, safety_level="SIL3",
                    **with_baseline(stations=stations or base_stations, **arm_kw))
    return cgl_shape(l5x, major)


# --- the steps ------------------------------------------------------------------------------

def _block(catalog: str, which: str) -> str:
    """A proven module block: the catalog's own, from its module-sweep chain."""
    xml = _MODULE_CHAINS[catalog][0]
    blocks = re.findall(r"<Module\b.*?</Module>", xml, re.S)
    return next(b for b in blocks if f'CatalogNumber="{which}"' in b)


def _renamed(block: str, name: str, ip: str | None = None, parent: str | None = None, slot: int | None = None) -> str:
    head, rest = block.split(">", 1)
    head = re.sub(r'Name="[^"]+"', f'Name="{name}"', head, count=1)
    if parent is not None:
        head = re.sub(r'ParentModule="[^"]+"', f'ParentModule="{parent}"', head, count=1)
    if ip is not None:
        rest = re.sub(r'Address="\d+\.\d+\.\d+\.\d+"', f'Address="{ip}"', rest, count=1)
    if slot is not None:
        rest, n = re.subn(r'(<Port Id="1" Address=")\d+(" Type="PointIO" Upstream="true")', rf"\g<1>{slot}\g<2>",
                          rest, count=1)
        assert n == 1, name
    return head + ">" + rest


def module_mix() -> list[str]:
    cards = ["1734-IB8/C"] * 4 + ["1734-OB8E/C"] * 2 + ["1734-IE2C/C"]
    out = [SIO.adapter("CglRack", "192.168.1.150", len(cards))]
    out += [_renamed(_block(c, c), f"CglRack_S{slot}", parent="CglRack", slot=slot)
            for slot, c in enumerate(cards, start=1)]
    out += [_renamed(_block("1732E-IB16M12R/A", "1732E-IB16M12R/A"), f"CglArmIn{i}", ip=f"192.168.1.{150 + i}")
            for i in (1, 2, 3)]
    out.append(_renamed(_block("1732E-OB16M12R/A", "1732E-OB16M12R/A"), "CglArmOut1", ip="192.168.1.154"))
    out += [_renamed(_block("EX260-SEN1/A", "EX260-SEN1/A"), f"CglValve{i}", ip=f"192.168.1.{154 + i}") for i in (1, 2)]
    return out


UDT_MEMBERS = ([MemberSpec(f"Dw{k}", "DINT") for k in range(4)] + [MemberSpec(f"Rv{k}", "REAL") for k in range(2)]
               + [MemberSpec("Iw0", "INT"), MemberSpec("Sb0", "SINT")] + [MemberSpec(f"Bit{k}", "BOOL") for k in range(6)])


def logic400() -> tuple[list[str], list[str]]:
    tags = [tag_xml("CglIn", "BOOL", dimensions=(416,)), tag_xml("CglOut", "BOOL", dimensions=(416,)),
            tag_xml("CglVal", "DINT", dimensions=(400,))]
    return tags, [f"XIC(CglIn[{i}])XIO(CglIn[{i + 1}])MOV({i},CglVal[{i}])OTE(CglOut[{i}]);" for i in range(400)]


def programs10() -> tuple[str, list[str]]:
    names = [f"CglPrg{i:02d}" for i in range(1, 11)]
    progs = []
    for p in names:
        routines = [("MainRoutine", [f"JSR(Sub{k},0);" for k in (1, 2, 3)])] + [(f"Sub{k}", ["NOP();"]) for k in (1, 2, 3)]
        body = "\n".join(R._routine(n, r) for n, r in routines)
        progs.append(f'<Program Name="{p}" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" '
                     f'UseAsFolder="false">\n<Tags>\n</Tags>\n<Routines>\n{body}\n</Routines>\n</Program>')
    return "\n".join(progs), names


def safe_rung60() -> tuple[list[str], list[str]]:
    tags = [R.prog_tag("SfIn", "BOOL", (64,)), R.prog_tag("SfOut", "BOOL", (64,)), R.prog_tag("SfVal", "DINT", (16,)),
            R.prog_tag("SfTmr", "TIMER", (5,)), R.prog_tag("SfOns", "BOOL", (32,))]
    rungs = [f"XIC(SfIn[{i}])XIO(SfIn[{i + 1}])OTE(SfOut[{i}]);" for i in range(40)]
    rungs += [f"XIC(SfIn[{i}])MOV({i},SfVal[{i}]);" for i in range(10)]
    rungs += [f"XIC(SfIn[{40 + j}])TON(SfTmr[{j}],?,?);" for j in range(5)]
    rungs += [f"XIC(SfIn[{50 + j}])ONS(SfOns[{j}])OTE(SfOut[{40 + j}]);" for j in range(5)]
    return tags, rungs


def safe_rtn8() -> list[tuple[str, list[str]]]:
    return [("MainRoutine", [f"JSR(SfRtn{k},0);" for k in range(1, 9)])] + [(f"SfRtn{k}", ["NOP();"]) for k in range(1, 9)]


def safe_instr() -> tuple[list[str], list[str]]:
    tags, rungs = [], []
    for mn in ("DCS", "CROUT"):
        t, r = G.instruction_pair(mn, 4)
        tags += t
        rungs += r
    return tags, rungs


STEPS = {
    "base": ("the plant and the safety shell", {}),
    "plant2x": ("twice the plant's stations", {"stations": 2}),
    "dint400": ("400 controller DINTs (12-character names)",
                {"controller_tags": [tag_xml(f"CglDint{i:05d}", "DINT") for i in range(400)]}),
    "udtdef20": ("20 unused UDT definitions of 14 members (4 DINT, 2 REAL, INT, SINT, 6 BOOL)",
                 {"datatypes_xml": "\n".join(udt_xml(f"CglUdt{k:02d}", UDT_MEMBERS) for k in range(1, 21))}),
    "logic400": ("400 standard rungs XIC XIO MOV OTE on three controller arrays", {"logic": True}),
    "progs10": ("10 standard programs, each a MainRoutine calling three one-rung routines", {"programs": True}),
    "mods": ("a 1734-AENTR/C rack (4 IB8/C, 2 OB8E/C, IE2C/C), 3 1732E-IB16M12R/A, a 1732E-OB16M12R/A and 2 "
             "EX260-SEN1/A on the Ethernet port", {"mods": True}),
    "safecontent": ("50 controller safety DINTs and 10 RIN rungs (round 4's content step)", {"safecontent": True}),
    "safertn8": ("8 one-rung safety routines called from the safety MainRoutine", {"safety_routines": safe_rtn8()}),
    "saferung60": ("60 safety rungs (40 XIC XIO OTE, 10 MOV, 5 TON, 5 ONS) on safety-program tags", {"rung60": True}),
    "safeinstr": ("4 DCS and 4 CROUT on their own safety-program tags", {"instr": True}),
    "sio_ib8s": ("a safety rack (1734-AENTR/C) with 2 1734-IB8S/B, both connections", {"sio": ["ib8s", "ib8s"]}),
    "sio_ib8s1c": ("the safety rack with 2 1734-IB8S/B, SafetyInput connection only", {"sio": ["ib8s1c", "ib8s1c"]}),
    "sio_ob8s": ("the safety rack with 1 1734-OB8S/A", {"sio": ["ob8sa"]}),
    "sio_mix": ("the safety rack with one 1734-IB8S/B (both connections), one (input only) and one 1734-OB8S/A",
                {"sio": ["ib8s", "ib8s1c", "ob8sa"]}),
}


def make(sample_id: str, kw: dict) -> str:
    if kw.get("twin"):
        if kw["twin"] == "rung60":
            tags, rungs = safe_rung60()
            return R.build(sample_id, programs=[R.main_program(tags, rungs)])
        return R.build(sample_id, programs=[(R.MAIN, [], safe_rtn8())])
    arm, step = kw["arm"], kw["step"]
    opts = dict(STEPS[step][1])
    args: dict = {}
    if "stations" in opts:
        args["stations"] = ARM[arm][4] * opts["stations"]
    for key in ("controller_tags", "datatypes_xml", "safety_routines"):
        if key in opts:
            args[key] = opts[key]
    if opts.get("logic"):
        args["controller_tags"], args["standard_rungs"] = logic400()
    if opts.get("programs"):
        args["programs_xml"], args["scheduled"] = programs10()
    if opts.get("mods"):
        args["modules"] = module_mix()
    if opts.get("safecontent"):
        tags, rungs = G.instruction_pair("RIN", 10)
        args["controller_tags"] = [R.ctl_tag(f"SafeDint{i:04d}", "DINT") for i in range(50)]
        args["safety_tags"], args["safety_routines"] = tags, [("MainRoutine", rungs)]
    if opts.get("rung60"):
        tags, rungs = safe_rung60()
        args["safety_tags"], args["safety_routines"] = tags, [("MainRoutine", rungs)]
    if opts.get("instr"):
        tags, rungs = safe_instr()
        args["safety_tags"], args["safety_routines"] = tags, [("MainRoutine", rungs)]
    if "sio" in opts:
        args["modules"] = SIO.rack("SRACK_1", "192.168.1.200", SIO.RACK_SNN[0], opts["sio"])
    return build_arm(sample_id, arm, **args)


def plan() -> list[tuple[str, str, dict]]:
    files = []
    for arm, processor, major, _minor, _sw, stations in ARMS:
        for step, (what, _opts) in STEPS.items():
            if arm in BASE_ONLY and step != "base":
                continue
            against = "" if step == "base" else f", against cgl_{arm}_base"
            files.append((f"cgl_{arm}_{step}", f"{processor} v{major}, the realism plant at {stations} stations with the "
                          f"safety shell: {what}{against}", {"arm": arm, "step": step}))
    files.append(("safe_cgl_rung60", "1756-L81ES v35 twin of cgl_*_saferung60: the same 60 safety rungs on the "
                  "standard plant, against safe_n00", {"twin": "rung60"}))
    files.append(("safe_cgl_rtn8", "1756-L81ES v35 twin of cgl_*_safertn8: the same 8 safety routines, against "
                  "safe_n00", {"twin": "rtn8"}))
    return [(sid, f"{OQ}: {desc}", kw) for sid, desc, kw in files]


def _make(job: tuple[str, dict]) -> int:
    sample_id, kw = job
    return write_sample(make(sample_id, kw), OUT_ROOT / f"{sample_id}.L5X")


def main(argv: list[str] | None = None) -> None:
    from sample_gen.progress import run
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX", help="build only the sample_ids this matches")
    args = ap.parse_args([] if argv is None else argv)
    jobs = [(sid, desc, kw) for sid, desc, kw in plan() if not args.only or re.search(args.only, sid)]
    predicted = run(((sid, (sid, kw)) for sid, _, kw in jobs), _make, label="cgl-1769")
    for sample_id, description, _ in jobs:
        append_manifest_row(sample_id, description, G.CATEGORY, OUT_ROOT / f"{sample_id}.L5X", predicted[sample_id])
        print(f"{sample_id}: predicted {predicted[sample_id]:,}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
