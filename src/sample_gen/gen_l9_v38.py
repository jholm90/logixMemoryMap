"""ControlLogix 5590 (L9) and firmware v38, side by side with the 1756-L81E.

An L9 cannot run v35, so an L9 file differs from every existing capture in
platform AND firmware at once. This batch separates the two by building every
content item three times, byte-identical apart from what the arm changes:

    arm      processor      firmware   rung spelling
    l8v35    1756-L81E      v35.05     v35 (GEQ, GRT, ...)   the control
    l8v38    1756-L81E      v38.02     v36+ (GE, GT, ...)    firmware only
    l9v38    1756-L908TS    v38.02     v36+ (GE, GT, ...)    platform only, vs l8v38

  l8v38 - l8v35   = what the firmware move costs at that content
  l9v38 - l8v38   = what the L9 costs at the same firmware

Content items (FUTURE_TESTS.md, "L9 (ControlLogix 5590): what it takes"):

  stage 1-2  density d0000..d1600   mixed content at five densities, as
             OQ-REAL5069 did for 5069: flat across density means a
             project-level constant, growing means a rate.
  stage 3    i_<mnemonic>           1,000 rungs of one instruction, for the
             21 most-used real instructions (the top 20 plus LEQ, so all six
             renamed comparisons are present).
  stage 4    m_<item>               Kinetix bus + drive + two axes, PowerFlex
             525, generic Ethernet, a sixth POINT I/O rack, 1756 local I/O in
             the chassis, 200 tag-based alarm conditions.

Plus six SPELLING DISCRIMINATORS (OQ-V36MNEMONIC): each comparison file of
stage 3 on L81E v38 with the v35 spelling left in. If Studio v38 rejects the
v35 spelling, the import error names it; if it accepts it, the reading must
equal the v36-spelled l8v38 twin, and the re-export shows which spelling
Studio writes.

Every file is on the realism floor (sample_gen.realism.with_baseline): the
baseline's own GRT/EQU/LES rungs are respelled with the content on v38 arms.
The L9 catalog is 1756-L908TS; content cost is not expected to depend on the
catalog within the family, and the budget question is OQ-L9BUDGET.

PLATFORM LINT EXEMPTION. Sweeping processor and firmware is the variable under
test, the reason the firmware/catalog matrices carry. Target names start
"PlatNine", listed in lint._PLATFORM_EXEMPT_NAME_PREFIXES. The l8v35 arm is
the standard and anchors the batch to the rest of the corpus.

Run: python -m sample_gen.gen_l9_v38
"""

from __future__ import annotations

import re
from pathlib import Path

from sample_gen.builders import MemberSpec, rung_xml, string_array_tag_xml, tag_xml, udt_xml
from sample_gen.gen_alarm_conditions import _ASSOC_ORDER, _condition_xml
from sample_gen.gen_module_motion import (
    _MOTION_GROUP_TAG_XML, _axis_tag, _drive_module_xml, bus_supply_with_converter,
)
from sample_gen.lint import to_v36_spelling
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import rack_xml, with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "l9v38"
CATEGORY = "l9v38"
TARGET_PREFIX = "PlatNine"
_MODULES = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

L9_CATALOG = "1756-L908TS"
# (arm, processor, MajorRev, SoftwareRevision, v36+ spelling)
ARMS = (
    ("l8v35", "1756-L81E", "35", "35.05", False),
    ("l8v38", "1756-L81E", "38", "38.02", True),
    ("l9v38", L9_CATALOG, "38", "38.02", True),
)

DENSITIES = (0, 25, 100, 400, 1600)
RUNGS = 1000
_BITS = 1024  # BOOL arrays are sized in whole DINTs

_DENS_UDT = "PnUnit"
_DENS_MEMBERS = [MemberSpec(f"Mbr{i:02d}", "DINT") for i in range(8)] + [MemberSpec("Done", "BOOL")]

# Stage 3: the 20 most-used real instructions (share of all real instruction
# occurrences across samples/local, measured when this batch was specified)
# plus LEQ. Each rung writes its own output, so the realism floor holds.
_CMP = "{m}(PnSrc[{i}],{i})OTE(PnOut[{i}]);"
INSTRUCTIONS: dict[str, str] = {
    "XIC": "XIC(PnBit[{i}])OTE(PnOut[{i}]);",
    "OTE": "OTE(PnOut[{i}]);",
    "MOV": "MOV(PnSrc[{i}],PnDst[{i}]);",
    "XIO": "XIO(PnBit[{i}])OTE(PnOut[{i}]);",
    "EQU": _CMP.replace("{m}", "EQU"),
    "OTU": "OTU(PnOut[{i}]);",
    "CLR": "CLR(PnDst[{i}]);",
    "OTL": "OTL(PnOut[{i}]);",
    "ADD": "ADD(PnSrc[{i}],1,PnDst[{i}]);",
    "ONS": "XIC(PnBit[{i}])ONS(PnOns[{i}])OTE(PnOut[{i}]);",
    "NEQ": _CMP.replace("{m}", "NEQ"),
    "TON": "XIC(PnBit[{i}])TON(PnTmr[{i}],?,?);",
    "GRT": _CMP.replace("{m}", "GRT"),
    "COP": "COP(PnSrc[{i}],PnDst[{i}],1);",
    "NOP": "NOP();",
    "LES": _CMP.replace("{m}", "LES"),
    "SUB": "SUB(PnSrc[{i}],1,PnDst[{i}]);",
    "JSR": "JSR(PnSub,0);",
    "GEQ": _CMP.replace("{m}", "GEQ"),
    "LIM": "LIM(0,PnSrc[{i}],100)OTE(PnOut[{i}]);",
    "LEQ": _CMP.replace("{m}", "LEQ"),
}
RENAMED = ("EQU", "NEQ", "GRT", "LES", "GEQ", "LEQ")

_ARRAY_TAGS = {
    "PnBit": lambda: tag_xml("PnBit", "BOOL", (_BITS,)),
    "PnOut": lambda: tag_xml("PnOut", "BOOL", (_BITS,)),
    "PnOns": lambda: tag_xml("PnOns", "BOOL", (_BITS,)),
    "PnSrc": lambda: tag_xml("PnSrc", "DINT", (RUNGS,)),
    "PnDst": lambda: tag_xml("PnDst", "DINT", (RUNGS,)),
    "PnTmr": lambda: tag_xml("PnTmr", "TIMER", (RUNGS,)),
}

ALARMS = 200
_ALARM_SIZE = 640


def _content_density(n: int) -> dict[str, str]:
    """n units: one PnUnit tag, one DINT tag and one rung writing that unit's
    own Done bit."""
    if not n:
        return {"tags_xml": "", "extra_rungs_xml": rung_xml(0, "NOP();")}
    tags = [tag_xml("PnGo", "BOOL")]
    tags += [tag_xml(f"PnUdt{i:04d}", _DENS_UDT, udt_members=_DENS_MEMBERS) for i in range(n)]
    tags += [tag_xml(f"PnDint{i:04d}", "DINT") for i in range(n)]
    rungs = [rung_xml(i, f"XIC(PnGo)MOV(PnDint{i:04d},PnUdt{i:04d}.Mbr00)OTE(PnUdt{i:04d}.Done);")
             for i in range(n)]
    return {"tags_xml": "\n".join(tags), "extra_datatypes_xml": udt_xml(_DENS_UDT, _DENS_MEMBERS),
            "extra_rungs_xml": "\n".join(rungs)}


def _content_instruction(mnemonic: str) -> dict[str, str]:
    template = INSTRUCTIONS[mnemonic]
    used = [name for name in _ARRAY_TAGS if name in template]
    kw = {
        "tags_xml": "\n".join(_ARRAY_TAGS[name]() for name in used),
        "extra_rungs_xml": "\n".join(rung_xml(i, template.format(i=i)) for i in range(RUNGS)),
    }
    if mnemonic == "JSR":
        kw["extra_routines_xml"] = (
            '<Routine Name="PnSub" Type="RLL">\n<RLLContent>\n'
            + rung_xml(0, "NOP();") + "\n</RLLContent>\n</Routine>")
    return kw


def _proven_module(sample: str, name: str, *, address: str | None = None,
                   slot: int | None = None) -> str:
    """The one non-controller Module of a zero-error capture, renamed and
    re-addressed (IP for a network module, slot for a chassis card)."""
    text = (_MODULES / f"{sample}.L5X").read_text(encoding="utf-8-sig")
    block = [m for m in re.findall(r"<Module\b.*?</Module>", text, re.S) if 'Name="Local"' not in m]
    assert len(block) == 1, f"{sample}: expected one module, found {len(block)}"
    block = re.sub(r'Name="[^"]+"', f'Name="{name}"', block[0], count=1)
    if address is not None:
        block = re.sub(r'Address="\d+\.\d+\.\d+\.\d+"', f'Address="{address}"', block, count=1)
    if slot is not None:
        block = re.sub(r'(<Port Id="1" Address=")\d+(" Type="ICP" Upstream="true")',
                       rf"\g<1>{slot}\g<2>", block, count=1)
    return block


def _alarm_host(conditions: list[str]) -> str:
    base = tag_xml("PnAlarm", "BOOL", (_ALARM_SIZE,))
    block = "<AlarmConditions>\n" + "\n".join(conditions) + "\n</AlarmConditions>\n"
    marker = '\n        <Data Format="Decorated">'
    assert marker in base, "tag_xml shape changed -- alarm splice point is gone"
    return base.replace(marker, "\n" + block + marker, 1)


def _content_module(item: str) -> dict[str, str]:
    if item == "kinetix":
        supply, converter = bus_supply_with_converter(
            name="PnBusSupply", address="192.168.1.10", axis_name="PnBusAxis")
        drive = _drive_module_xml("PnDrive1", "2198-D032-ERS3", "false", address="192.168.1.20")
        tags = [_MOTION_GROUP_TAG_XML, converter,
                _axis_tag("PnAxisX", "PnDrive1:Ch1"), _axis_tag("PnAxisY", "PnDrive1:Ch3")]
        return {"tags_xml": "\n".join(tags), "extra_modules_xml": "\n".join([supply, drive])}
    if item == "pf525":
        return {"extra_modules_xml": _proven_module(
            "modulevfd_powerflex525", "PnVfd", address="192.168.1.40")}
    if item == "geneth":
        return {"extra_modules_xml": _proven_module(
            "module_genericeth_in0008_out0008", "PnGateway", address="192.168.1.50")}
    if item == "pointio":
        return {"extra_modules_xml": rack_xml("RACK_6", "192.168.1.106")}
    if item == "local1756":
        # Slots 1 and 2: the L9 chassis on file is Bus Size 4.
        return {"extra_modules_xml": "\n".join([
            _proven_module("modulesweep_1756_ib16", "PnSlot1_IB16", slot=1),
            _proven_module("modulesweep_1756_ob16e_variant_1conn", "PnSlot2_OB16E", slot=2),
        ])}
    if item == "alarms":
        conds = [_condition_xml(f"PnAlarm{i:03d}", i, assoc=_ASSOC_ORDER[:3], hmi_group="LineA")
                 for i in range(ALARMS)]
        tags = [_alarm_host(conds),
                tag_xml("AlarmNumberArray", "DINT", (_ALARM_SIZE,)),
                string_array_tag_xml("AlarmDescArray", _ALARM_SIZE),
                string_array_tag_xml("AlarmMoreInfoArray", _ALARM_SIZE)]
        return {"tags_xml": "\n".join(tags)}
    raise KeyError(item)


MODULE_ITEMS = {
    "kinetix": "a 2198-P208 bus supply with its converter axis, one 2198-D032-ERS3 and two "
               "AXIS_CIP_DRIVE axes in a motion group -- every block proven at zero errors",
    "pf525": "one PowerFlex 525 (modulevfd_powerflex525, zero-error capture)",
    "geneth": "one generic Ethernet module, 8 in / 8 out SINT (module_genericeth_in0008_out0008)",
    "pointio": "a sixth POINT I/O rack, RACK_6, the baseline's own rack shape",
    "local1756": "1756-IB16 in slot 1 and 1756-OB16E in slot 2 of the controller's own chassis",
    "alarms": f"{ALARMS} tag-based alarm conditions in the real production shape (TRIP, three "
              f"associated tags, HMI group) on a BOOL[{_ALARM_SIZE}] host",
}


def build(content: dict[str, str], target: str, processor: str, major: str, software: str,
          v36_spelling: bool) -> str:
    l5x = build_l5x(target_name=target, processor_type=processor, major_rev=major,
                    software_revision=software, **with_baseline(**content))
    return to_v36_spelling(l5x) if v36_spelling else l5x


def _target(arm: str, stem: str) -> str:
    return f"{TARGET_PREFIX}_{arm}_{stem}"


def _emit(stem: str, content: dict[str, str], what: str, question: str) -> int:
    n = 0
    for arm, processor, major, software, v36 in ARMS:
        sample_id = f"l9v38_{stem.lower()}_{arm}"
        out = OUT_ROOT / f"{sample_id}.L5X"
        l5x = build(content, _target(arm, stem), processor, major, software, v36)
        predicted = write_sample(l5x, out)
        spelling = "v36+ comparison spelling (GE/GT/LE/LT/EQ/NE)" if v36 else "v35 spelling"
        append_manifest_row(
            sample_id,
            f"{processor} at v{software}, {spelling}, on the realism baseline, carrying {what}. "
            f"Byte-identical content to the l8v35/l8v38/l9v38 siblings of l9v38_{stem.lower()}: "
            f"l8v38 - l8v35 is the firmware move, l9v38 - l8v38 is the L9 at matched firmware. "
            f"{question}",
            CATEGORY, out, predicted)
        n += 1
    return n


def main() -> None:
    written = 0
    for d in DENSITIES:
        written += _emit(
            f"d{d:04d}", _content_density(d),
            f"{d} density unit(s) (one {_DENS_UDT} tag, one DINT tag, one rung each)",
            "OQ-L9PLATFORM stages 1-2: flat across density = a constant, growing = a rate.")
    for m in INSTRUCTIONS:
        written += _emit(
            f"i_{m}", _content_instruction(m),
            f"{RUNGS} rungs of {m} ({INSTRUCTIONS[m].format(i='n')})",
            "OQ-L9PLATFORM stage 3: any per-instruction cost that moved with firmware or platform."
            + (" OQ-V36MNEMONIC: renamed at v36." if m in RENAMED else ""))
    for item, what in MODULE_ITEMS.items():
        written += _emit(f"m_{item}", _content_module(item), what,
                         "OQ-L9PLATFORM stage 4: module, axis and alarm costs at v38 and on L9.")
    # Spelling discriminators: L81E v38, v35 spelling kept.
    for m in RENAMED:
        sample_id = f"l9v38_spell_{m.lower()}_l8v38_v35spelling"
        out = OUT_ROOT / f"{sample_id}.L5X"
        l5x = build(_content_instruction(m), _target("l8v38", f"spell_{m}"), "1756-L81E",
                    "38", "38.02", v36_spelling=False)
        predicted = write_sample(l5x, out)
        append_manifest_row(
            sample_id,
            f"1756-L81E at v38.02 with the v35 spelling {m} left in, on the realism baseline, "
            f"{RUNGS} rungs of {m}. Twin of l9v38_i_{m.lower()}_l8v38, which is identical but "
            f"spelled the v36+ way. OQ-V36MNEMONIC: an import error here says v38 does not accept "
            f"the v35 spelling; a clean import reading the same as the twin says it is an alias "
            f"of the same instruction, and the re-export shows which spelling Studio writes.",
            CATEGORY, out, predicted)
        written += 1
    print(f"Done. {written} files in {OUT_ROOT}.")


if __name__ == "__main__":
    main()
