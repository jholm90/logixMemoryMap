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
    # Nested UDT support (James, 2026-08-20: "nested UDTs need to be
    # tested"). When set, `data_type` names another UDT and this is that
    # UDT's own member list -- both the definition side (_udt_members_xml,
    # a plain type-name reference, no recursion needed) and the
    # instance/Structure side (_udt_structure_body_xml, which does need to
    # recurse) use this to render the nested type correctly. Works combined
    # with `dimension` for "array of nested UDT" (a member that's an array
    # of another UDT's instances -- OQ-TAGOVERHEAD "nested array udts").
    nested_members: tuple["MemberSpec", ...] | None = None
    # An AOI instance nested as a UDT member (James, 2026-08-23, real
    # hand-built trial files after this was one of 5 real bugs behind a
    # batch of Build failures): renders differently from an ordinary
    # nested UDT member -- needs Radix="NullType" ExternalAccess=
    # "Read/Write" on the <Member> declaration, which a plain nested UDT
    # member does NOT carry (confirmed: axis_composite_udt_* already
    # passed real Build without them). See _udt_members_xml.
    is_aoi_member: bool = False
    # AOI Parameter Required/Visible flags (James, 2026-08-23: real calling-
    # instance semantics, not just cosmetic -- Required="true" means the
    # calling rung MUST have a tag wired to that parameter; Required="false"
    # + Visible="true" means the calling rung must have SOME value present
    # (tag or literal) but it's optional whether to wire one at all (real
    # corpus evidence, SJ_Gormley_20251112_r02.L5X's PTimer call omits 2 of
    # its 4 non-hidden Input params entirely); Required="false" +
    # Visible="false" means the parameter has nowhere to appear on the
    # calling rung at all -- storage-only, tag-browser-visible only. Only
    # meaningful for Input/Output params (_aoi_parameter_xml), ignored for
    # InOut (whose Required/Visible are always "true"/"true", not author-
    # chosen, per real corpus) and EnableIn/EnableOut (always "false"/
    # "false"). Defaults match this generator's own prior behavior (safe
    # hidden default) so existing callers are unaffected.
    required: bool = False
    visible: bool = False


_FLOAT_TYPES = {"REAL"}
_ATOMIC_TYPES = {"BOOL", "SINT", "INT", "DINT", "LINT", "REAL"}


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

    Nested-UDT members (m.nested_members set) recurse into their own
    <Structure>, and combined with m.dimension produce an array of nested
    Structures -- the same Array/Element/Structure shape already confirmed
    for a top-level array-of-UDT tag (tag_xml), just one level deeper.
    """
    parts = []
    for m in members:
        if m.nested_members is not None:
            inner = _udt_structure_body_xml(list(m.nested_members))
            if m.dimension:
                elements = "".join(
                    f'<Element Index="[{i}]"><Structure DataType="{m.data_type}">{inner}</Structure></Element>'
                    for i in range(m.dimension)
                )
                parts.append(f'<ArrayMember Name="{m.name}" DataType="{m.data_type}" '
                             f'Dimensions="{m.dimension}">{elements}</ArrayMember>')
            else:
                parts.append(f'<StructureMember Name="{m.name}" DataType="{m.data_type}">{inner}</StructureMember>')
        elif m.data_type == "STRING":
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
            parts.append(f"<!-- unsupported member {m.name}:{m.data_type} -->")
    return "".join(parts)


def collect_nested_datatypes(name: str, members: list["MemberSpec"], family: str = "NoFamily") -> str:
    """Every nested UDT referenced (transitively) by `members` needs its own
    <DataType> definition alongside the top one -- returns all of them,
    innermost-first, ready to concatenate into <DataTypes>.

    2026-08-23 fix (James, real Studio 5000 error after a generated AOI-
    nested-in-UDT file failed import): "Unable to create AOI definition
    'DriveAxisNestTest' because it collides with a UDT of the same name."
    An AOI member sets nested_members too (so the *instance/Structure*
    side, _udt_structure_body_xml, renders its storage correctly), but
    that used to also make this function emit a redundant plain <DataType>
    for it -- on top of its real <AddOnInstructionDefinition> (passed
    separately via build_l5x's extra_aoi_xml). AOI and UDT names share one
    namespace in Logix; two definitions with the same name is a hard
    import error, not a warning. Skip recursion for AOI members -- their
    type definition comes from extra_aoi_xml only, never from here.
    """
    parts = []
    for m in members:
        if m.nested_members is not None and not m.is_aoi_member:
            parts.append(collect_nested_datatypes(m.data_type, list(m.nested_members), family))
    parts.append(udt_xml(name, members, family))
    return "\n".join(parts)


def _string_tag_data_xml(max_len: int) -> str:
    """Standalone STRING-typed (built-in or custom-length) tag body --
    confirmed against real corpus (2026-08-20, multiple files e.g.
    RobbinsGrn_2026_05_13r00.L5X szInstruction): a top-level STRING tag
    exports as a *pair* of <Data> elements (Format="L5K" and Format="String"),
    NOT the <Data Format="Decorated"> every other tag type uses. A STRING
    *member inside a UDT* is different again (Decorated StructureMember,
    see _string_structure_member_xml) -- confirmed separately, real shape,
    not the same rule applied twice by assumption."""
    l5k_padding = "$00" * max_len
    return (
        f'<Data Format="L5K">\n<![CDATA[[0,\'{l5k_padding}\'\n\t\t]]]>\n</Data>\n'
        f'        <Data Format="String" Length="0">\n<![CDATA[\'\']]>\n</Data>'
    )


def string_array_tag_xml(name: str, count: int, max_len: int = 82, data_type: str = "STRING") -> str:
    """An ARRAY of STRING-typed elements (built-in, `data_type="STRING"`,
    or a custom string type by name) -- a genuinely different real shape
    from a scalar STRING tag, confirmed 2026-08-25 against two independent
    real corpus examples: samples/local/L5X_Samples/CMU_2025_10_14r00.L5X's
    CMU_PackNames tag (built-in, `DataType="STRING" Dimensions="5"`) and
    Gutchess_GreenLine_2026_06_04r00.L5X's PrintStrings tag (custom type,
    `DataType="SortString" Dimensions="160"`) -- both follow the identical
    shape, only the DataType name differs. Unlike a scalar STRING tag's
    L5K+String Data pair (`_string_tag_data_xml`), a STRING ARRAY exports
    as L5K+Decorated -- Decorated being an `<Array><Element><Structure
    DataType=X><DataValueMember Name="LEN".../><DataValueMember Name=
    "DATA".../></Structure></Element>...</Array>`, the same Decorated-
    array convention every other array type in this project already uses,
    NOT the scalar STRING's special pair. Real per-element data content
    varies (this generator emits empty/zero-length strings, matching a
    freshly-created array before any runtime value is written) --
    OQ-STRINGARRAY, never previously tested."""
    l5k_padding = "$00" * max_len
    l5k_elements = ",".join([f"[0,'{l5k_padding}'\n\t\t]"] * count)
    decorated_elements = "".join(
        f'<Element Index="[{i}]"><Structure DataType="{data_type}">'
        f'<DataValueMember Name="LEN" DataType="DINT" Radix="Decimal" Value="0"/>'
        f'<DataValueMember Name="DATA" DataType="{data_type}" Radix="ASCII"><![CDATA[]]></DataValueMember>'
        f"</Structure></Element>"
        for i in range(count)
    )
    return (
        f'      <Tag Name="{name}" TagType="Base" DataType="{data_type}" Dimensions="{count}"'
        f' Constant="false" ExternalAccess="Read/Write">\n'
        f'        <Data Format="L5K">\n<![CDATA[[{l5k_elements}]]]>\n</Data>\n'
        f'        <Data Format="Decorated"><Array DataType="{data_type}" Dimensions="{count}">'
        f"{decorated_elements}</Array></Data>\n"
        f"      </Tag>"
    )


def tag_xml(
    name: str, data_type: str, dimensions: tuple[int, ...] = (), radix: str = "Decimal",
    description: str | None = None, udt_members: list["MemberSpec"] | None = None,
    string_max_len: int | None = None, constant: bool = False,
) -> str:
    dims_attr = f' Dimensions="{" ".join(str(d) for d in dimensions)}"' if dimensions else ""
    desc_xml = f"\n        <Description><![CDATA[{description}]]></Description>" if description else ""
    constant_attr = "true" if constant else "false"

    # Real exports (2026-08-20): a UDT-typed Tag element carries no Radix
    # attribute at all -- only atomic-rooted tags (scalar or array) do.
    radix_attr = f' Radix="{radix}"' if udt_members is None and string_max_len is None else ""

    if string_max_len is not None:
        return (
            f'      <Tag Name="{name}" TagType="Base" DataType="{data_type}"'
            f' Constant="{constant_attr}" ExternalAccess="Read/Write">{desc_xml}\n'
            f'        {_string_tag_data_xml(string_max_len)}\n'
            f"      </Tag>"
        )

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
        f'{radix_attr} Constant="{constant_attr}" ExternalAccess="Read/Write">{desc_xml}\n'
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
            aoi_attrs = ' Radix="NullType" ExternalAccess="Read/Write"' if m.is_aoi_member else ""
            desc = _member_description_xml(m.description)
            parts.append(f'      <Member Name="{m.name}" DataType="{m.data_type}"{dim_attr}{aoi_attrs} Hidden="false">{desc}</Member>'
                         if desc else f'      <Member Name="{m.name}" DataType="{m.data_type}"{dim_attr}{aoi_attrs} Hidden="false"/>')
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
    # Real shape confirmed 2026-08-20, samples/local/SJ_Gormley_20251112_r02.L5X
    # (DataType Name="Long_String", DATA Dimension="128").
    return (
        f'    <DataType Name="{name}" Family="StringFamily" Class="User">\n'
        f"      <Members>\n"
        f'        <Member Name="LEN" DataType="DINT" Dimension="0" Radix="Decimal" Hidden="false" ExternalAccess="Read/Write"/>\n'
        f'        <Member Name="DATA" DataType="SINT" Dimension="{max_len}" Radix="ASCII" Hidden="false" ExternalAccess="Read/Write"/>\n'
        f"      </Members>\n"
        f"    </DataType>"
    )


def _aoi_default_data_xml(m: "MemberSpec") -> str:
    """DefaultData for an atomic Parameter/LocalTag. Nested-UDT/nested-AOI
    members need _aoi_nested_default_data_xml instead (Structure body, not
    a scalar DataValue)."""
    val = _default_value(m.data_type)
    radix = "Float" if m.data_type in _FLOAT_TYPES else "Decimal"
    return (
        f'<DefaultData Format="L5K"><![CDATA[{val}]]></DefaultData>'
        f'<DefaultData Format="Decorated">{_data_value_xml(m.data_type, radix)}</DefaultData>'
    )


def _aoi_array_default_data_xml(m: "MemberSpec") -> str:
    """DefaultData for a DIMENSIONED atomic Parameter/LocalTag (an array
    Input/Output param, or a non-InOut array LocalTag) -- real bug found
    2026-08-30 (James: aoi_array_param_def_only.L5X fails to import with
    XMLSrv_E_IMPORT_ABORTED_NO_CHANGES, even after the earlier Required/
    Visible fix). Real corpus check (SJ_Gormley_20251112_r02.L5X,
    TS_TrackSts AOI): every non-InOut Parameter that carries ExternalAccess
    ALSO carries <DefaultData> (WindowStart/WindowEnd/ConsecTest/ER/EM/
    StartBit/EndBit, all scalar) -- InOut params (BitArray, PkgSts) are the
    only ones that go bare with no DefaultData at all. The generator's own
    `default = "" if m.dimension else ...` rule conflated "is an array"
    with "is InOut" the same way the Required/Visible bug did -- BitArray
    happens to be both InOut AND dimensioned in every real example on
    file, so the array case was never actually tested independent of
    InOut. No real corpus example of an array Input/Output Parameter
    exists to confirm the array DefaultData's own internal shape, so this
    follows the same <Array>/<Element> convention this project's own
    _array_body_xml already uses for an ordinary array Tag's Data body
    (real shape, confirmed against BaillieLeitchField_Edger), and the same
    bracketed-list L5K convention _aoi_nested_default_data_xml already
    uses for a nested-UDT LocalTag's default -- both ASSUMED to generalize
    here, not independently confirmed for this exact combination."""
    val = _default_value(m.data_type)
    radix = "Float" if m.data_type in _FLOAT_TYPES else "Decimal"
    l5k_vals = ",".join([val] * m.dimension)
    array_body = _array_body_xml(m.data_type, m.dimension, radix=radix)
    return (
        f'<DefaultData Format="L5K"><![CDATA[[{l5k_vals}]]]></DefaultData>'
        f'<DefaultData Format="Decorated">{array_body}</DefaultData>'
    )


def _aoi_nested_default_data_xml(m: "MemberSpec") -> str:
    """DefaultData for a LocalTag whose type is a nested UDT/AOI -- real
    shape confirmed 2026-08-20 (James's Aoi_Nested.L5X, LocalTag
    "InReal_OutReal" of type InReal_OutReal): L5K is a positional value
    list `[1,val,val,...]` (leading 1 = EnableIn's real captured value, not
    modeled precisely here since it doesn't affect byte size -- 0 is fine),
    Decorated wraps a <Structure> the same way _udt_structure_body_xml does."""
    inner = _udt_structure_body_xml(list(m.nested_members))
    l5k_vals = ",".join(_default_value(nm.data_type) for nm in m.nested_members)
    return (
        f'<DefaultData Format="L5K"><![CDATA[[0,{l5k_vals}]]]></DefaultData>'
        f'<DefaultData Format="Decorated"><Structure DataType="{m.data_type}">{inner}</Structure></DefaultData>'
    )


def _aoi_parameter_xml(m: "MemberSpec", usage: str) -> str:
    # Real shape confirmed 2026-08-20 against James's own AOI templates
    # (AOI_Definition.L5X, AOI_Definition2.L5X, Aoi_Nested*.L5X, and the
    # InOut examples aoi_inOut_OneDint.L5X/aoi_inOut_OneString.L5X) --
    # superseded an earlier guess built off one different real AOI that
    # turned out wrong on several attributes: Required/Visible are
    # author-chosen per parameter (both true and false appear across
    # James's real files), not derivable from Usage, so "false"/"false" is
    # used here for Input/Output as a safe default matching most of his
    # examples. ExternalAccess is "Read/Write" for Input, "Read Only" for
    # Output/EnableIn/EnableOut -- confirmed across every one of his files,
    # not "None" (the earlier guess).
    if m.name in ("EnableIn", "EnableOut"):
        radix_attr = f' Radix="{"Float" if m.data_type in _FLOAT_TYPES else "Decimal"}"'
        return (
            f'<Parameter Name="{m.name}" TagType="Base" DataType="{m.data_type}"{radix_attr} Usage="{usage}" '
            f'Required="false" Visible="false" ExternalAccess="Read Only"/>'
        )

    if usage == "InOut":
        # Real shape confirmed 2026-08-20 (aoi_inOut_OneDint.L5X,
        # aoi_inOut_OneString.L5X): self-closed, no DefaultData, no
        # ExternalAccess at all, Required="true" Visible="true"
        # Constant="false" (not the false/false used for Input/Output).
        # Radix appears for an atomic type (DINT) but not for STRING --
        # matches the same "STRING never gets a bare Radix" rule seen
        # elsewhere in this file. Confirmed separately: an InOut param
        # carries no storage of its own -- the real instance Tag's
        # Structure body only ever contains EnableIn/EnableOut, InOut is
        # completely absent -- so aoi_xml() already excludes inout_params
        # from the returned storage_members list, unchanged by this fix.
        #
        # 2026-08-23 fix (James's real hand-built trial files, after 5
        # AXIS_CIP_DRIVE-InOut files all failed Build): STRING wasn't the
        # only non-atomic case -- AXIS_CIP_DRIVE is a predefined
        # STRUCTURE type too, and James's real, Studio-5000-confirmed
        # parameter for it is bare: `Usage="InOut" Required="true"
        # Visible="true"/>` -- no Radix, no Constant at all. The STRING
        # special case generalizes to "no atomic type, no Radix/Constant,"
        # not "no STRING specifically."
        is_atomic = m.data_type in _ATOMIC_TYPES
        radix_attr = f' Radix="{"Float" if m.data_type in _FLOAT_TYPES else "Decimal"}"' if is_atomic else ""
        constant_attr = ' Constant="false"' if is_atomic else ""
        return (
            f'<Parameter Name="{m.name}" TagType="Base" DataType="{m.data_type}"{radix_attr} Usage="InOut" '
            f'Required="true" Visible="true"{constant_attr}/>'
        )

    # Real bug fix, 2026-08-27: <Parameter>/<LocalTag> array size is a
    # "Dimensions" (PLURAL) attribute in real Rockwell exports -- was
    # "Dimension" (singular, correct only for a plain UDT <Member>, see
    # datatypes.py), which self-consistently matched the SAME bug in
    # parser/aoi.py's own reader. Confirmed against 271 real <Parameter>/
    # <LocalTag Dimensions="N"> elements in James's corpus, zero
    # counter-examples. Every previously-generated file with an
    # array-dimensioned AOI Parameter/LocalTag needs regenerating +
    # RE-CAPTURING -- the malformed attribute name almost certainly also
    # went unrecognized by Studio 5000's own importer on the prior
    # capture, meaning those "confirmed" numbers likely tested scalar
    # behavior, not the array behavior they were meant to.
    dim_attr = f' Dimensions="{m.dimension}"' if m.dimension else ""
    radix_attr = f' Radix="{"Float" if m.data_type in _FLOAT_TYPES else "Decimal"}"'
    external_access = "Read Only" if usage == "Output" else "Read/Write"
    if m.dimension and m.nested_members is None:
        default = _aoi_array_default_data_xml(m)
    elif m.dimension:
        default = ""  # nested-UDT array param -- genuinely unexplored, not this bug's scope
    else:
        default = _aoi_default_data_xml(m)
    # 2026-08-29 real-world bug report (James: "aoi_array_param_def_only
    # does not open"): this file used the false/false Required/Visible
    # default on a DIMENSIONED (array) Input Parameter. The only real
    # corpus evidence this project has for an array Parameter's Required/
    # Visible (LOG_HMIDisplay Dimensions="25", BitArray Dimensions="1024",
    # both InOut) is Required="true" Visible="true" -- already-confirmed
    # for InOut specifically (see the InOut branch above), but never
    # independently confirmed for Input/Output. Given a real file with
    # false/false on an array Input Parameter is now confirmed BROKEN
    # (doesn't open) and zero real evidence exists for false/false working
    # on any array Parameter regardless of Usage, forcing true/true here
    # is the best-supported fix available without a positive real Input/
    # Output-array counter-example -- flagged as ASSUMED/hypothesis-driven
    # in OPEN_QUESTIONS.md OQ-AOIARRAYDIMENSION, not silently treated as
    # fully confirmed.
    if m.dimension:
        required_attr = "true"
        visible_attr = "true"
    else:
        required_attr = "true" if m.required else "false"
        visible_attr = "true" if (m.required or m.visible) else "false"
    return (
        f'<Parameter Name="{m.name}" TagType="Base" DataType="{m.data_type}"{dim_attr} Usage="{usage}"'
        f'{radix_attr} Required="{required_attr}" Visible="{visible_attr}" '
        f'ExternalAccess="{external_access}">{default}</Parameter>'
    )


def _aoi_local_tag_xml(m: "MemberSpec") -> str:
    # See the matching comment in _aoi_parameter_xml -- same real
    # Dimension->Dimensions attribute-name fix, same reason.
    dim_attr = f' Dimensions="{m.dimension}"' if m.dimension else ""
    if m.nested_members is not None:
        # Real shape confirmed: a nested-UDT/nested-AOI LocalTag has no
        # Radix attribute at all (matches the same UDT-typed-tag rule).
        default = "" if m.dimension else _aoi_nested_default_data_xml(m)
        return f'<LocalTag Name="{m.name}" DataType="{m.data_type}"{dim_attr} ExternalAccess="None">{default}</LocalTag>'
    radix_attr = f' Radix="{"Float" if m.data_type in _FLOAT_TYPES else "Decimal"}"'
    default = "" if m.dimension else _aoi_default_data_xml(m)
    return (
        f'<LocalTag Name="{m.name}" DataType="{m.data_type}"{dim_attr}{radix_attr} '
        f'ExternalAccess="None">{default}</LocalTag>'
    )


# Static but well-formed, matches the shape of James's real AOI exports
# closely enough to import (these attributes don't affect byte size, only
# well-formedness) -- doesn't need to be live/unique per generated file.
_AOI_CREATED_DATE = "2026-08-20T12:00:00.000Z"


def aoi_xml(
    name: str,
    input_params: list["MemberSpec"] | None = None,
    output_params: list["MemberSpec"] | None = None,
    inout_params: list["MemberSpec"] | None = None,
    local_tags: list["MemberSpec"] | None = None,
) -> tuple[str, list["MemberSpec"]]:
    """AddOnInstructionDefinition + the "storage member list" for generating
    an instance tag of it. Real shape confirmed 2026-08-20 against James's
    own real AOI export templates (AOI_Definition.L5X, AOI_Definition2.L5X,
    Aoi_Nested*.L5X) after an earlier version of this function (built off a
    different real AOI) failed Studio 5000 import -- fixed several real
    discrepancies: AddOnInstructionDefinition needs Vendor/CreatedDate/
    CreatedBy/EditedDate/EditedBy attributes (the earlier version omitted
    them entirely); Parameter ExternalAccess is Read/Write (Input) or
    Read Only (Output), not "None"; a nested-UDT/AOI-typed LocalTag needs a
    Structure-shaped DefaultData, not the atomic DataValue every Parameter/
    LocalTag got before (this was silently wrong, not just cosmetically
    off). AOI-instance tags render exactly like UDT instances (confirmed
    2026-08-20 against 4 real production files, see PROJECT_PLAN.md Phase
    4c) -- InOut params carry no storage of their own (reference-only), so
    the returned storage list is EnableIn/EnableOut + input/output params +
    local tags, usable directly with tag_xml(udt_members=...) the same way
    a UDT instance is.
    """
    input_params = input_params or []
    output_params = output_params or []
    inout_params = inout_params or []
    local_tags = local_tags or []

    enable_in = MemberSpec("EnableIn", "BOOL")
    enable_out = MemberSpec("EnableOut", "BOOL")

    param_parts = [_aoi_parameter_xml(enable_in, "Input"), _aoi_parameter_xml(enable_out, "Output")]
    param_parts += [_aoi_parameter_xml(m, "Input") for m in input_params]
    param_parts += [_aoi_parameter_xml(m, "Output") for m in output_params]
    param_parts += [_aoi_parameter_xml(m, "InOut") for m in inout_params]

    local_parts = [_aoi_local_tag_xml(m) for m in local_tags]
    locals_xml = ("<LocalTags>\n" + "\n".join(local_parts) + "\n      </LocalTags>") if local_parts else "<LocalTags/>"

    definition = (
        f'    <AddOnInstructionDefinition Name="{name}" Revision="1.0" Vendor="LogixMemoryMap" '
        f'ExecutePrescan="false" ExecutePostscan="false" ExecuteEnableInFalse="false" '
        f'CreatedDate="{_AOI_CREATED_DATE}" CreatedBy="Generator" EditedDate="{_AOI_CREATED_DATE}" '
        f'EditedBy="Generator" SoftwareRevision="v35.05">\n'
        f'      <Parameters>\n' + "\n".join(param_parts) + "\n      </Parameters>\n"
        f'      {locals_xml}\n'
        f'      <Routines>\n'
        f'        <Routine Name="Logic" Type="RLL"/>\n'
        f'      </Routines>\n'
        f"    </AddOnInstructionDefinition>"
    )
    storage_members = [enable_in, enable_out, *input_params, *output_params, *local_tags]
    return definition, storage_members


def program_xml(name: str, tags_xml: str = "", rungs_xml_body: str = "") -> str:
    """A second/extra <Program> block, for build_l5x(extra_programs_xml=...).
    Same MainRoutine/RLL shape as the wrapper's own MainProgram. OQ-XPROGREF
    -- James, 2026-08-22: "add it to the next batch" (cross-program tag
    reference). Real Logix has no direct cross-program addressing syntax in
    logic (confirmed: no such pattern found anywhere in the real corpus,
    despite 47 real files including some with Public program tags) -- the
    real mechanism James described earlier is a Controller-scoped global
    tag with a same-named Local alias in each program that needs it, which
    is what this builder is for."""
    rungs = rungs_xml_body if rungs_xml_body.strip() else (
        '<Rung Number="0" Type="N"><Text><![CDATA[NOP();]]></Text></Rung>'
    )
    return (
        f'<Program Name="{name}" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" UseAsFolder="false">\n'
        f"<Tags>\n{tags_xml}\n</Tags>\n"
        f"<Routines>\n<Routine Name=\"MainRoutine\" Type=\"RLL\">\n<RLLContent>\n{rungs}\n</RLLContent>\n</Routine>\n</Routines>\n"
        f"</Program>"
    )


def rung_xml(number: int, instructions: str, comment: str | None = None) -> str:
    # Real exports always wrap rung Text in CDATA (2026-08-21: caught while
    # building the instruction sweep -- this was missing here, harmless so
    # far only because no rung text generated to date needed a literal '<',
    # but CMP's real syntax does e.g. CMP(A>B), and a future '<' would have
    # produced invalid XML without this).
    comment_xml = f"<Comment><![CDATA[{comment}]]></Comment>\n                " if comment else ""
    return (
        f'              <Rung Number="{number}" Type="N">\n'
        f"                {comment_xml}<Text><![CDATA[{instructions}]]></Text>\n"
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


def timer_tag_xml(name: str, preset: int = 1000) -> str:
    """Real shape confirmed 2026-08-21 (samples/local/SJ_Gormley_20251112_r02.L5X,
    IncisorOtfdBeltJogDwell): a TIMER tag, like STRING, uses the dual
    Format="L5K"/Format="Decorated" pair at the top level -- NOT the single
    Format="Decorated" every UDT/atomic tag gets. 5 real members (PRE/ACC
    DINT, EN/TT/DN BOOL) match this project's already-confirmed 12-byte
    TIMER constant (docs/MEMORY_MODEL.md)."""
    return (
        f'      <Tag Name="{name}" TagType="Base" DataType="TIMER" Constant="false" ExternalAccess="Read/Write">\n'
        f'        <Data Format="L5K"><![CDATA[[0,{preset},0]]]></Data>\n'
        f'        <Data Format="Decorated"><Structure DataType="TIMER">'
        f'<DataValueMember Name="PRE" DataType="DINT" Radix="Decimal" Value="{preset}" />'
        f'<DataValueMember Name="ACC" DataType="DINT" Radix="Decimal" Value="0" />'
        f'<DataValueMember Name="EN" DataType="BOOL" Value="0" />'
        f'<DataValueMember Name="TT" DataType="BOOL" Value="0" />'
        f'<DataValueMember Name="DN" DataType="BOOL" Value="0" /></Structure></Data>\n'
        f"      </Tag>"
    )


def counter_tag_xml(name: str, preset: int = 100) -> str:
    """Real shape confirmed 2026-08-21 (samples/local/SJ_Gormley_20251112_r02.L5X,
    LL_BlowoffCTR_PkgIFLL): same dual-format shape as TIMER, 7 real members
    (PRE/ACC DINT, CU/CD/DN/OV/UN BOOL)."""
    return (
        f'      <Tag Name="{name}" TagType="Base" DataType="COUNTER" Constant="false" ExternalAccess="Read/Write">\n'
        f'        <Data Format="L5K"><![CDATA[[0,{preset},0]]]></Data>\n'
        f'        <Data Format="Decorated"><Structure DataType="COUNTER">'
        f'<DataValueMember Name="PRE" DataType="DINT" Radix="Decimal" Value="{preset}" />'
        f'<DataValueMember Name="ACC" DataType="DINT" Radix="Decimal" Value="0" />'
        f'<DataValueMember Name="CU" DataType="BOOL" Value="0" />'
        f'<DataValueMember Name="CD" DataType="BOOL" Value="0" />'
        f'<DataValueMember Name="DN" DataType="BOOL" Value="0" />'
        f'<DataValueMember Name="OV" DataType="BOOL" Value="0" />'
        f'<DataValueMember Name="UN" DataType="BOOL" Value="0" /></Structure></Data>\n'
        f"      </Tag>"
    )


def control_tag_xml(name: str, length: int = 10, position: int = 9) -> str:
    """CONTROL tag -- real shape confirmed 2026-08-24
    (samples/local/BAI10048_TrimmerTally_20250704.L5X, srtControl): same
    dual-format shape as TIMER/COUNTER, 10 real members (LEN/POS DINT,
    EN/EU/DN/EM/ER/UL/IN/FD BOOL) -- matches the already-confirmed 12-byte
    CONTROL predefined-structure constant. Needed for the file/array
    instructions (FFL/FFU/BSL/BSR/SRT/AVE/FAL/FSC) that all take a CONTROL
    tag as one of their operands, per real corpus examples."""
    return (
        f'      <Tag Name="{name}" TagType="Base" DataType="CONTROL" Constant="false" ExternalAccess="Read/Write">\n'
        f'        <Data Format="L5K"><![CDATA[[-1610612736,{length},{position}]]]></Data>\n'
        f'        <Data Format="Decorated"><Structure DataType="CONTROL">'
        f'<DataValueMember Name="LEN" DataType="DINT" Radix="Decimal" Value="{length}"/>'
        f'<DataValueMember Name="POS" DataType="DINT" Radix="Decimal" Value="{position}"/>'
        f'<DataValueMember Name="EN" DataType="BOOL" Value="1"/>'
        f'<DataValueMember Name="EU" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="DN" DataType="BOOL" Value="1"/>'
        f'<DataValueMember Name="EM" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="ER" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="UL" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="IN" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="FD" DataType="BOOL" Value="0"/>'
        f'</Structure></Data>\n'
        f"      </Tag>"
    )


def message_tag_xml(name: str, local_element: str, destination_tag: str) -> str:
    """MESSAGE tag -- real shape confirmed 2026-08-24
    (samples/local/BaillieLeitchField_Edger_20260812_r00.L5X,
    MESSAGE_Alarms): a single self-closed <MessageParameters> element, no
    Structure/DataValueMember body at all (much simpler than TIMER/COUNTER/
    CONTROL) -- a "CIP Generic" get-attribute-list message, real attribute
    set copied verbatim except LocalElement/DestinationTag, which point at
    plain tags this generator declares itself rather than the real file's
    own array tags. MESSAGE has no predefined_structures entry in
    memory_model.yaml (completely unmodeled byte size) -- callers must use
    write_sample_unmodeled, not write_sample, for any file containing this."""
    return (
        f'      <Tag Name="{name}" TagType="Base" DataType="MESSAGE" ExternalAccess="Read/Write">\n'
        f'        <Data Format="Message">\n'
        f'          <MessageParameters MessageType="CIP Generic" RequestedLength="4" ConnectedFlag="2" '
        f'ConnectionPath="THIS" CommTypeCode="0" ServiceCode="16#0003" ObjectType="16#00b1" '
        f'TargetObject="2" AttributeNumber="16#0000" LocalIndex="0" LocalElement="{local_element}" '
        f'DestinationTag="{destination_tag}" LargePacketUsage="false"/>\n'
        f'        </Data>\n'
        f"      </Tag>"
    )


# Real CAM element rows -- distinct from CAM_PROFILE (see
# _CAM_PROFILE_L5K_ROWS above). Confirmed 2026-08-24
# (samples/local/L5X_Samples/RobbinsGrn_2026_05_13r00.L5X, NewCI2Cam): a
# CAM array tag's Decorated shape is fully visible (no hidden fields the
# way CAM_PROFILE has) -- just Master(REAL)/Slave(REAL)/SegmentType(DINT)
# per element, matching every L5K row exactly. Genuinely unmodeled in
# memory_model.yaml still (no real Capacity data captured yet) -- see
# docs/OPEN_QUESTIONS.md for the new open question this creates.
def cam_tag_xml(name: str, count: int) -> str:
    l5k_rows = ["[0.0,0.0,1]"] + ["[200.0,100.0,0]"] * (count - 1) if count else []
    l5k_body = "[" + ",".join(l5k_rows) + "]"
    elements = []
    for i in range(count):
        master, slave, seg = ("0.0", "0.0", "1") if i == 0 else ("200.0", "100.0", "0")
        elements.append(
            f'<Element Index="[{i}]"><Structure DataType="CAM">'
            f'<DataValueMember Name="Master" DataType="REAL" Radix="Float" Value="{master}"/>'
            f'<DataValueMember Name="Slave" DataType="REAL" Radix="Float" Value="{slave}"/>'
            f'<DataValueMember Name="SegmentType" DataType="DINT" Radix="Decimal" Value="{seg}"/>'
            f"</Structure></Element>"
        )
    return (
        f'      <Tag Name="{name}" TagType="Base" DataType="CAM" Dimensions="{count}" '
        f'Constant="false" ExternalAccess="Read/Write">\n'
        f'        <Data Format="L5K"><![CDATA[{l5k_body}]]></Data>\n'
        f'        <Data Format="Decorated"><Array DataType="CAM" Dimensions="{count}">'
        + "".join(elements) +
        f"</Array></Data>\n"
        f"      </Tag>"
    )


def program_tag_xml(name: str, data_type: str, usage: str | None = None) -> str:
    """Program-scoped (Program/Tags, not Controller/Tags) atomic tag. Real
    shape confirmed 2026-08-22 (samples/local/SJ_Gormley_20251112_r02.L5X,
    PC366_BitPos/DLugNum): a Program-scoped tag -- Local (no Usage attribute)
    or Public (Usage="Public") alike -- uses the dual Format="L5K"/
    Format="Decorated" pair, unlike a Controller-scoped atomic tag which
    gets Decorated only (see tag_xml). The dual format is a program-scope
    convention, not something specific to Usage="Public" -- confirmed by
    checking a same-file Local-scope tag (DLugNum, no Usage attribute) shows
    the identical dual-Data shape. OQ-TAGSCOPE."""
    usage_attr = f' Usage="{usage}"' if usage else ""
    val = _default_value(data_type)
    radix = "Float" if data_type in _FLOAT_TYPES else "Decimal"
    return (
        f'      <Tag Name="{name}" TagType="Base" DataType="{data_type}" Radix="{radix}"{usage_attr} '
        f'Constant="false" ExternalAccess="Read/Write">\n'
        f'        <Data Format="L5K"><![CDATA[{val}]]></Data>\n'
        f'        <Data Format="Decorated">{_data_value_xml(data_type, radix)}</Data>\n'
        f"      </Tag>"
    )


def alias_tag_xml(name: str, alias_for: str, radix: str = "Decimal") -> str:
    """Alias tag -- real shape confirmed 2026-08-20 (multiple real corpus
    files, e.g. samples/local/BAI10048_TrimmerTally_20250704.L5X): self-
    closed, no Data element at all, just AliasFor pointing at the real
    target tag's path. OQ-ALIASSIZE."""
    return f'      <Tag Name="{name}" TagType="Alias" Radix="{radix}" AliasFor="{alias_for}" ExternalAccess="Read/Write"/>'


def motion_instruction_tag_xml(name: str) -> str:
    """MOTION_INSTRUCTION tag -- real shape confirmed 2026-08-22
    (samples/local/BAI10048_TrimmerTally_20250704.L5X, AxisMotionControlMAG,
    a real MAG/MAH-style motion instruction backing tag). Same dual
    Format="L5K"/Format="Decorated" convention as TIMER/COUNTER. Unlike
    those, this one's 16 named Decorated members (FLAGS DINT, 10 status
    BOOLs, ERR INT, STATUS/STATE/EXERR SINT, SEGMENT DINT) are NOT
    necessarily independent storage -- the BOOLs almost certainly alias
    into bits of FLAGS the same way TIMER's EN/TT/DN do, per real Rockwell
    convention. Treat MOTION_INSTRUCTION as an opaque predefined-structure
    constant (like AXIS_CIP_DRIVE/TIMER/COUNTER) once real Capacity data
    comes in -- don't naively sum member byte sizes. OQ-PREDEFINED."""
    return (
        f'      <Tag Name="{name}" TagType="Base" DataType="MOTION_INSTRUCTION" Constant="false" ExternalAccess="Read/Write">\n'
        f'        <Data Format="L5K"><![CDATA[[0,0,0,0,0,0,0,0,0]]]></Data>\n'
        f'        <Data Format="Decorated"><Structure DataType="MOTION_INSTRUCTION">'
        f'<DataValueMember Name="FLAGS" DataType="DINT" Radix="Decimal" Value="0"/>'
        f'<DataValueMember Name="EN" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="DN" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="ER" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="PC" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="IP" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="AC" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="ACCEL" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="DECEL" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="TrackingMaster" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="CalculatedDataAvailable" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="ERR" DataType="INT" Radix="Decimal" Value="0"/>'
        f'<DataValueMember Name="STATUS" DataType="SINT" Radix="Decimal" Value="0"/>'
        f'<DataValueMember Name="STATE" DataType="SINT" Radix="Decimal" Value="0"/>'
        f'<DataValueMember Name="SEGMENT" DataType="DINT" Radix="Decimal" Value="0"/>'
        f'<DataValueMember Name="EXERR" DataType="SINT" Radix="Decimal" Value="0"/>'
        f'</Structure></Data>\n'
        f"      </Tag>"
    )


# Real CAM_PROFILE element rows, captured verbatim 2026-08-22 from
# samples/local/L5X_Samples/CMU_2025_10_14r00.L5X (HoldCamProfile, a real
# 20-element array). Deliberately NOT synthesized: the visible Decorated
# shape exposes only one named member (Status, DINT) per element, but the
# real L5K row for each element carries 14 numeric fields -- confirming
# James's "voodoo... hides stuff not visible in the tag browser" (2026-08-22).
# There's no way to reconstruct the meaning of the other 13 fields from the
# L5X alone, so rather than invent plausible-looking values (risking a
# subtly-invalid encoding that fails import), every generated CAM_PROFILE
# element reuses one of these 20 real rows cyclically. CAM_PROFILE's real
# per-element byte cost can only come from empirical Capacity measurement,
# never from counting visible structure members. OQ-PREDEFINED.
_CAM_PROFILE_L5K_ROWS = [
    "[2,0,0,0,0,1,0,0,1072693248,0,-1080956027,515396076,1059086925,-755914243]",
    "[2,1078198272,0,1077149696,0,1,0,0,1070176665,-1717986918,-1083933983,1202590845,1055091462,-418679770]",
    "[2,1079574528,0,1077477376,0,1,0,0,0,0,0,0,0,0]",
    "[0,1079574528,0,1077477376,0,1,0,0,0,0,0,0,0,0]",
]
_CAM_PROFILE_STATUS_VALUES = ["2", "2", "2", "0"]


def cam_profile_tag_xml(name: str, count: int) -> str:
    """Array-of-CAM_PROFILE tag, `count` elements, built from real captured
    rows cycled to fill any size -- see _CAM_PROFILE_L5K_ROWS docstring."""
    l5k_rows = [_CAM_PROFILE_L5K_ROWS[i % len(_CAM_PROFILE_L5K_ROWS)] for i in range(count)]
    l5k_body = "[" + ",".join(l5k_rows) + "]"
    elements = []
    for i in range(count):
        status = _CAM_PROFILE_STATUS_VALUES[i % len(_CAM_PROFILE_STATUS_VALUES)]
        elements.append(
            f'<Element Index="[{i}]"><Structure DataType="CAM_PROFILE">'
            f'<DataValueMember Name="Status" DataType="DINT" Radix="Decimal" Value="{status}"/>'
            f"</Structure></Element>"
        )
    return (
        f'      <Tag Name="{name}" TagType="Base" DataType="CAM_PROFILE" Dimensions="{count}" '
        f'Constant="false" ExternalAccess="Read/Write">\n'
        f'        <Data Format="L5K"><![CDATA[{l5k_body}]]></Data>\n'
        f'        <Data Format="Decorated"><Array DataType="CAM_PROFILE" Dimensions="{count}">'
        + "".join(elements) +
        f"</Array></Data>\n"
        f"      </Tag>"
    )


# ---------------------------------------------------------------------------
# I/O Module builders (OQ series pending, docs/IO_MODULES.md). Three real,
# structurally distinct patterns confirmed against the corpus 2026-08-22 --
# module sizing is NOT one-size-fits-all, exactly James's caution ("same
# catalog Phoenix rack with 2 input cards or 30... be careful looking at the
# data sizes in the l5x module properties"):
#
#   1. Catalog-fixed backplane module (e.g. 1756-IB16): its own
#      <Communications><Connections><Connection><InputTag> with a real
#      AOP-defined Structure (AB:1756_DI:I:0 etc) -- size is fully
#      determined by CatalogNumber, same every time.
#   2. Point I/O rack member behind a 1734-AENT/AENTR adapter: NO
#      independent connection at all -- <RackConnection><InAliasTag/></
#      RackConnection>, rolled into the adapter's own combined rack-image
#      connection instead. Sizing has to walk adapter+members together,
#      not module-by-module.
#   3. Generic/no-EDS Ethernet module (CatalogNumber="ETHERNET-MODULE" --
#      real corpus examples include Balluff/IFM IO-Link masters and
#      Phoenix bus couplers, confirmed 2026-08-22): size is NOT
#      catalog-derived at all, it's the explicit PrimCxnInputSize/
#      PrimCxnOutputSize attributes on <Communications>, chosen per-
#      instance when the module was added in Studio 5000 -- the same
#      catalog number can and does appear with wildly different sizes.
#      Confirmed the Structure DataType name literally encodes the byte
#      count (AB:ETHERNET_MODULE_SINT_{n}Bytes:{I,O}:0).
# ---------------------------------------------------------------------------


def module_1756_digital_input_xml(name: str, slot: int = 1, parent_port_id: int = 1) -> str:
    """Real shape confirmed 2026-08-22 (samples/local/L5X_Samples/
    RobbinsGrn_2026_05_13r00.L5X, DC_Input): 1756-IB16, catalog-fixed AOP
    structure, ConfigSize=24 (10 named filter/COS members), Input
    Connection with a Fault+Data DINT pair (8 bytes). Pattern 1 above."""
    return (
        f'<Module Name="{name}" CatalogNumber="1756-IB16" Vendor="1" ProductType="7" ProductCode="11" '
        f'Major="2" Minor="5" ParentModule="Local" ParentModPortId="{parent_port_id}" Inhibited="false" MajorFault="false">\n'
        f'<EKey State="CompatibleModule"/>\n'
        f'<Ports><Port Id="1" Address="{slot}" Type="ICP" Upstream="true"/></Ports>\n'
        f'<Communications CommMethod="536870913">\n'
        f'<ConfigTag ConfigSize="24" ExternalAccess="Read/Write">\n'
        f'<Data Format="L5K"><![CDATA[[28,16,1,0,0,0,1,1,1,1,0,0,0,0,65535,65535]]]></Data>\n'
        f'<Data Format="Decorated"><Structure DataType="AB:1756_DI:C:0">'
        f'<DataValueMember Name="DiagCOSDisable" DataType="BOOL" Value="0"/>'
        f'<DataValueMember Name="FilterOffOn_0_7" DataType="SINT" Radix="Decimal" Value="1"/>'
        f'<DataValueMember Name="FilterOnOff_0_7" DataType="SINT" Radix="Decimal" Value="1"/>'
        f'<DataValueMember Name="FilterOffOn_8_15" DataType="SINT" Radix="Decimal" Value="1"/>'
        f'<DataValueMember Name="FilterOnOff_8_15" DataType="SINT" Radix="Decimal" Value="1"/>'
        f'<DataValueMember Name="FilterOffOn_16_23" DataType="SINT" Radix="Decimal" Value="0"/>'
        f'<DataValueMember Name="FilterOnOff_16_23" DataType="SINT" Radix="Decimal" Value="0"/>'
        f'<DataValueMember Name="FilterOffOn_24_31" DataType="SINT" Radix="Decimal" Value="0"/>'
        f'<DataValueMember Name="FilterOnOff_24_31" DataType="SINT" Radix="Decimal" Value="0"/>'
        f'<DataValueMember Name="COSOnOffEn" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_1111_1111_1111_1111"/>'
        f'<DataValueMember Name="COSOffOnEn" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_1111_1111_1111_1111"/>'
        f'</Structure></Data>\n'
        f'</ConfigTag>\n'
        f'<Connections><Connection Name="StandardInput" RPI="10000" Type="Input" EventID="0" '
        f'ProgrammaticallySendEventTrigger="false">\n'
        f'<InputTag ExternalAccess="Read/Write"><Data Format="Decorated"><Structure DataType="AB:1756_DI:I:0">'
        f'<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>'
        f'<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>'
        f'</Structure></Data></InputTag>\n'
        f'</Connection></Connections>\n'
        f'</Communications>\n'
        f"</Module>"
    )


def module_generic_ethernet_xml(name: str, ip_address: str, input_bytes: int, output_bytes: int) -> str:
    """Real shape confirmed 2026-08-22 (samples/local/L5X_Samples/
    Emporium_2025_05_28r01.L5X, IFM_LugLoader1 -- a Balluff/IFM IO-Link
    master added as a generic module, no vendor-specific EDS). Pattern 3
    above: CatalogNumber="ETHERNET-MODULE" is shared by every such device
    regardless of what it physically is -- real per-instance size comes
    ONLY from PrimCxnInputSize/PrimCxnOutputSize, and the Structure
    DataType name literally encodes the configured byte count
    (AB:ETHERNET_MODULE_SINT_{n}Bytes:{I,O}:0). Exactly the case James
    flagged: same catalog, real size varies per instance -- this builder
    exists specifically to generate several same-catalog files at
    different input_bytes/output_bytes and prove the sizing engine can't
    use a catalog lookup table for this class of module."""
    def _sint_array(n: int) -> str:
        return "".join(f'<Element Index="[{i}]" Value="0"/>' for i in range(n))

    return (
        f'<Module Name="{name}" CatalogNumber="ETHERNET-MODULE" Vendor="1" ProductType="0" ProductCode="18" '
        f'Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">\n'
        f'<EKey State="Disabled"/>\n'
        f'<Ports><Port Id="2" Address="{ip_address}" Type="Ethernet" Upstream="true"/></Ports>\n'
        f'<Communications CommMethod="536870916" PrimCxnInputSize="{input_bytes}" PrimCxnOutputSize="{output_bytes}">\n'
        f'<ConfigTag ConfigSize="0" ExternalAccess="Read/Write">\n'
        f'<Data Format="L5K"><![CDATA[[4,1,[0,0]]]]></Data>\n'
        f'<Data Format="Decorated"><Structure DataType="AB:ETHERNET_MODULE:C:0">'
        f'<ArrayMember Name="Data" DataType="SINT" Dimensions="0" Radix="Hex"></ArrayMember>'
        f'</Structure></Data>\n'
        f'</ConfigTag>\n'
        f'<Connections><Connection Name="Standard" RPI="20000" Type="Input" EventID="0" '
        f'ProgrammaticallySendEventTrigger="false" Unicast="true">\n'
        f'<InputTag ExternalAccess="Read/Write"><Data Format="Decorated">'
        f'<Structure DataType="AB:ETHERNET_MODULE_SINT_{input_bytes}Bytes:I:0">'
        f'<ArrayMember Name="Data" DataType="SINT" Dimensions="{input_bytes}" Radix="Decimal">'
        f'{_sint_array(input_bytes)}</ArrayMember></Structure></Data></InputTag>\n'
        f'<Data Format="L5K"><![CDATA[[[0,{output_bytes},0,0,0,0,0,0]]]]></Data>\n'
        f'<Data Format="Decorated"><Structure DataType="AB:ETHERNET_MODULE_SINT_{output_bytes}Bytes:O:0">'
        f'<ArrayMember Name="Data" DataType="SINT" Dimensions="{output_bytes}" Radix="Decimal">'
        f'{_sint_array(output_bytes)}</ArrayMember></Structure></Data>\n'
        f'</Connection></Connections>\n'
        f'</Communications>\n'
        f"</Module>"
    )



def task_xml(task_name: str, program_name: str, task_type: str = "CONTINUOUS",
             priority: int = 10, watchdog: int = 500,
             event_trigger: str | None = None, event_tag: str | None = None) -> str:
    """A second/extra <Task> block (with its own <ScheduledPrograms>), for
    build_l5x(extra_tasks_xml=...). Real shape matches the wrapper's own
    MainTask element exactly, just parametrized. Only CONTINUOUS Type is
    used by callers today -- real Logix only allows ONE Continuous task per
    controller, so a second Task under test must be Type="Periodic" (with a
    Rate attribute) to actually import; callers pass task_type explicitly
    for that reason rather than defaulting silently.

    Type="EVENT" (event_trigger set) mirrors the real corpus shape found in
    SJ_Gormley_20251112_r02.L5X/Sorter1_20260722r00.L5X: a Rate attribute
    (same as Periodic), DisableUpdateOutputs="true" (real EVENT tasks always
    carry this, unlike Periodic/Continuous's "false"), and a child
    <EventInfo EventTrigger="..."/> element -- either "EVENT Instruction
    Only" (no EventTag) or "Axis Watch" (EventTag pointing at a real
    AXIS_CIP_DRIVE/AXIS_VIRTUAL tag, confirmed real in the Gormley corpus)."""
    rate_attr = ' Rate="10"' if task_type in ("PERIODIC", "EVENT") else ""
    disable_outputs = "true" if task_type == "EVENT" else "false"
    event_tag_attr = f' EventTag="{event_tag}"' if event_tag else ""
    event_info_xml = (
        f'<EventInfo EventTrigger="{event_trigger}"{event_tag_attr} EnableTimeout="false"/>\n'
        if event_trigger else ""
    )
    return (
        f'<Task Name="{task_name}" Type="{task_type}"{rate_attr} Priority="{priority}" '
        f'Watchdog="{watchdog}" DisableUpdateOutputs="{disable_outputs}" InhibitTask="false">\n'
        f'{event_info_xml}'
        f'<ScheduledPrograms>\n<ScheduledProgram Name="{program_name}"/>\n</ScheduledPrograms>\n'
        f"</Task>"
    )
