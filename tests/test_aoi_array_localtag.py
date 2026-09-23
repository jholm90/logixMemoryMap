"""Array-dimensioned AOI declared members cost their own data space.

OQ-AOIARRAYLOCALTAG, wired off the 27-file aoi_arraylocal_* sweep.
"""

from __future__ import annotations

import dataclasses
import xml.etree.ElementTree as ET

from l5x_memory_analyzer.parser.aoi import parse_aoi_definitions
from l5x_memory_analyzer.parser.datatypes import parse_data_types
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.udt import compute_aoi_definition_cost


def _aoi(local_tag_xml: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<RSLogix5000Content SchemaRevision="1.0">
<Controller Name="T" ProcessorType="1756-L81E" MajorRev="35" MinorRev="11">
<DataTypes/>
<AddOnInstructionDefinitions>
<AddOnInstructionDefinition Name="ArrAoi" Revision="1.0" ExecutePrescan="false"
 ExecutePostscan="false" ExecuteEnableInFalse="false" CreatedDate="2026-08-20T12:00:00.000Z"
 CreatedBy="x" EditedDate="2026-08-20T12:00:00.000Z" EditedBy="x" SoftwareRevision="v35.00">
<Parameters>
<Parameter Name="EnableIn" TagType="Base" DataType="BOOL" Usage="Input" Radix="Decimal"
 Required="false" Visible="false" ExternalAccess="Read Only"/>
<Parameter Name="EnableOut" TagType="Base" DataType="BOOL" Usage="Output" Radix="Decimal"
 Required="false" Visible="false" ExternalAccess="Read Only"/>
</Parameters>
<LocalTags>{local_tag_xml}</LocalTags>
</AddOnInstructionDefinition>
</AddOnInstructionDefinitions>
</Controller>
</RSLogix5000Content>"""


def _cost(local_tag_xml: str) -> int:
    """The itemised definition sum, before its 8-byte total alignment -- this
    file isolates the array member's own data bytes by differencing, and
    alignment would quantise that difference. The alignment is tested in
    test_aoi_definition_itemization.py."""
    root = ET.fromstring(_aoi(local_tag_xml))
    model = load_memory_model()
    model = dataclasses.replace(
        model, aoi_definition=dataclasses.replace(model.aoi_definition, total_alignment_bytes=0))
    types = dict(parse_data_types(root))
    types.update(parse_aoi_definitions(root))
    bytes_, _conf = compute_aoi_definition_cost("ArrAoi", types, model)
    return bytes_


def test_dint_array_localtag_charges_element_size_times_dimension() -> None:
    scalar = _cost('<LocalTag Name="Buffer" DataType="DINT" Radix="Decimal"'
                   ' ExternalAccess="None"/>')
    arr = _cost('<LocalTag Name="Buffer" DataType="DINT" Dimensions="50" Radix="Decimal"'
                ' ExternalAccess="None"/>')
    # 50 DINT elements at 4 bytes each. 196, not 200: under the itemised
    # definition formula a declared member costs the descriptor plus its OWN
    # data bytes, so the array's 200 REPLACES the scalar's 4 rather than
    # stacking on top of it. The aoi_arraylocal_dim_* sweep confirms the
    # replacement reading: its residual is flat in dimension from 10 through
    # 1000, so the per-element rate is right.
    assert arr - scalar == 196


def test_array_data_space_is_additive_across_members() -> None:
    one = _cost('<LocalTag Name="Buffer0" DataType="DINT" Dimensions="50" Radix="Decimal"'
                ' ExternalAccess="None"/>')
    two = _cost('<LocalTag Name="Buffer0" DataType="DINT" Dimensions="50" Radix="Decimal"'
                ' ExternalAccess="None"/>'
                '<LocalTag Name="Buffer1" DataType="DINT" Dimensions="50" Radix="Decimal"'
                ' ExternalAccess="None"/>')
    # per_declared_item (20) + member name + the second array's own 200 bytes.
    assert two - one >= 200


def test_bool_array_localtag_is_left_unpriced() -> None:
    """BOOL[50] measured -13, fitting neither 7 packed bytes nor an 8-byte
    two-word rounding, so it is deliberately not approximated."""
    scalar = _cost('<LocalTag Name="Buffer" DataType="BOOL" Radix="Decimal"'
                   ' ExternalAccess="None"/>')
    arr = _cost('<LocalTag Name="Buffer" DataType="BOOL" Dimensions="50" Radix="Decimal"'
                ' ExternalAccess="None"/>')
    assert arr == scalar


def test_predefined_array_structure_member_does_not_raise() -> None:
    """CAM_PROFILE has no scalar element size; real programs declare ten of
    these as array LocalTags, and routing through compute_element_size raised
    UnknownDataTypeError on the first real file the wiring met."""
    assert _cost('<LocalTag Name="Buffer" DataType="CAM_PROFILE" Dimensions="10"'
                 ' ExternalAccess="None"/>') > 0
