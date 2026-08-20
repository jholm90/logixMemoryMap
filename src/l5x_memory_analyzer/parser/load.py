"""L5X file loading and basic schema sanity checks.

Version pinning is an open question (see docs/OPEN_QUESTIONS.md, OQ-L5XVERSION) --
this module records the SchemaRevision/SoftwareRevision found on the root element
but does not yet reject unrecognized versions.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

EXPECTED_ROOT_TAG = "RSLogix5000Content"


class L5XFormatError(ValueError):
    """Raised when a file does not look like an L5X export."""


CONTROLLER_TARGET_TYPE = "Controller"


@dataclass
class L5XDocument:
    path: Path
    root: ET.Element
    schema_revision: str | None
    software_revision: str | None
    target_type: str | None
    processor_type: str | None

    @property
    def is_controller_export(self) -> bool:
        return self.target_type == CONTROLLER_TARGET_TYPE


def _build_document(root: ET.Element, display_name: str) -> L5XDocument:
    if root.tag != EXPECTED_ROOT_TAG:
        raise L5XFormatError(
            f"{display_name}: root element is <{root.tag}>, expected <{EXPECTED_ROOT_TAG}>"
        )

    controller_el = root.find("Controller")
    processor_type = controller_el.get("ProcessorType") if controller_el is not None else None

    return L5XDocument(
        path=Path(display_name),
        root=root,
        schema_revision=root.get("SchemaRevision"),
        software_revision=root.get("SoftwareRevision"),
        target_type=root.get("TargetType"),
        processor_type=processor_type,
    )


def load_l5x(path: str | Path) -> L5XDocument:
    path = Path(path)
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise L5XFormatError(f"{path}: not well-formed XML ({exc})") from exc
    return _build_document(tree.getroot(), str(path))


def load_l5x_bytes(data: bytes, display_name: str) -> L5XDocument:
    """Same validation as load_l5x, but from in-memory bytes -- used by the
    UI's File->Open upload, which never touches a server-side filesystem path."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise L5XFormatError(f"{display_name}: not well-formed XML ({exc})") from exc
    return _build_document(root, display_name)
