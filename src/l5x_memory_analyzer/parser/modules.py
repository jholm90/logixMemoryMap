"""Parses Controller/Modules out of an L5X document (2026-08-27, first pass
-- James's Phase 1 "Module/IO parsing is still open" gap, never started
before now).

**2026-08-27, real gap found and fixed same day (James's own real-capture
data forced the correction):** the original version of this parser assumed
`InputSize`/`OutputSize`/`ConfigSize` attributes tell the whole story, and
that InputTag/OutputTag sit as direct `<Communications>` children. Both
assumptions were wrong for the dominant real shape: most real modules state
NO InputSize/OutputSize attribute at all (their I/O lives in a nested
`<Connection><InputTag>` element instead, or gets aliased into a parent
bridge's own Slot array via `<RackConnection><InAliasTag/></RackConnection>`
with no connection-level size of its own), and InputTag/OutputTag are
nested INSIDE their owning `<Connection>`, not a `<Communications>` sibling.
Fixed both: `module_defined_bytes` now computes the REAL raw size by
summing every atomic member of each InputTag/OutputTag/ConfigTag's own
`<Data Format="Decorated"><Structure>` content (the same member-sum logic
`compute_udt_size` already uses for an ordinary UDT) -- this is exactly the
"Module-Defined" data type Logix Designer auto-generates under
Data Types -> Module-Defined for every added module (James, 2026-08-27:
"you should see a new UDT under module-defined... you will then have to do
a % difference between those combined udts and how much actual space it
takes up").

**That % difference is real, large, and already computed from 2 real
captures (2026-08-27):** `module_defined_bytes` for a 1756-IB16 is 28
bytes; its real captured cost is 1,712 bytes -- **98.4% of the real cost
is NOT the I/O data itself.** A 1734-AENTR/C: 36 bytes computed vs 1,696
real -- **97.9% overhead.** Two very different module types landing on
almost the SAME overhead (1,684 / 1,660, within noise of each other)
strongly suggests a large, close-to-flat per-module cost dominates,
similar in spirit to how AOI/UDT definition cost turned out to be
dominated by a flat base term, not the member list. See
`memory_model.yaml` `module_overhead` for the current (FITTED, n=2, real
but low-confidence) estimate and `docs/OPEN_QUESTIONS.md` OQ-MODULEIO for
the full derivation -- more real per-module deltas are needed to confirm
this holds as a genuine flat constant vs. something that scales with
connection count/module family.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

# Same atomic-size convention as sizing/udt.py's compute_udt_size -- a
# module's own auto-generated Structure members are plain DataValueMember/
# ArrayMember entries, never bit-aliased BOOL runs (confirmed real,
# 2026-08-27: a module's BOOL members show up as plain DataType="BOOL",
# same as an AOI's Parameters/LocalTags, not a UDT's hidden-SINT/BIT-alias
# shape) -- so BOOL sizes as the standalone/unpacked 4 bytes, not packed.
_ATOMIC_BYTES = {"SINT": 1, "INT": 2, "DINT": 4, "LINT": 8, "REAL": 4, "BOOL": 4}

# James, 2026-08-30: "I thought we were excluding controlnet" / "And all
# legacy networks" -- a bridge module onto a pre-EtherNet/IP network
# (ControlNet, DeviceNet, DH+/DH-485, Remote I/O) gets the same treatment
# as a rack-aliased or processor-embedded module in report.py: zero real
# capture data exists for this shape's overhead cost (the one real point,
# modulesweep_1756_cnb_d, came from a file outside the current samples/
# local/ real corpus -- see OQ-LEGACYNETOVERHEAD), and the current real
# corpus has zero ControlNet/DeviceNet/DH+/RIO Port Types anywhere, so
# fitting a per-catalog byte value here would be a pure guess dressed up
# as ASSUMED. Detected off the module's own <Ports><Port Type="..."/>
# attributes (confirmed real shape: "ControlNet", "DeviceNet", "RIO" --
# see gen_module_sweep.py's 1756-CNB/D, 1756-DHRIO/E, 1756-DNB fixtures).
_LEGACY_NETWORK_PORT_TYPES = frozenset({"ControlNet", "DeviceNet", "DH+", "DH-485", "RIO"})


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
    # Real raw member-sum size of this module's own auto-generated
    # "Module-Defined" data type (2026-08-27) -- computed from the actual
    # Structure content under InputTag/OutputTag/ConfigTag, NOT the
    # (frequently absent) InputSize/OutputSize attribute. This is the
    # number James's methodology starts from: what you'd see if you sized
    # that Module-Defined UDT the normal way.
    module_defined_bytes: int = 0
    unknown_member_types: tuple[str, ...] = field(default_factory=tuple)
    # A VFD's real parameter-database blob (2026-08-27, PowerFlex 525/755
    # corpus) -- L5K only, its own stated Size attribute, already folded
    # into module_defined_bytes above but kept visible separately too
    # since it's the single biggest real contributor for a drive module.
    config_script_bytes: int = 0
    # True when this module's I/O is aliased into a parent bridge's own
    # Slot array (<RackConnection><InAliasTag/></RackConnection>) instead
    # of having its own real Connection -- module_overhead (memory_model.
    # yaml) was fitted from 2 modules that both have their OWN Connection,
    # not this shape, so report.py deliberately does NOT charge overhead
    # to a rack-aliased module: zero real data exists yet for whether its
    # incremental cost looks anything like a normal module's.
    uses_rack_connection: bool = False
    # Port Type values off this module's own <Ports><Port> elements (e.g.
    # "ICP", "Ethernet", "ControlNet", "DeviceNet", "RIO") -- see
    # _LEGACY_NETWORK_PORT_TYPES above. Kept as the raw set rather than a
    # collapsed bool so report.py can name which network in its SizeError.
    port_types: frozenset[str] = field(default_factory=frozenset)

    @property
    def is_legacy_network(self) -> bool:
        """True if any of this module's own ports bridge onto a
        pre-EtherNet/IP network (ControlNet/DeviceNet/DH+/DH-485/RIO) --
        see _LEGACY_NETWORK_PORT_TYPES."""
        return bool(self.port_types & _LEGACY_NETWORK_PORT_TYPES)

    @property
    def stated_total_bytes(self) -> int:
        """Sum of every raw size L5X itself states for this module (the
        InputSize/OutputSize/ConfigSize attributes, when present) -- kept
        for backward compatibility/comparison, but module_defined_bytes is
        the real number now; most real modules state 0 here even though
        they carry real I/O data (see module docstring)."""
        return self.connection_input_bytes + self.connection_output_bytes + self.config_bytes


def _int_attr(el: ET.Element, name: str) -> int:
    val = el.get(name)
    return int(val) if val is not None else 0


def _structure_el(tag_el: ET.Element | None) -> ET.Element | None:
    if tag_el is None:
        return None
    for data_el in tag_el.findall("Data"):
        if data_el.get("Format") == "Decorated":
            return data_el.find("Structure")
    return None


def _structure_datatype(tag_el: ET.Element | None) -> str | None:
    """The module-profile string off a <ConfigTag>/<InputTag>/<OutputTag>'s
    own <Data Format="Decorated"><Structure DataType="..."> body, if
    present. Real shape confirmed 2026-08-27 against samples/local/
    DnR_Personal/*.L5X -- e.g. ConfigTag's own Structure carries
    "AB:5000_DI16:C:0", InputTag's carries "AB:5000_SDI8:I:0" (same base
    module type, different suffix per I/O direction)."""
    structure_el = _structure_el(tag_el)
    return structure_el.get("DataType") if structure_el is not None else None


def _structure_size(structure_el: ET.Element | None) -> tuple[int, list[str]]:
    """Raw member-sum size of a module's own Structure, the same way an
    ordinary UDT's member list sizes -- sum of each DataValueMember's
    atomic size, or ArrayMember's atomic size x Dimensions. A nested nested
    Structure (e.g. a bridge's Slot ArrayMember, DataType pointing at
    another Structure rather than an atomic type) isn't a module this
    project sizes yet -- collected into unknown_member_types rather than
    silently mis-sized as 0, so it's visibly incomplete, not silently
    wrong."""
    if structure_el is None:
        return 0, []
    total = 0
    unknown: list[str] = []
    for child in structure_el:
        dtype = child.get("DataType")
        if child.tag == "DataValueMember":
            size = _ATOMIC_BYTES.get(dtype)
            if size is None:
                unknown.append(dtype or "?")
                continue
            total += size
        elif child.tag == "ArrayMember":
            size = _ATOMIC_BYTES.get(dtype)
            dims = int(child.get("Dimensions", "0"))
            if size is None:
                unknown.append(f"{dtype}[{dims}]")
                continue
            total += size * dims
        elif child.tag == "Structure":
            sub_total, sub_unknown = _structure_size(child)
            total += sub_total
            unknown.extend(sub_unknown)
    return total, unknown


def parse_modules(root: ET.Element) -> list[ModuleInfo]:
    modules_el = root.find("Controller/Modules")
    if modules_el is None:
        return []

    result: list[ModuleInfo] = []
    for module_el in modules_el.findall("Module"):
        name = module_el.get("Name", "")
        catalog = module_el.get("CatalogNumber", "")

        slot: int | None = None
        port_types: set[str] = set()
        ports_el = module_el.find("Ports")
        if ports_el is not None:
            port_el = ports_el.find("Port")
            if port_el is not None and port_el.get("Address") is not None:
                try:
                    slot = int(port_el.get("Address"))
                except ValueError:
                    slot = None
            for p_el in ports_el.findall("Port"):
                p_type = p_el.get("Type")
                if p_type:
                    port_types.add(p_type)

        input_bytes = 0
        output_bytes = 0
        input_profile: str | None = None
        output_profile: str | None = None
        config_bytes = 0
        config_profile: str | None = None
        config_script_bytes = 0
        module_defined_bytes = 0
        unknown_types: list[str] = []

        uses_rack_connection = False
        comm_el = module_el.find("Communications")
        if comm_el is not None:
            connections_el = comm_el.find("Connections")
            if connections_el is not None:
                uses_rack_connection = connections_el.find("RackConnection") is not None
                for conn_el in connections_el.findall("Connection"):
                    input_bytes += _int_attr(conn_el, "InputSize")
                    output_bytes += _int_attr(conn_el, "OutputSize")
                    # InputTag/OutputTag live INSIDE their owning Connection
                    # in every real shape found this session, not as a
                    # Communications sibling -- see module docstring.
                    input_tag_el = conn_el.find("InputTag")
                    if input_tag_el is not None:
                        if input_profile is None:
                            input_profile = _structure_datatype(input_tag_el)
                        size, unk = _structure_size(_structure_el(input_tag_el))
                        module_defined_bytes += size
                        unknown_types.extend(unk)
                    output_tag_el = conn_el.find("OutputTag")
                    if output_tag_el is not None:
                        if output_profile is None:
                            output_profile = _structure_datatype(output_tag_el)
                        size, unk = _structure_size(_structure_el(output_tag_el))
                        module_defined_bytes += size
                        unknown_types.extend(unk)

            # ConfigTag (Decorated Structure content available -- e.g. every
            # I/O module found this session) vs ConfigData (2026-08-27,
            # found in the real motion/drive corpus -- P208/D012/S086 all
            # use this instead: an L5K-only blob, NO Decorated structure at
            # all, just a real stated ConfigSize). Both carry a real
            # ConfigSize attribute; only ConfigTag's Decorated form can be
            # summed member-by-member, so ConfigData falls back to its own
            # stated attribute -- still real, not guessed, just less
            # granular than computing from actual member content.
            config_tag_el = comm_el.find("ConfigTag")
            if config_tag_el is not None:
                config_bytes = _int_attr(config_tag_el, "ConfigSize")
                config_profile = _structure_datatype(config_tag_el)
                size, unk = _structure_size(_structure_el(config_tag_el))
                module_defined_bytes += size
                unknown_types.extend(unk)
            else:
                config_data_el = comm_el.find("ConfigData")
                if config_data_el is not None:
                    config_bytes = _int_attr(config_data_el, "ConfigSize")
                    module_defined_bytes += config_bytes

            # ConfigScript (2026-08-27, found in real VFD corpus -- PowerFlex
            # 525/755 both carry one ALONGSIDE their own ConfigData, not
            # instead of it): a real, stated `Size` attribute (not
            # `ConfigSize`) on the drive's full parameter-database blob, L5K
            # only, no Decorated form. Same floor treatment as ConfigData.
            config_script_el = comm_el.find("ConfigScript")
            if config_script_el is not None:
                config_script_bytes = _int_attr(config_script_el, "Size")
                module_defined_bytes += config_script_bytes

        result.append(ModuleInfo(
            name=name, catalog_number=catalog, slot=slot,
            connection_input_bytes=input_bytes, connection_output_bytes=output_bytes,
            config_bytes=config_bytes,
            input_profile=input_profile, output_profile=output_profile, config_profile=config_profile,
            module_defined_bytes=module_defined_bytes, unknown_member_types=tuple(unknown_types),
            uses_rack_connection=uses_rack_connection, config_script_bytes=config_script_bytes,
            port_types=frozenset(port_types),
        ))
    return result
