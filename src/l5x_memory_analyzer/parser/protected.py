"""Source-protected content: give it a MINIMUM price instead of zero.

A source-protected AOI exports as
`<EncodedData EncodedType="AddOnInstructionDefinition">`: its logic and local
tags are encrypted, but its <Parameters> -- the external interface -- stay in
clear text. A protected routine exports as
`<EncodedData EncodedType="Routine">` with nothing but its name and language.

Priced at zero, a protected AOI also zeroed every INSTANCE of it: an instance
tag's type did not resolve to any definition, so it fell out as an unknown
type. One real program carried 34 such tags, and a controller-scoped instance
is real data memory whatever the AOI hides.

`add_protected_aoi_standins` appends, for each protected AOI with no clear-text
definition, a stand-in AddOnInstructionDefinition carrying only its visible
Parameters. Everything downstream then prices it as it prices any AOI: the
definition from its interface, each instance from its parameter data, each
call site from its arguments. What stays unpriced -- the encrypted local tags
and internal logic -- is reported by coverage.audit_coverage as a MINIMUM.
"""

from __future__ import annotations

import copy
import xml.etree.ElementTree as ET

STANDIN_ATTR = "ProtectedStandIn"


def protected_aoi_elements(root: ET.Element) -> list[ET.Element]:
    return [el for el in root.iter("EncodedData")
            if el.get("EncodedType") == "AddOnInstructionDefinition"]


def protected_routine_elements(root: ET.Element) -> list[tuple[str, ET.Element]]:
    """(program name, EncodedData) for every protected program routine."""
    found = []
    for program_el in root.findall("Controller/Programs/Program"):
        routines_el = program_el.find("Routines")
        if routines_el is None:
            continue
        for el in routines_el.findall("EncodedData"):
            if el.get("EncodedType") == "Routine":
                found.append((program_el.get("Name") or "", el))
    return found


def add_protected_aoi_standins(root: ET.Element) -> int:
    """Append a clear-text stand-in definition for each protected AOI that has
    none. Idempotent: a second call adds nothing. Returns how many were added."""
    container = root.find("Controller/AddOnInstructionDefinitions")
    if container is None:
        return 0
    existing = {el.get("Name") for el in container.findall("AddOnInstructionDefinition")}
    added = 0
    for enc in protected_aoi_elements(root):
        name = enc.get("Name")
        if not name or name in existing:
            continue
        standin = ET.SubElement(container, "AddOnInstructionDefinition", {
            "Name": name,
            "Revision": enc.get("Revision", ""),
            STANDIN_ATTR: "true",
        })
        params = enc.find("Parameters")
        if params is not None:
            standin.append(copy.deepcopy(params))
        existing.add(name)
        added += 1
    return added
