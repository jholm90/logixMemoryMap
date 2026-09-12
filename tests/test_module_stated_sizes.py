"""The L5X's own stated size is the final decision on module sizing.

2026-09-12 rule: a module's cost is its overhead plus the size the FILE states,
and every module gets sized -- there is no shape whose declared data is free.
Some catalogs (ETHERNET-MODULE, ETHERNET-PANELVIEW, generic devices) have their
connection sizes typed in by hand, so the catalog cannot know the size and only
the file can.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from l5x_memory_analyzer.parser.modules import parse_modules


def _root(module_xml: str) -> ET.Element:
    return ET.fromstring(f"""
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="T" ProcessorType="1756-L81E" MajorRev="35" MinorRev="11">
        <DataTypes/><AddOnInstructionDefinitions/><Tags/><Programs/>
        <Modules>
          <Module Name="Local" CatalogNumber="1756-L81E">
            <Ports><Port Id="1" Address="0" Type="ICP" Upstream="false"/></Ports>
          </Module>
          {module_xml}
        </Modules>
        <Tasks/>
      </Controller>
    </RSLogix5000Content>""")


def _generic(input_size: int, output_size: int, resolvable: bool) -> str:
    """A generic ETHERNET-MODULE. `resolvable=False` uses the real
    AB:ETHERNET_MODULE_INT_<n>Bytes structure type, which the member walk
    cannot size, so only the stated attribute knows the answer."""
    # resolvable: a plain INT ArrayMember, which the member walk sizes.
    # unresolvable: an ArrayMember whose DataType is itself a module-defined
    # structure -- the real shape a bridge's Slot array has, and the one case
    # _structure_size collects into unknown_member_types instead of sizing.
    dt_in = "INT" if resolvable else "SLOT"
    body_in = (f'<ArrayMember Name="Data" DataType="INT" Dimensions="{input_size // 2}"'
               f' Radix="Decimal"/>' if resolvable else
               f'<ArrayMember Name="Data" DataType="AB:ETHERNET_MODULE_SLOT:I:0"'
               f' Dimensions="{input_size // 2}"/>')
    return f"""
    <Module Name="Gen1" CatalogNumber="ETHERNET-MODULE" Vendor="1" ProductType="0"
     ProductCode="18" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2"
     Inhibited="false" MajorFault="false">
      <EKey State="Disabled"/>
      <Ports><Port Id="2" Address="192.168.1.20" Type="Ethernet" Upstream="true"/></Ports>
      <Communications CommMethod="536870915" PrimCxnInputSize="{input_size}"
       PrimCxnOutputSize="{output_size}">
        <Connections>
          <Connection Name="Standard" RPI="10000" Type="Output" InputSize="{input_size}"
           OutputSize="{output_size}" EventID="0"
           ProgrammaticallySendEventTrigger="false" Unicast="true">
            <InputTag ExternalAccess="Read/Write">
              <Data Format="Decorated">
                <Structure DataType="AB:ETHERNET_MODULE_{dt_in}_{input_size}Bytes:I:0">
                  {body_in}
                </Structure>
              </Data>
            </InputTag>
          </Connection>
        </Connections>
      </Communications>
    </Module>"""


def _module(root: ET.Element):
    return next(m for m in parse_modules(root) if m.name != "Local")


def test_unresolvable_connection_falls_back_to_the_stated_input_size() -> None:
    """The member walk cannot size AB:ETHERNET_MODULE_* structures. Dropping
    them made the total a silent floor on exactly the modules whose size is not
    a property of their catalog."""
    m = _module(_root(_generic(450, 8, resolvable=False)))
    assert m.module_defined_bytes == 450
    assert m.unknown_member_types  # still reported, not silently absorbed
    assert any("stated InputSize=450" in u for u in m.unknown_member_types)


def test_two_instances_of_one_catalog_get_different_sizes() -> None:
    """109 real ETHERNET-MODULE instances carry 40 distinct connection shapes,
    input spanning 2 to 450 bytes. A per-catalog constant cannot express that;
    the file can."""
    small = _module(_root(_generic(2, 2, resolvable=False))).module_defined_bytes
    large = _module(_root(_generic(450, 8, resolvable=False))).module_defined_bytes
    assert large - small == 448


def test_member_walk_still_wins_when_it_can_resolve_the_type() -> None:
    """Stated size is the FALLBACK, not the override: the walk is finer-grained
    (it sees real member padding) and agrees with the attribute where both
    exist."""
    m = _module(_root(_generic(64, 2, resolvable=True)))
    assert m.module_defined_bytes == 64
    assert not m.unknown_member_types
