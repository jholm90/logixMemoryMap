"""The realism floor every generated file is built on.

The generated corpus that the instruction weights were fitted on differs from
real programs in three gross ways, none of them measured:

  * **No I/O.** Every standard real program has at least 5 Ethernet I/O nodes;
    almost every generated file has none.
  * **Nearly empty controller.** Real programs fill 16-94% of the controller;
    a calibration file is typically under 5%, so every operand a rung
    references sits within a few hundred bytes of the start of the data table.
  * **Duplicated output bits.** The instruction sweeps write the same ten BOOLs
    thousands of times over (`gen_logic_sweep._b(i)` is `B{i % 10}`). Real
    ladder writes each output bit in one place.

So every file generated from here on carries this baseline, and
`sample_gen.lint.realism_findings` refuses a file that does not meet it:

  * >= 5 Ethernet I/O nodes -- five POINT I/O racks, RACK_1..RACK_5, each a
    1734-AENTR/C adapter with four 1734-IB8/C and four 1734-OB8/C in slots 1-8
    (Bus Size 9, rack-optimized, the shape of real POINT I/O);
  * >= 25% of the controller's capacity predicted (786,432 bytes on the
    1756-L81E standard);
  * no bit written by more than one OTE (or ONS storage bit), and no OTL/OTU
    target that is also OTE'd.

The fill is a PLANT: `STATIONS` stations, each one UDT instance, one TIMER and
ten rungs of ordinary machine ladder -- a seal-in branch, a timer and its done
bit, a counter with a one-shot, a latch and its unlatch, a compare -- against
its own members only, so every output bit is written exactly once. Stations sit
ten to a routine, the routines are called by JSR from each line program's
MainRoutine, and the lines are scheduled in MainTask. Every instruction in it
has an isolation-confirmed weight (instruction_accuracy in memory_model.yaml).

The module blocks are the proven clean captures `modulesweep_1734_ib8_c` and
`modulesweep_1734_ob8_c` (adapter and card verbatim), with the adapter resized
to Bus Size 9 the way `pioconn_optimized_n08` (clean, AB:1734_9SLOT) proves.

Rack-optimized card tags are addressed `RACK_n:slot:I.bit` / `RACK_n:slot:O.bit`
-- the most common POINT I/O operand form in the real set (1,108 input and 510
output uses).
"""

from __future__ import annotations

import re

from sample_gen.builders import MemberSpec, rung_xml, tag_xml, timer_tag_xml, udt_xml
from sample_gen.gen_composite_realistic import _resize_slot_structure
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.lint import MIN_FILL, MIN_IO_NODES, io_node_count, output_bit_duplicates  # noqa: F401  (re-exported)

RACKS = tuple(f"RACK_{n}" for n in range(1, 6))
RACK_SLOTS = 9  # the adapter plus eight cards
INPUT_SLOTS = (1, 2, 3, 4)  # 1734-IB8/C
OUTPUT_SLOTS = (5, 6, 7, 8)  # 1734-OB8/C
POINTS_PER_CARD = 8

LINES = 4
STATIONS_PER_ROUTINE = 10
# Sized so the baseline ALONE predicts over 25% of a 1756-L81E; an arm only
# adds to it. Pinned by tests/test_realism.py.
STATIONS = 1280

_STATION_UDT = "PlantStation"
_STATION_MEMBERS = (
    [MemberSpec(f"In{i}", "BOOL") for i in range(8)]
    + [MemberSpec(f"Out{i}", "BOOL") for i in range(6)]
    + [MemberSpec("Ons0", "BOOL")]
    + [MemberSpec("Cnt", "DINT"), MemberSpec("Sp", "DINT"),
       MemberSpec("Pv", "REAL"), MemberSpec("PvHi", "REAL")]
)


def _module_blocks(catalog: str) -> list[str]:
    xml, _source, _n = _MODULE_CHAINS[catalog]
    return re.findall(r"<Module\b.*?</Module>", xml, re.DOTALL)


_ADAPTER_BLOCK = _module_blocks("1734-IB8/C")[0]
_CARD_BLOCKS = {"IB8": _module_blocks("1734-IB8/C")[1], "OB8": _module_blocks("1734-OB8/C")[1]}
assert 'CatalogNumber="1734-AENTR/C"' in _ADAPTER_BLOCK


def rack_xml(name: str, ip: str) -> str:
    """One 9-slot POINT I/O rack: AENTR/C, IB8/C in slots 1-4, OB8/C in 5-8."""
    adapter = re.sub(r'Name="[^"]+"', f'Name="{name}"', _ADAPTER_BLOCK, count=1)
    adapter = re.sub(r'<Bus Size="\d+" ?/>', f'<Bus Size="{RACK_SLOTS}" />', adapter, count=1)
    adapter = re.sub(r'Address="192\.168\.[0-9.]+"', f'Address="{ip}"', adapter, count=1)
    adapter = _resize_slot_structure(adapter, RACK_SLOTS)
    parts = [adapter]
    for slot in range(1, RACK_SLOTS):
        card = _CARD_BLOCKS["IB8" if slot in INPUT_SLOTS else "OB8"]
        card = re.sub(r'ParentModule="[^"]+"', f'ParentModule="{name}"', card, count=1)
        card = re.sub(r'(<Port Id="1" Address=")\d+(" Type="PointIO" Upstream="true")',
                      rf"\g<1>{slot}\g<2>", card, count=1)
        parts.append(card)
    return "\n".join(parts)


def racks_xml() -> str:
    return "\n".join(rack_xml(name, f"192.168.1.{100 + n}") for n, name in enumerate(RACKS, start=1))


def input_points() -> list[str]:
    """Every POINT I/O input bit, as a rung operand: RACK_n:slot:I.bit."""
    return [f"{r}:{s}:I.{b}" for r in RACKS for s in INPUT_SLOTS for b in range(POINTS_PER_CARD)]


def output_points() -> list[str]:
    """Every POINT I/O output bit, as a rung operand: RACK_n:slot:O.bit."""
    return [f"{r}:{s}:O.{b}" for r in RACKS for s in OUTPUT_SLOTS for b in range(POINTS_PER_CARD)]


def _station_rungs(s: str) -> list[str]:
    t = f"{s}T"
    return [
        f"XIC({s}.In0)XIO({s}.In1)OTE({s}.Out0);",
        f"XIC({s}.In2)[XIC({s}.Out1),XIC({s}.In3)]XIO({s}.In4)OTE({s}.Out1);",
        f"XIC({s}.Out1)TON({t},?,?);",
        f"XIC({t}.DN)OTE({s}.Out2);",
        f"GRT({s}.Cnt,{s}.Sp)OTE({s}.Out3);",
        f"XIC({s}.In5)ONS({s}.Ons0)ADD({s}.Cnt,1,{s}.Cnt);",
        f"EQU({s}.Cnt,100)OTL({s}.Out4);",
        f"XIC({s}.In6)OTU({s}.Out4);",
        f"XIC({s}.In7)MOV(0,{s}.Cnt);",
        f"LES({s}.Pv,{s}.PvHi)OTE({s}.Out5);",
    ]


def _routine_xml(name: str, rungs: list[str]) -> str:
    body = "\n".join(rung_xml(i, text) for i, text in enumerate(rungs))
    return f'<Routine Name="{name}" Type="RLL">\n<RLLContent>\n{body}\n</RLLContent>\n</Routine>'


def plant(stations: int = STATIONS) -> dict[str, str]:
    """The fill: build_l5x keyword arguments to MERGE with an arm's own.

    Returns datatypes, controller tags, programs and scheduled-program XML.
    Station names are Stn0001..; nothing here is named like an arm's tags.
    """
    names = [f"Stn{i:04d}" for i in range(1, stations + 1)]
    tags = []
    for s in names:
        tags.append(tag_xml(s, _STATION_UDT, udt_members=_STATION_MEMBERS))
        tags.append(timer_tag_xml(f"{s}T"))
    per_line = -(-stations // LINES)
    programs, scheduled = [], []
    for line in range(LINES):
        line_names = names[line * per_line:(line + 1) * per_line]
        if not line_names:
            continue
        areas = [line_names[i:i + STATIONS_PER_ROUTINE]
                 for i in range(0, len(line_names), STATIONS_PER_ROUTINE)]
        routines = [_routine_xml("MainRoutine", [f"JSR(Area{a + 1:02d},0);" for a in range(len(areas))])]
        routines += [_routine_xml(f"Area{a + 1:02d}", [r for s in area for r in _station_rungs(s)])
                     for a, area in enumerate(areas)]
        prog = f"Line{line + 1}"
        programs.append(
            f'<Program Name="{prog}" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" '
            f'UseAsFolder="false">\n<Tags>\n</Tags>\n<Routines>\n' + "\n".join(routines)
            + "\n</Routines>\n</Program>")
        scheduled.append(f'<ScheduledProgram Name="{prog}"/>')
    return {
        "extra_datatypes_xml": udt_xml(_STATION_UDT, _STATION_MEMBERS),
        "tags_xml": "\n".join(tags),
        "extra_programs_xml": "\n".join(programs),
        "extra_scheduled_programs_xml": "\n".join(scheduled),
        "extra_modules_xml": racks_xml(),
    }


def with_baseline(stations: int = STATIONS, **arm) -> dict[str, str]:
    """build_l5x keyword arguments: the arm's own content plus the baseline.

    Every XML-fragment argument is concatenated (arm first), so an arm passes
    exactly what it would have passed to build_l5x without the baseline.
    """
    base = plant(stations)
    merged = dict(arm)
    for key, xml in base.items():
        merged[key] = "\n".join(p for p in (arm.get(key, ""), xml) if p)
    return merged
