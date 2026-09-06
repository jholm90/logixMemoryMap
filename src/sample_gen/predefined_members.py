"""AOI Parameter/LocalTag members whose type is a PREDEFINED STRUCTURE.

2026-09-06. Written for `gen_aoi_structure.py` after a member-type census
of the nine real programs against the whole generated corpus found this:

    type                real AOI member uses   ever generated
    TIMER                              557          0
    DateTime                           120          0
    COUNTER                             66          0
    STRING                              58          2
    MOTION_INSTRUCTION                  36          0
    MESSAGE                             15          0

Every one of those falls through `AoiDefinitionModel.bytes_for`'s
`per_type_rate` table (which only knows BOOL/SINT/INT/LINT) onto the flat
20-bytes-per-declared-item rate, and that rate was fitted entirely on
atomic members. A TIMER is 12 bytes of real storage and five named
members; there is no reason to assume it declares for the same 20 bytes a
DINT does, and until now nothing in the corpus could tell us.

The DefaultData blocks below are copied VERBATIM from the real corpus
rather than synthesized, because the encoding is not derivable: a real
TIMER LocalTag's L5K default is `[0,1500,0]` -- three fields for five
members, because EN/TT/DN alias into the leading status word. Guessing
that encoding would produce a file that lints clean here and then fails
Studio 5000 import, costing a whole capture run to discover.

Sources (all samples/local, gitignored, never committed):
  TIMER, COUNTER, STRING, MOTION_INSTRUCTION  SJ_Gormley_20251112_r02.L5X
  MESSAGE (InOut Parameter, bare)             311DGeneratedProgram.L5X,
                                              BaillieLeitchField_Edger_*.L5X
"""

from __future__ import annotations

from sample_gen.builders import MemberSpec

_TIMER_STRUCT = (
    '<Structure DataType="TIMER">'
    '<DataValueMember Name="PRE" DataType="DINT" Radix="Decimal" Value="0"/>'
    '<DataValueMember Name="ACC" DataType="DINT" Radix="Decimal" Value="0"/>'
    '<DataValueMember Name="EN" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="TT" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="DN" DataType="BOOL" Value="0"/>'
    "</Structure>"
)
_COUNTER_STRUCT = (
    '<Structure DataType="COUNTER">'
    '<DataValueMember Name="PRE" DataType="DINT" Radix="Decimal" Value="0"/>'
    '<DataValueMember Name="ACC" DataType="DINT" Radix="Decimal" Value="0"/>'
    '<DataValueMember Name="CU" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="CD" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="DN" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="OV" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="UN" DataType="BOOL" Value="0"/>'
    "</Structure>"
)
_MOTION_STRUCT = (
    '<Structure DataType="MOTION_INSTRUCTION">'
    '<DataValueMember Name="FLAGS" DataType="DINT" Radix="Decimal" Value="0"/>'
    '<DataValueMember Name="EN" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="DN" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="ER" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="PC" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="IP" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="AC" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="ACCEL" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="DECEL" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="TrackingMaster" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="CalculatedDataAvailable" DataType="BOOL" Value="0"/>'
    '<DataValueMember Name="ERR" DataType="INT" Radix="Decimal" Value="0"/>'
    '<DataValueMember Name="STATUS" DataType="SINT" Radix="Decimal" Value="0"/>'
    '<DataValueMember Name="STATE" DataType="SINT" Radix="Decimal" Value="0"/>'
    '<DataValueMember Name="SEGMENT" DataType="DINT" Radix="Decimal" Value="0"/>'
    '<DataValueMember Name="EXERR" DataType="SINT" Radix="Decimal" Value="0"/>'
    "</Structure>"
)
# Real STRING DefaultData: 82 escaped NULs in the L5K positional list, then
# a Format="String" Length="0" block instead of a Decorated one.
_STRING_L5K = "[0,'" + "$00" * 82 + "']"

_SCALAR_DEFAULTS = {
    "TIMER": f'<DefaultData Format="L5K"><![CDATA[[0,0,0]]]></DefaultData>'
             f'<DefaultData Format="Decorated">{_TIMER_STRUCT}</DefaultData>',
    "COUNTER": f'<DefaultData Format="L5K"><![CDATA[[0,0,0]]]></DefaultData>'
               f'<DefaultData Format="Decorated">{_COUNTER_STRUCT}</DefaultData>',
    "MOTION_INSTRUCTION": f'<DefaultData Format="L5K"><![CDATA[[0,0,0,0,0,0,0,0,0]]]></DefaultData>'
                          f'<DefaultData Format="Decorated">{_MOTION_STRUCT}</DefaultData>',
    "STRING": f'<DefaultData Format="L5K"><![CDATA[{_STRING_L5K}]]></DefaultData>'
              f'<DefaultData Format="String" Length="0"><![CDATA[\'\']]></DefaultData>',
}

_ARRAY_ELEMENT_L5K = {
    "TIMER": "[0,0,0]",
    "COUNTER": "[0,0,0]",
    "MOTION_INSTRUCTION": "[0,0,0,0,0,0,0,0,0]",
}
_ARRAY_STRUCT = {
    "TIMER": _TIMER_STRUCT,
    "COUNTER": _COUNTER_STRUCT,
    "MOTION_INSTRUCTION": _MOTION_STRUCT,
}

SUPPORTED_SCALAR = tuple(_SCALAR_DEFAULTS)
SUPPORTED_ARRAY = tuple(_ARRAY_STRUCT)


def predef_member(name: str, data_type: str, description: str | None = None) -> MemberSpec:
    """A scalar predefined-structure AOI Parameter/LocalTag."""
    if data_type not in _SCALAR_DEFAULTS:
        raise ValueError(
            f"{data_type!r} has no captured real DefaultData shape -- add one from the "
            f"real corpus rather than synthesizing it (see this module's docstring)."
        )
    return MemberSpec(name, data_type, description=description,
                      raw_default_data=_SCALAR_DEFAULTS[data_type])


def predef_array_member(name: str, data_type: str, dimension: int,
                        description: str | None = None) -> MemberSpec:
    """An array-dimensioned predefined-structure AOI LocalTag -- the real
    `Motion` shape (MOTION_INSTRUCTION Dimensions="7") from SJ_Gormley.

    LocalTag only: Logix rejects an array-dimensioned Input/Output
    Parameter outright (see _aoi_parameter_xml), and an InOut Parameter
    carries no DefaultData at all.
    """
    if data_type not in _ARRAY_STRUCT:
        raise ValueError(f"{data_type!r}: no captured real array element shape.")
    l5k = ",".join([_ARRAY_ELEMENT_L5K[data_type]] * dimension)
    elements = "".join(
        f'<Element Index="[{i}]">{_ARRAY_STRUCT[data_type]}</Element>' for i in range(dimension)
    )
    raw = (
        f'<DefaultData Format="L5K"><![CDATA[[{l5k}]]]></DefaultData>'
        f'<DefaultData Format="Decorated">'
        f'<Array DataType="{data_type}" Dimensions="{dimension}">{elements}</Array>'
        f"</DefaultData>"
    )
    return MemberSpec(name, data_type, dimension=dimension, description=description,
                      raw_default_data=raw)
