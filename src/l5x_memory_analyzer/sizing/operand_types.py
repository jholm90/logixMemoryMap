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

# Members of the predefined structures real operands reach into. Only the
# members an arithmetic, compare or move instruction can take are needed.
_PREDEFINED_MEMBERS: dict[str, dict[str, str]] = {
    "TIMER": {"PRE": "DINT", "ACC": "DINT", "EN": "BOOL", "TT": "BOOL", "DN": "BOOL"},
    "COUNTER": {"PRE": "DINT", "ACC": "DINT", "CU": "BOOL", "CD": "BOOL", "DN": "BOOL",
                "OV": "BOOL", "UN": "BOOL"},
    "CONTROL": {"LEN": "DINT", "POS": "DINT", "EN": "BOOL", "EU": "BOOL", "DN": "BOOL",
                "EM": "BOOL", "ER": "BOOL", "UL": "BOOL", "IN": "BOOL", "FD": "BOOL"},
    "STRING": {"LEN": "DINT", "DATA": "SINT"},
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
        if not operand or _depth > _MAX_ALIAS_DEPTH or ":" in operand:
            return None
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
        self._controller = OperandTypes([controller_scope], members)
        self._programs: dict[str, OperandTypes] = {}
        if controller is not None:
            for program in controller.iter("Program"):
                self._programs[program.get("Name")] = OperandTypes(
                    [_tag_table(program), controller_scope], members)

    def for_program(self, program_name: str | None) -> OperandTypes:
        return self._programs.get(program_name or "", self._controller)

    def for_aoi(self, aoi_name: str) -> OperandTypes | None:
        return self._aoi.get(aoi_name)
