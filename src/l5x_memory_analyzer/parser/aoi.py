"""Parses Controller/AddOnInstructionDefinitions out of an L5X document.

An AOI instance's data structure is, for sizing purposes, exactly a UDT: its
Input/Output Parameters plus its LocalTags are storage members, recursed and
summed the same way DataTypeDef/Member already work for Controller/DataTypes
-- so this module reuses those same dataclasses rather than inventing a
parallel shape. Confirmed against real production L5X data (2026-08-20):
every AOI-typed tag found there is a plain named Tag with DataType=<AOIName>,
sized identically to any UDT-typed tag with no logic/call-site parsing
needed. That's a different (and much smaller) problem than OQ-AOIINSTANCE's
inline/anonymous-instance-per-call-site question -- see docs/OPEN_QUESTIONS.md.

InOut parameters are excluded entirely: they're a reference to a caller-scope
tag's existing memory, not a new allocation, per standard documented AOI
behavior.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from l5x_memory_analyzer.parser.datatypes import DataTypeDef, Member

_STORAGE_USAGES = {"Input", "Output"}


def _member_from_element(el: ET.Element) -> Member:
    # Real bug, found 2026-08-27 auditing James's own corpus: <Parameter>
    # and <LocalTag> elements carry their array size on a "Dimensions"
    # (PLURAL) attribute -- confirmed against 80 real <Parameter
    # Dimensions="N"> and 191 real <LocalTag Dimensions="N"> elements
    # across all 64 real corpus files, zero counter-examples anywhere for
    # the singular form. This previously read "Dimension" (singular, the
    # attribute name real <Member> elements inside a plain UDT use
    # instead -- see parser/datatypes.py, correct there) which never
    # matched, so every array-dimensioned AOI Parameter/LocalTag was
    # silently sized as a scalar. Confirmed real-world impact: 24 of
    # James's 64 files carry an AOI with an array-typed local/param
    # (CAM_PROFILE-backed camming AOIs are the most common real case).
    return Member(
        name=el.get("Name"),
        data_type=el.get("DataType"),
        dimension=int(el.get("Dimensions", "0")),
    )


def parse_aoi_definitions(root: ET.Element) -> dict[str, DataTypeDef]:
    result: dict[str, DataTypeDef] = {}
    aois_el = root.find("Controller/AddOnInstructionDefinitions")
    if aois_el is None:
        return result

    for aoi_el in aois_el.findall("AddOnInstructionDefinition"):
        name = aoi_el.get("Name")
        members: list[Member] = []

        params_el = aoi_el.find("Parameters")
        if params_el is not None:
            for p_el in params_el.findall("Parameter"):
                if p_el.get("Usage") in _STORAGE_USAGES:
                    members.append(_member_from_element(p_el))

        local_tags_el = aoi_el.find("LocalTags")
        if local_tags_el is not None:
            for lt_el in local_tags_el.findall("LocalTag"):
                members.append(_member_from_element(lt_el))

        result[name] = DataTypeDef(name=name, family="NoFamily", members=members, is_aoi=True)

    return result
