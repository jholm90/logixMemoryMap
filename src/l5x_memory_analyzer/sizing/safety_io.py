"""Safety I/O devices (OQ-SAFETYPARTITION, round 5): the CIP Safety connections of a
project's modules, which cost safety memory by the data type they carry and a further
amount of standard memory beyond what the module's own sizing charges.

A device is a module with at least one Safety* connection. Its type family is the
connection's decorated data type without its connection suffix ("AB:5000_SDI16:I:0" ->
"AB:5000_SDI16"; an EDS profile's "_002B:BNI00HN_B482D29B:SI:0" -> "_002B:BNI00HN").
Constants: memory_model.yaml safety_io; MEMORY_MODEL.md, "Safety I/O".
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

_SUFFIX = re.compile(r"(?:_[0-9A-F]{8})?:[A-Z]+:\d+$")


@dataclass(frozen=True)
class SafetyDevice:
    name: str
    catalog: str  # CatalogNumber, or "vendor<V>:<ProductCode>" for an EDS profile without one
    families: tuple[str, ...]


def type_family(data_type: str) -> str:
    return _SUFFIX.sub("", data_type)


def safety_devices(root: ET.Element) -> list[SafetyDevice]:
    devices: list[SafetyDevice] = []
    for mod in root.iter("Module"):
        if mod.get("Name") == "Local":
            continue
        families: set[str] = set()
        for conn in mod.iter("Connection"):
            if not (conn.get("Type") or "").startswith("Safety"):
                continue
            for tag in (conn.find("InputTag"), conn.find("OutputTag")):
                struct = tag.find("Data[@Format='Decorated']/Structure") if tag is not None else None
                if struct is not None and struct.get("DataType"):
                    families.add(type_family(struct.get("DataType")))
        if families:
            catalog = mod.get("CatalogNumber") or f"vendor{mod.get('Vendor')}:{mod.get('ProductCode')}"
            devices.append(SafetyDevice(mod.get("Name") or catalog, catalog, tuple(sorted(families))))
    return devices


def device_key(device: SafetyDevice) -> str:
    """The table key: the device's type families joined, so a device is priced only when its
    whole set of safety connections matches a measured one."""
    return "+".join(device.families)


Row = tuple[str, str, str, int, str]


def safety_rows(devices: list[SafetyDevice], model) -> tuple[list[Row], dict[str, int]]:
    """(safety-partition rows, {unpriced device key: count})."""
    sio = model.safety_io
    rows: list[Row] = []
    unpriced: dict[str, int] = {}
    for d in devices:
        key = device_key(d)
        if key in sio.safety_bytes:
            rows.append((f"safety_io/{d.name}", "module_io", key, sio.safety_bytes[key], sio.safety_confidence))
        else:
            unpriced[key] = unpriced.get(key, 0) + 1
    return rows, unpriced


def standard_rows(devices: list[SafetyDevice], model) -> list[Row]:
    """Standard memory a safety device costs beyond its module's own sizing."""
    sio = model.safety_io
    rows: list[Row] = []
    seen_catalogs: set[str] = set()
    for d in devices:
        size = sio.standard_each_bytes.get(d.catalog, 0)
        if d.catalog not in seen_catalogs:
            seen_catalogs.add(d.catalog)
            size += sio.standard_first_bytes.get(d.catalog, 0)
        if size:
            rows.append((f"safety_io_standard/{d.name}", "module_io", d.catalog, size, sio.standard_confidence))
    for prefix, size in sio.standard_shared_first_bytes.items():
        if any(f.startswith(prefix) for d in devices for f in d.families):
            rows.append((f"safety_io_standard/{prefix}", "module_io", prefix, size, sio.standard_confidence))
    return rows
