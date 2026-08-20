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


@dataclass
class L5XDocument:
    path: Path
    root: ET.Element
    schema_revision: str | None
    software_revision: str | None


def load_l5x(path: str | Path) -> L5XDocument:
    path = Path(path)
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise L5XFormatError(f"{path}: not well-formed XML ({exc})") from exc

    root = tree.getroot()
    if root.tag != EXPECTED_ROOT_TAG:
        raise L5XFormatError(
            f"{path}: root element is <{root.tag}>, expected <{EXPECTED_ROOT_TAG}>"
        )

    return L5XDocument(
        path=path,
        root=root,
        schema_revision=root.get("SchemaRevision"),
        software_revision=root.get("SoftwareRevision"),
    )
