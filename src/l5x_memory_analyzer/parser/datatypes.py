"""Parses Controller/DataTypes (UDT definitions) out of an L5X document.

BOOL members inside a UDT are represented by Logix Designer itself as a
hidden backing SINT member plus visible DataType="BIT" alias members
(Target/BitNumber pointing at the backing SINT) -- the 8-per-byte packing
described in docs/MEMORY_MODEL.md is already encoded in the XML shape, not
something this parser has to re-derive.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Member:
    name: str
    data_type: str
    dimension: int
    hidden: bool = False

    @property
    def is_bit_alias(self) -> bool:
        return self.data_type == "BIT"


@dataclass(frozen=True)
class DataTypeDef:
    name: str
    family: str = "NoFamily"  # "StringFamily" marks a user-defined string type
    members: list[Member] = field(default_factory=list)

    @property
    def is_string_family(self) -> bool:
        return self.family == "StringFamily"


def parse_data_types(root: ET.Element) -> dict[str, DataTypeDef]:
    result: dict[str, DataTypeDef] = {}
    data_types_el = root.find("Controller/DataTypes")
    if data_types_el is None:
        return result

    for dt_el in data_types_el.findall("DataType"):
        name = dt_el.get("Name")
        members = []
        members_el = dt_el.find("Members")
        if members_el is not None:
            for m_el in members_el.findall("Member"):
                members.append(
                    Member(
                        name=m_el.get("Name"),
                        data_type=m_el.get("DataType"),
                        dimension=int(m_el.get("Dimension", "0")),
                        hidden=m_el.get("Hidden", "false").lower() == "true",
                    )
                )
        result[name] = DataTypeDef(
            name=name, family=dt_el.get("Family", "NoFamily"), members=members
        )

    return result
