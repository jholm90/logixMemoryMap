"""Parses controller-scope and program-scope Tag elements out of an L5X document."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

CONTROLLER_SCOPE = "controller"
ALIAS_TAG_TYPE = "Alias"


@dataclass(frozen=True)
class Tag:
    name: str
    data_type: str | None  # None for Alias tags -- see is_alias
    dimensions: tuple[int, ...]
    scope: str  # CONTROLLER_SCOPE or "program:<ProgramName>"
    tag_type: str = "Base"
    alias_for: str | None = None

    @property
    def path(self) -> str:
        return f"{self.scope}/{self.name}"

    @property
    def is_alias(self) -> bool:
        # Alias tags carry no DataType of their own in the L5X -- they're a
        # pointer/rename onto another tag or module I/O point, and consume
        # no memory beyond what the aliased target already accounts for.
        return self.tag_type == ALIAS_TAG_TYPE


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
                tag_type=tag_el.get("TagType", "Base"),
                alias_for=tag_el.get("AliasFor"),
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
