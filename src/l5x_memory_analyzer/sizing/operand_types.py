"""Resolve a rung operand to its data type, the way the controller sees it.

The operand-type surcharge (memory_model.yaml operand_type_surcharge) was wired
against a flat table of BARE controller tag names, so every operand written as a
member path (`Stn.Pv`), an array element (`Arr[i].Cnt`), an alias, a program-scope
tag in its own program, or an AOI parameter inside the AOI's own logic resolved
to nothing and paid no surcharge. Half of all real operands are member paths, and
OQ-OPERANDSHAPE measured a member path costing exactly what a plain tag of the same
type costs, so the type -- not the spelling -- is what the surcharge follows.

Resolution walks the path: base tag (own scope first, then controller), through
aliases, then each `.Member` through UDT, AOI and predefined-structure member
tables. Array subscripts are dropped (an element has the array's type); a `.N`
bit subscript is BOOL. Anything that cannot be followed -- a module I/O tag, a
member of a structure whose layout the file does not declare -- is None, and pays
no surcharge, exactly as before.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

_AXIS_COMMON = {"ActualPosition": "REAL", "CommandPosition": "REAL", "ActualVelocity": "REAL",
                "CommandVelocity": "REAL", "AverageVelocity": "REAL",
                "InterpolatedActualPosition": "REAL", "AxisFault": "DINT", "AxisStatus": "DINT"}

# Members of the predefined structures real operands reach into. Only the
# members an arithmetic, compare or move instruction can take are needed.
_PREDEFINED_MEMBERS: dict[str, dict[str, str]] = {
    "TIMER": {"PRE": "DINT", "ACC": "DINT", "EN": "BOOL", "TT": "BOOL", "DN": "BOOL"},
    "COUNTER": {"PRE": "DINT", "ACC": "DINT", "CU": "BOOL", "CD": "BOOL", "DN": "BOOL",
                "OV": "BOOL", "UN": "BOOL"},
    "CONTROL": {"LEN": "DINT", "POS": "DINT", "EN": "BOOL", "EU": "BOOL", "DN": "BOOL",
                "EM": "BOOL", "ER": "BOOL", "UL": "BOOL", "IN": "BOOL", "FD": "BOOL"},
    "STRING": {"LEN": "DINT", "DATA": "SINT"},
    # Motion structures: the numeric attributes real ladder reads (types per the
    # instruction-set structure definitions). A status BOOL needs no entry here --
    # it is only ever an XIC/XIO operand, which carries no type surcharge.
    "MOTION_INSTRUCTION": {"FLAGS": "DINT", "ERR": "INT", "STATUS": "SINT", "STATE": "SINT",
                           "SEGMENT": "DINT", "EXERR": "SINT", "EN": "BOOL", "DN": "BOOL",
                           "ER": "BOOL", "PC": "BOOL", "IP": "BOOL", "AC": "BOOL"},
    "CAM": {"Master": "REAL", "Slave": "REAL", "SegmentType": "DINT"},
    "AXIS_CIP_DRIVE": {**_AXIS_COMMON, "CIPAxisState": "INT", "OutputCurrent": "REAL",
                       "MotorCapacity": "REAL", "PositionError": "REAL", "VelocityError": "REAL",
                       "Registration1Position": "REAL", "Registration1Time": "DINT",
                       "Registration2Time": "DINT", "OutputFrequency": "REAL",
                       "TorqueReferenceFiltered": "REAL", "CIPAxisIOStatus": "DINT"},
    "AXIS_VIRTUAL": dict(_AXIS_COMMON),
    "AXIS_SERVO": dict(_AXIS_COMMON),
    "AXIS_SERVO_DRIVE": dict(_AXIS_COMMON),
}

_SUBSCRIPT = re.compile(r"\[[^\]]*\]")
_NUMERIC_LITERAL = re.compile(r"^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$")
_MAX_ALIAS_DEPTH = 8


def _tag_table(container: ET.Element | None) -> tuple[dict[str, str], dict[str, str]]:
    types: dict[str, str] = {}
    aliases: dict[str, str] = {}
    tags = container.find("Tags") if container is not None else None
    if tags is None:
        return types, aliases
    for tag in tags.findall("Tag"):
        name = tag.get("Name")
        if not name:
            continue
        if tag.get("TagType") == "Alias" and tag.get("AliasFor"):
            aliases[name] = tag.get("AliasFor")
        elif tag.get("DataType"):
            types[name] = tag.get("DataType")
    return types, aliases


class OperandTypes:
    """Operand -> data type for one scope (a program, or an AOI definition)."""

    def __init__(self, scopes: list[tuple[dict[str, str], dict[str, str]]],
                 members: dict[str, dict[str, str]]) -> None:
        self._scopes = scopes
        self._members = members

    def resolve(self, operand: str, _depth: int = 0) -> str | None:
        operand = operand.strip()
        if not operand or _depth > _MAX_ALIAS_DEPTH:
            return None
        if ":" in operand:
            return self._resolve_module(operand)
        if _NUMERIC_LITERAL.match(operand):
            return None
        path = _SUBSCRIPT.sub("", operand).split(".")
        base, steps = path[0], path[1:]
        current = None
        for types, aliases in self._scopes:
            if base in types:
                current = types[base]
                break
            if base in aliases:
                target = aliases[base] + "".join("." + s for s in steps)
                return self.resolve(target, _depth + 1)
        for step in steps:
            if current is None:
                return None
            if step.isdigit():
                return "BOOL"
            current = self._members.get(current, {}).get(step)
        return "BOOL" if current == "BIT" else current

    def _resolve_module(self, operand: str) -> str | None:
        """A module I/O operand -- `Mod:I.Ch0Data`, `Local:3:I.Data[2]` -- typed from
        the member types the module's own connection tags declare in the file."""
        modules = getattr(self, "_modules", None)
        if not modules:
            return None
        head, _, rest = operand.partition(".")
        members = modules.get(_SUBSCRIPT.sub("", head))
        if members is None or not rest:
            return None
        steps = _SUBSCRIPT.sub("", rest).split(".")
        current = members.get(steps[0])
        for step in steps[1:]:
            if current is None:
                return None
            if step.isdigit():
                return "BOOL"
            current = self._members.get(current, {}).get(step)
        return "BOOL" if current == "BIT" else current


def _module_io_types(root: ET.Element) -> dict[str, dict[str, str]]:
    """`Mod:I` / `Parent:slot:I` (and :O, :C) -> {member: type}, read from each module's
    Decorated InputTag / OutputTag / ConfigTag structure."""
    table: dict[str, dict[str, str]] = {}
    for mod in root.iter("Module"):
        name = mod.get("Name")
        if not name:
            continue
        slot = None
        parent = mod.get("ParentModule")
        for port in mod.iter("Port"):
            if port.get("Upstream") == "true" and (port.get("Address") or "").isdigit():
                slot = port.get("Address")
        for tag_el, suffix in (("InputTag", "I"), ("OutputTag", "O"), ("ConfigTag", "C")):
            for t in mod.iter(tag_el):
                st = t.find("Data[@Format='Decorated']/Structure")
                if st is None:
                    continue
                members = {m.get("Name"): m.get("DataType") for m in st
                           if m.get("Name") and m.get("DataType")}
                if not members:
                    continue
                table.setdefault(f"{name}:{suffix}", {}).update(members)
                if parent and slot is not None:
                    table.setdefault(f"{parent}:{slot}:{suffix}", {}).update(members)
    return table


class FileOperandTypes:
    """Every scope in one file: one resolver per program and per AOI."""

    def __init__(self, root: ET.Element) -> None:
        controller = root.find("Controller") if root.tag != "Controller" else root
        members: dict[str, dict[str, str]] = {k: dict(v) for k, v in _PREDEFINED_MEMBERS.items()}
        for dt in root.iter("DataType"):
            members[dt.get("Name")] = {
                m.get("Name"): m.get("DataType") for m in dt.iter("Member")
                if m.get("Hidden") != "true"
            }
        self._aoi: dict[str, OperandTypes] = {}
        for aoi in root.iter("AddOnInstructionDefinition"):
            own = {p.get("Name"): p.get("DataType") for p in aoi.iter("Parameter")}
            own.update({t.get("Name"): t.get("DataType") for t in aoi.iter("LocalTag")})
            members[aoi.get("Name")] = own
        for aoi in root.iter("AddOnInstructionDefinition"):
            self._aoi[aoi.get("Name")] = OperandTypes([(members[aoi.get("Name")], {})], members)
        controller_scope = _tag_table(controller)
        modules = _module_io_types(root)
        self._controller = OperandTypes([controller_scope], members)
        self._controller._modules = modules
        self._programs: dict[str, OperandTypes] = {}
        if controller is not None:
            for program in controller.iter("Program"):
                self._programs[program.get("Name")] = OperandTypes(
                    [_tag_table(program), controller_scope], members)
                self._programs[program.get("Name")]._modules = modules

    def for_program(self, program_name: str | None) -> OperandTypes:
        return self._programs.get(program_name or "", self._controller)

    def for_aoi(self, aoi_name: str) -> OperandTypes | None:
        return self._aoi.get(aoi_name)
