"""Safety I/O devices (OQ-SAFETYPARTITION, round 5): the CIP Safety connections of a
project's modules, which cost safety memory by the data type they carry and a further
amount of standard memory beyond what the module's own sizing charges.

A device is a module with at least one Safety* connection. Its type family is the
connection's decorated data type without its connection suffix ("AB:5000_SDI16:I:0" ->
"AB:5000_SDI16"; an EDS profile's "_002B:BNI00HN_B482D29B:SI:0" -> "_002B:BNI00HN").
A measured device type is priced from its own table entry. Any other -- a custom card,
another vendor's device, an EDS profile -- by the device law the 18 measured types follow:
an overhead per safety connection plus its connection data (safety partition), and a
per-device overhead plus its data types' definitions (standard).
Constants: memory_model.yaml safety_io; MEMORY_MODEL.md, "Safety I/O".
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

_SUFFIX = re.compile(r"(?:_[0-9A-F]{8})?:[A-Z]+:\d+$")
# Bits a decorated member occupies on the wire, for a connection whose size the file does
# not state (the 1734 and 442G safety connections carry no InputSize / OutputSize).
_BITS = {"BOOL": 1, "SINT": 8, "USINT": 8, "BYTE": 8, "INT": 16, "UINT": 16, "WORD": 16, "DINT": 32,
         "UDINT": 32, "DWORD": 32, "REAL": 32, "LINT": 64, "ULINT": 64, "LWORD": 64, "LREAL": 64}


@dataclass(frozen=True)
class SafetyDevice:
    name: str
    catalog: str  # CatalogNumber, or "vendor<V>:<ProductCode>" for an EDS profile without one
    families: tuple[str, ...]
    # Its connection shape, for the device law: safety input and output connections that
    # carry a tag, the bytes of data they carry, and its standard (non-safety, non-motion)
    # data connections. A motion device (a drive) is priced by the motion laws instead.
    safety_inputs: int = 0
    safety_outputs: int = 0
    safety_data_bytes: int = 0
    standard_connections: int = 0
    motion: bool = False


def type_family(data_type: str) -> str:
    return _SUFFIX.sub("", data_type)


def _decorated_bits(struct: ET.Element) -> int:
    bits = 0
    for child in struct:
        if child.tag == "DataValueMember":
            bits += _BITS.get(child.get("DataType") or "", 0)
        elif child.tag == "ArrayMember":
            width = _BITS.get(child.get("DataType") or "")
            if width:
                bits += width * int((child.get("Dimensions") or "0").split(",")[0] or 0)
            else:
                bits += sum(_decorated_bits(el) for el in child.iter("Structure"))
        elif child.tag in ("StructureMember", "Structure"):
            bits += _decorated_bits(child)
    return bits


def _tag_structure(conn: ET.Element, tag_name: str) -> ET.Element | None:
    tag = conn.find(tag_name)
    return tag.find("Data[@Format='Decorated']/Structure") if tag is not None else None


def device_of(mod: ET.Element) -> SafetyDevice | None:
    """The module as a safety device, or None when it has no Safety* connection."""
    families: set[str] = set()
    inputs = outputs = data = standard = 0
    motion = False
    for conn in mod.iter("Connection"):
        conn_type = conn.get("Type") or ""
        if "Motion" in conn_type or "Diagnostic" in conn_type:
            motion = True
            continue
        safety = conn_type.startswith("Safety")
        carried = False
        for tag_name, size_attr in (("InputTag", "InputSize"), ("OutputTag", "OutputSize")):
            struct = _tag_structure(conn, tag_name)
            if struct is None or not struct.get("DataType"):
                continue
            carried = True
            if safety:
                families.add(type_family(struct.get("DataType")))
                stated = int(conn.get(size_attr) or 0)
                data += stated if stated > 0 else math.ceil(_decorated_bits(struct) / 8)
        if not carried:
            continue
        if not safety:
            standard += 1
        elif conn_type.startswith("SafetyOutput"):
            outputs += 1
        else:
            inputs += 1
    if not families:
        return None
    catalog = mod.get("CatalogNumber") or f"vendor{mod.get('Vendor')}:{mod.get('ProductCode')}"
    return SafetyDevice(mod.get("Name") or catalog, catalog, tuple(sorted(families)),
                        inputs, outputs, data, standard, motion)


def safety_devices(root: ET.Element) -> list[SafetyDevice]:
    devices: list[SafetyDevice] = []
    for mod in root.iter("Module"):
        if mod.get("Name") == "Local":
            continue
        device = device_of(mod)
        if device is not None:
            devices.append(device)
    return devices


def device_key(device: SafetyDevice) -> str:
    """The table key: the device's type families joined, so a device is priced only when its
    whole set of safety connections matches a measured one."""
    return "+".join(device.families)


Row = tuple[str, str, str, int, str]


def safety_rows(devices: list[SafetyDevice], model) -> tuple[list[Row], dict[str, int]]:
    """(safety-partition rows, {unmeasured device key: count}). A device of types never
    measured is priced at its connection shape's median and counted as unmeasured."""
    sio = model.safety_io
    rows: list[Row] = []
    unmeasured: dict[str, int] = {}
    for d in devices:
        key = device_key(d)
        if key in sio.safety_bytes:
            rows.append((f"safety_io/{d.name}", "module_io", key, sio.safety_bytes[key], sio.safety_confidence))
        else:
            rows.append((f"safety_io/{d.name}", "module_io", key, sio.unseen_safety_bytes(d),
                         sio.unseen_confidence))
            unmeasured[key] = unmeasured.get(key, 0) + 1
    return rows, unmeasured


def has_standard_terms(d: SafetyDevice, sio) -> bool:
    """True when the device's standard cost has measured terms (its device key or catalog)."""
    return _standard_key(d, sio) in sio.standard_each_bytes or _standard_key(d, sio) in sio.standard_first_bytes


def _standard_key(d: SafetyDevice, sio) -> str:
    """The standard table's key for a device: its device key where the table has one (a
    catalog carrying more than one safety shape), else its catalog."""
    key = device_key(d)
    return key if key in sio.standard_each_bytes or key in sio.standard_first_bytes else d.catalog


def standard_rows(devices: list[SafetyDevice], model) -> list[Row]:
    """Standard memory a safety device costs beyond its module's own sizing."""
    sio = model.safety_io
    rows: list[Row] = []
    seen: set[str] = set()
    for d in devices:
        key = _standard_key(d, sio)
        size = sio.standard_each_bytes.get(key, 0)
        if key not in seen:
            seen.add(key)
            size += sio.standard_first_bytes.get(key, 0)
        if size:
            rows.append((f"safety_io_standard/{d.name}", "module_io", key, size, sio.standard_confidence))
    for prefix, size in sio.standard_shared_first_bytes.items():
        if any(f.startswith(prefix) for d in devices for f in d.families):
            rows.append((f"safety_io_standard/{prefix}", "module_io", prefix, size, sio.standard_confidence))
    return rows
