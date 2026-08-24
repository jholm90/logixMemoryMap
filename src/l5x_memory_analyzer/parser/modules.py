"""Parses Controller/Modules out of an L5X document (2026-08-27, first pass
-- James's Phase 1 "Module/IO parsing is still open" gap, never started
before now).

Unlike every other sizing category in this project, module I/O/config data
size does NOT need to be empirically fitted from scratch: real corpus
inspection (samples/local/DnR_Personal/*.L5X, 2026-08-27) confirmed Logix
Designer's own L5X export states these sizes directly, as real attributes,
not something this project has to infer:
  - Each <Connection> under a Module's <Communications> carries its own
    `InputSize`/`OutputSize` attributes, in bytes (e.g. a 16-point digital
    input module's Standard connection: InputSize="4"; a safety module's
    SafetyInput connection: InputSize="52").
  - Each <ConfigTag> carries its own `ConfigSize` attribute, in bytes
    (e.g. ConfigSize="64" for a 16-channel digital input module).
A module can have multiple Connections (e.g. a safety module has both a
"Standard" and a "SafetyInput"/"SafetyOutput" connection) -- every
Connection found under a Module is summed, not just the first.

**What this does NOT yet establish (real open question, not modeled here):**
whether these L5X-stated byte counts map 1:1 to actual controller memory
Capacity-tab consumption, or whether (like literally every other category
in this project -- tag_overhead, alias_overhead, udt_definition, etc.) real
firmware adds its own per-module/per-connection overhead on top. Every
other "the raw size looks obvious" assumption in this project's history
has turned out to need a real overhead correction once actual capture data
came in (see docs/RESOLVED_QUESTIONS.md), so this is flagged as UNMODELED
for the controller-memory total (not summed into it) until real capture
data confirms the relationship -- same treatment AXIS_CIP_DRIVE/MOTION_GROUP
got before their own real formulas were derived (see sizing/report.py's
SizeError pattern for AXIS_* types). The parsed ModuleInfo data is still
surfaced (module name, catalog, raw stated sizes) so the next real test
round (a small set of real captures with a known module added/removed) can
fit the true per-module/per-connection overhead constant directly against
these already-exact raw sizes -- a much smaller fitting problem than usual,
since the base size is real, not guessed.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleInfo:
    name: str
    catalog_number: str
    slot: int | None
    connection_input_bytes: int
    connection_output_bytes: int
    config_bytes: int
    # Rockwell's own internal module-profile identifier, e.g.
    # "AB:5000_DI16:I:0" / "AB:5000_DI16:C:0" -- the Structure DataType on
    # each of InputTag/OutputTag/ConfigTag's own <Data Format="Decorated">
    # body (2026-08-27, James: "add records from the L5X module profile as
    # a checkable item"). Kept separately per I/O direction rather than
    # collapsed into one field -- a module's Input and Config profiles are
    # DIFFERENT strings (same base type, different :I:/:O:/:C: suffix),
    # not one shared identifier, and James asked for in/out/config kept
    # separately marked throughout, not just for the byte counts.
    input_profile: str | None
    output_profile: str | None
    config_profile: str | None

    @property
    def stated_total_bytes(self) -> int:
        """Sum of every raw size L5X itself states for this module --
        NOT a confirmed controller-memory cost, see module docstring."""
        return self.connection_input_bytes + self.connection_output_bytes + self.config_bytes


def _int_attr(el: ET.Element, name: str) -> int:
    val = el.get(name)
    return int(val) if val is not None else 0


def _structure_datatype(tag_el: ET.Element | None) -> str | None:
    """The module-profile string off a <ConfigTag>/<InputTag>/<OutputTag>'s
    own <Data Format="Decorated"><Structure DataType="..."> body, if
    present. Real shape confirmed 2026-08-27 against samples/local/
    DnR_Personal/*.L5X -- e.g. ConfigTag's own Structure carries
    "AB:5000_DI16:C:0", InputTag's carries "AB:5000_SDI8:I:0" (same base
    module type, different suffix per I/O direction)."""
    if tag_el is None:
        return None
    for data_el in tag_el.findall("Data"):
        if data_el.get("Format") == "Decorated":
            structure_el = data_el.find("Structure")
            if structure_el is not None:
                return structure_el.get("DataType")
    return None


def parse_modules(root: ET.Element) -> list[ModuleInfo]:
    modules_el = root.find("Controller/Modules")
    if modules_el is None:
        return []

    result: list[ModuleInfo] = []
    for module_el in modules_el.findall("Module"):
        name = module_el.get("Name", "")
        catalog = module_el.get("CatalogNumber", "")

        slot: int | None = None
        ports_el = module_el.find("Ports")
        if ports_el is not None:
            port_el = ports_el.find("Port")
            if port_el is not None and port_el.get("Address") is not None:
                try:
                    slot = int(port_el.get("Address"))
                except ValueError:
                    slot = None

        input_bytes = 0
        output_bytes = 0
        input_profile: str | None = None
        output_profile: str | None = None
        config_bytes = 0
        config_profile: str | None = None

        comm_el = module_el.find("Communications")
        if comm_el is not None:
            connections_el = comm_el.find("Connections")
            if connections_el is not None:
                for conn_el in connections_el.findall("Connection"):
                    input_bytes += _int_attr(conn_el, "InputSize")
                    output_bytes += _int_attr(conn_el, "OutputSize")

            config_tag_el = comm_el.find("ConfigTag")
            if config_tag_el is not None:
                config_bytes = _int_attr(config_tag_el, "ConfigSize")
                config_profile = _structure_datatype(config_tag_el)

            input_profile = _structure_datatype(comm_el.find("InputTag"))
            output_profile = _structure_datatype(comm_el.find("OutputTag"))

        result.append(ModuleInfo(
            name=name, catalog_number=catalog, slot=slot,
            connection_input_bytes=input_bytes, connection_output_bytes=output_bytes,
            config_bytes=config_bytes,
            input_profile=input_profile, output_profile=output_profile, config_profile=config_profile,
        ))
    return result
