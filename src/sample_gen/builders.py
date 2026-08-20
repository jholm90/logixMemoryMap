"""Composable L5X fragment builders for the sample generator (James,
2026-08-20: "the l5x generator application where you make up the l5x files
based on things you want to test -- UDT size, comment length for bits or
rungs etc.").

BOOL-run handling in udt_xml() matches the packing rule confirmed against
real Logix Designer behavior 2026-08-20 (see docs/OPEN_QUESTIONS.md
OQ-ALIGN, docs/MEMORY_MODEL.md UDT packing): consecutive BOOL members share
one hidden backing SINT (wrapping to a new one every 8 bits), but a
non-BOOL member breaks the run and the next BOOL(s) get a fresh backing
SINT. Generating that exact shape means samples this tool produces are
genuinely representative of what Logix Designer itself would export, not
a simplified stand-in.
"""

from __future__ import annotations

from dataclasses import dataclass

BOOL_BITS_PER_BACKING_SINT = 8


@dataclass(frozen=True)
class MemberSpec:
    name: str
    data_type: str
    dimension: int = 0
    description: str | None = None


_FLOAT_TYPES = {"REAL"}


def _default_value(data_type: str) -> str:
    return "0.0" if data_type in _FLOAT_TYPES else "0"


def _data_value_xml(data_type: str, radix: str = "Decimal") -> str:
    return f'<DataValue DataType="{data_type}" Radix="{radix}" Value="{_default_value(data_type)}" />'


def _array_body_xml(data_type: str, count: int, radix: str | None = "Decimal", element_fn=None) -> str:
    """element_fn(i) -> inner XML for one <Element>, defaults to a plain Value attr
    (atomic element type). Real shape confirmed against a real export
    (BaillieLeitchField_Edger, Alarms_Edger array) 2026-08-20 -- including
    that an array-of-UDT has no Radix attribute at all (radix=None), unlike
    an array-of-atomic which does."""
    if element_fn is None:
        elements = "".join(f'<Element Index="[{i}]" Value="{_default_value(data_type)}" />' for i in range(count))
    else:
        elements = "".join(f'<Element Index="[{i}]">{element_fn(i)}</Element>' for i in range(count))
    radix_attr = f' Radix="{radix}"' if radix else ""
    return f'<Array DataType="{data_type}" Dimensions="{count}"{radix_attr}>{elements}</Array>'


def _string_structure_member_xml(name: str) -> str:
    return (
        f'<StructureMember Name="{name}" DataType="STRING">'
        f'<DataValueMember Name="LEN" DataType="DINT" Radix="Decimal" Value="0" />'
        f'<DataValueMember Name="DATA" DataType="STRING" Radix="ASCII"></DataValueMember>'
        f"</StructureMember>"
    )


def _udt_structure_body_xml(members: list["MemberSpec"]) -> str:
    """Tag-instance <Structure> body for a UDT -- confirmed against a real
    export (Alarms_SE) 2026-08-20: members appear under their LOGICAL
    name/type (e.g. a BOOL member as a plain DataValueMember), with no trace
    of the hidden-SINT/BIT-alias representation that's purely a <DataType>
    Members-list authoring detail. Much simpler than the definition side.
    Nested UDT-typed members aren't supported yet (no generator CLI syntax
    for authoring one), so they're skipped with a comment rather than
    silently emitting something wrong.
    """
    parts = []
    for m in members:
        if m.data_type == "STRING":
            parts.append(_string_structure_member_xml(m.name))
        elif m.dimension:
            parts.append(f'<ArrayMember Name="{m.name}" DataType="{m.data_type}" '
                         f'Dimensions="{m.dimension}" Radix="Decimal">' +
                         "".join(f'<Element Index="[{i}]" Value="{_default_value(m.data_type)}" />'
                                 for i in range(m.dimension)) +
                         "</ArrayMember>")
        elif m.data_type in ("SINT", "INT", "DINT", "LINT", "REAL", "BOOL"):
            parts.append(f'<DataValueMember Name="{m.name}" DataType="{m.data_type}" '
                         f'Value="{_default_value(m.data_type)}" />')
        else:
            parts.append(f"<!-- nested UDT member {m.name}:{m.data_type} not yet supported by the generator -->")
    return "".join(parts)


def tag_xml(
    name: str, data_type: str, dimensions: tuple[int, ...] = (), radix: str = "Decimal",
    description: str | None = None, udt_members: list["MemberSpec"] | None = None,
) -> str:
    dims_attr = f' Dimensions="{" ".join(str(d) for d in dimensions)}"' if dimensions else ""
    desc_xml = f"\n        <Description><![CDATA[{description}]]></Description>" if description else ""

    # Real exports (2026-08-20): a UDT-typed Tag element carries no Radix
    # attribute at all -- only atomic-rooted tags (scalar or array) do.
    radix_attr = f' Radix="{radix}"' if udt_members is None else ""

    if udt_members is not None:
        structure_body = f'<Structure DataType="{data_type}">{_udt_structure_body_xml(udt_members)}</Structure>'
        data_body = (
            _array_body_xml(data_type, dimensions[0], radix=None, element_fn=lambda i: structure_body)
            if dimensions else structure_body
        )
    elif dimensions:
        data_body = _array_body_xml(data_type, dimensions[0], radix)
    else:
        data_body = _data_value_xml(data_type, radix)

    return (
        f'      <Tag Name="{name}" TagType="Base" DataType="{data_type}"{dims_attr}'
        f'{radix_attr} Constant="false" ExternalAccess="Read/Write">{desc_xml}\n'
        f'        <Data Format="Decorated">{data_body}</Data>\n'
        f"      </Tag>"
    )


def tags_xml(specs: list[tuple[str, str] | tuple[str, str, tuple[int, ...]]]) -> str:
    tags = []
    for spec in specs:
        name, dt = spec[0], spec[1]
        dims = spec[2] if len(spec) > 2 else ()
        tags.append(tag_xml(name, dt, dims))
    return "\n".join(tags)


def _member_description_xml(description: str | None) -> str:
    return f"<Description><![CDATA[{description}]]></Description>" if description else ""


def _udt_members_xml(members: list[MemberSpec]) -> str:
    parts: list[str] = []
    hidden_index = 0
    i = 0
    while i < len(members):
        m = members[i]
        if m.data_type != "BOOL":
            dim_attr = f' Dimension="{m.dimension}"' if m.dimension else ' Dimension="0"'
            desc = _member_description_xml(m.description)
            parts.append(f'      <Member Name="{m.name}" DataType="{m.data_type}"{dim_attr} Hidden="false">{desc}</Member>'
                         if desc else f'      <Member Name="{m.name}" DataType="{m.data_type}"{dim_attr} Hidden="false"/>')
            i += 1
            continue

        # Consume a run of consecutive BOOL members, splitting every 8 bits.
        run = []
        while i < len(members) and members[i].data_type == "BOOL":
            run.append(members[i])
            i += 1
        for chunk_start in range(0, len(run), BOOL_BITS_PER_BACKING_SINT):
            chunk = run[chunk_start:chunk_start + BOOL_BITS_PER_BACKING_SINT]
            hidden_name = f"ZZZZZZZZZZBoolMember{hidden_index:02d}"
            hidden_index += 1
            parts.append(f'      <Member Name="{hidden_name}" DataType="SINT" Dimension="0" Hidden="true"/>')
            for bit_num, bool_member in enumerate(chunk):
                desc = _member_description_xml(bool_member.description)
                tag = (
                    f'      <Member Name="{bool_member.name}" DataType="BIT" Dimension="0" '
                    f'Hidden="false" Target="{hidden_name}" BitNumber="{bit_num}">{desc}</Member>'
                    if desc else
                    f'      <Member Name="{bool_member.name}" DataType="BIT" Dimension="0" '
                    f'Hidden="false" Target="{hidden_name}" BitNumber="{bit_num}"/>'
                )
                parts.append(tag)
    return "\n".join(parts)


def udt_xml(name: str, members: list[MemberSpec], family: str = "NoFamily",
            description: str | None = None) -> str:
    members_xml = _udt_members_xml(members)
    # Real exports (2026-08-20, samples/local/SJ_Gormley_20251112_r02.L5X):
    # a DataType-level Description sits right after the opening tag, before
    # Members -- same CDATA shape as a Tag's Description.
    desc_xml = f"<Description><![CDATA[{description}]]></Description>\n      " if description else ""
    return (
        f'    <DataType Name="{name}" Family="{family}" Class="User">\n'
        f"      {desc_xml}<Members>\n{members_xml}\n      </Members>\n"
        f"    </DataType>"
    )


def custom_string_type_xml(name: str, max_len: int) -> str:
    return (
        f'    <DataType Name="{name}" Family="StringFamily" Class="User">\n'
        f"      <Members>\n"
        f'        <Member Name="LEN" DataType="DINT" Dimension="0" Hidden="false"/>\n'
        f'        <Member Name="DATA" DataType="SINT" Dimension="{max_len}" Hidden="false" Radix="ASCII"/>\n'
        f"      </Members>\n"
        f"    </DataType>"
    )


def rung_xml(number: int, instructions: str, comment: str | None = None) -> str:
    comment_xml = f"<Comment><![CDATA[{comment}]]></Comment>\n                " if comment else ""
    return (
        f'              <Rung Number="{number}" Type="N">\n'
        f"                {comment_xml}<Text>{instructions}</Text>\n"
        f"              </Rung>"
    )


def rungs_xml(count: int, instructions_fn, comment_fn=None) -> str:
    """instructions_fn(i) -> instruction text for rung i; comment_fn(i) -> comment
    text or None. Both take the rung index so callers can vary per rung if needed."""
    rungs = []
    for i in range(count):
        comment = comment_fn(i) if comment_fn else None
        rungs.append(rung_xml(i, instructions_fn(i), comment))
    return "\n".join(rungs)
