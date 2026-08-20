"""Parses controller-scope and program-scope Tag elements out of an L5X document."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

CONTROLLER_SCOPE = "controller"


@dataclass(frozen=True)
class Tag:
    name: str
    data_type: str
    dimensions: tuple[int, ...]
    scope: str  # CONTROLLER_SCOPE or "program:<ProgramName>"

    @property
    def path(self) -> str:
        return f"{self.scope}/{self.name}"


def _parse_dimensions(raw: str | None) -> tuple[int, ...]:
    if not raw:
        return ()
    parts = raw.replace(",", " ").split()
    dims = tuple(int(p) for p in parts)
    return dims if any(dims) else ()


def _parse_tag_elements(tags_el: ET.Element, scope: str) -> list[Tag]:
    tags = []
    for tag_el in tags_el.findall("Tag"):
        tags.append(
            Tag(
                name=tag_el.get("Name"),
                data_type=tag_el.get("DataType"),
                dimensions=_parse_dimensions(tag_el.get("Dimensions")),
                scope=scope,
            )
        )
    return tags


def parse_tags(root: ET.Element) -> list[Tag]:
    tags: list[Tag] = []

    controller_tags_el = root.find("Controller/Tags")
    if controller_tags_el is not None:
        tags.extend(_parse_tag_elements(controller_tags_el, CONTROLLER_SCOPE))

    programs_el = root.find("Controller/Programs")
    if programs_el is not None:
        for program_el in programs_el.findall("Program"):
            program_name = program_el.get("Name")
            program_tags_el = program_el.find("Tags")
            if program_tags_el is not None:
                tags.extend(
                    _parse_tag_elements(program_tags_el, f"program:{program_name}")
                )

    return tags
