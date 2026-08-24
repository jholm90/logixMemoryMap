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
    connection_input_bytes: int
    connection_output_bytes: int
    config_bytes: int

    @property
    def stated_total_bytes(self) -> int:
        """Sum of every raw size L5X itself states for this module --
        NOT a confirmed controller-memory cost, see module docstring."""
        return self.connection_input_bytes + self.connection_output_bytes + self.config_bytes


def _int_attr(el: ET.Element, name: str) -> int:
    val = el.get(name)
    return int(val) if val is not None else 0


def parse_modules(root: ET.Element) -> list[ModuleInfo]:
    modules_el = root.find("Controller/Modules")
    if modules_el is None:
        return []

    result: list[ModuleInfo] = []
    for module_el in modules_el.findall("Module"):
        name = module_el.get("Name", "")
        catalog = module_el.get("CatalogNumber", "")

        input_bytes = 0
        output_bytes = 0
        comm_el = module_el.find("Communications")
        if comm_el is not None:
            connections_el = comm_el.find("Connections")
            if connections_el is not None:
                for conn_el in connections_el.findall("Connection"):
                    input_bytes += _int_attr(conn_el, "InputSize")
                    output_bytes += _int_attr(conn_el, "OutputSize")

        config_bytes = 0
        if comm_el is not None:
            config_tag_el = comm_el.find("ConfigTag")
            if config_tag_el is not None:
                config_bytes = _int_attr(config_tag_el, "ConfigSize")

        result.append(ModuleInfo(
            name=name, catalog_number=catalog,
            connection_input_bytes=input_bytes, connection_output_bytes=output_bytes,
            config_bytes=config_bytes,
        ))
    return result
