"""STRING closure batch (James, 2026-08-25): "I want strings as a whole
closed. No more open questions or unknowns... Be sure you know the array
of sints can be used in copy instructions as well as the Len tag elements"
and (interrupt) "Be sure you know moving 'constants' into strings and
custom strings for the L8 and 5069 processors."

Closes the specific threads still open after the nearest-8 custom-string
padding fix (see memory_model.yaml's string: block for the full derivation
-- 9/9 real maxlen points now fit exactly):

  A. group_typename_length -- a genuinely NEW residual found while
     verifying the padding fix end-to-end: `stringoverhead_customnamelen*`
     (maxlen=100, type name "CStrNameLen100") shows a flat +8 the
     confirmed formula doesn't explain, even though the SAME maxlen=100
     under a DIFFERENT, shorter type name ("CStrB3_100") fits with zero
     residual. memory_model.yaml already flagged this exact risk before
     today ("Not yet tested for type-NAME-length sensitivity"). Isolates
     it directly: same maxlen (100), same tag-name shape, THREE type-name
     lengths (short/medium/long) at both def_only and 1-instance shapes.

  B. group_constant_flag -- Constant="true" on a STRING/custom-string tag,
     James's new question, never tested for ANY data type in this project
     before. Crossed with processor family (1756-L8x vs 5069-Lxxx) per
     James's explicit ask -- built-in and custom STRING each get a
     Constant=true/false pair on each processor family (8 files).

  C. group_cop_string_members -- COP/CPS on a STRING's own .DATA (a plain
     SINT array, real corpus-confirmed subscript syntax `.DATA[0]`, see
     docs/MEMORY_MODEL.md's SIZE/BTD syntax note) and .LEN (a plain DINT)
     sub-elements, for both built-in and custom STRING. Confirms these
     size like an ordinary SINT-array/DINT COP -- no STRING-specific
     surcharge -- since a real program commonly copies string internals
     this way (fixed-length buffer shuffling, length-prefixed protocols).

Run: python -m sample_gen.gen_string_closure
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import custom_string_type_xml, rungs_xml, string_array_tag_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

TAGS_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"
LOGIC_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"


def _write(out_dir: Path, l5x: str, out_name: str, description: str, category: str) -> int:
    out_path = out_dir / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, category, out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 1


# ---------------------------------------------------------------------------
# A. Custom-string TYPE-NAME length sensitivity (new residual, isolate it)
# ---------------------------------------------------------------------------

def group_typename_length() -> int:
    n = 0
    maxlen = 100
    names = {"short": "A", "medium": "CStr100Md", "long": "CStrTypeNameVeryLongIsolation100"}
    for label, type_name in names.items():
        datatype = custom_string_type_xml(type_name, maxlen)
        def_l5x = build_l5x(target_name=f"StrTName{label.title()}Def", tags_xml="", extra_datatypes_xml=datatype)
        n += _write(TAGS_OUT, def_l5x, f"stringoverhead_typenamelen_{label}_def_only",
                    f"Custom string type maxlen=100, type name '{type_name}' ({len(type_name)} chars), "
                    f"0 instances -- isolates whether custom_definition_cost depends on the TYPE's own "
                    f"name length (real residual found 2026-08-25 on a long type name, unexplained by "
                    f"the confirmed maxlen-only formula)",
                    "string_tagoverhead")

        tag = tag_xml("TestInstance", type_name, string_max_len=maxlen)
        inst_l5x = build_l5x(target_name=f"StrTName{label.title()}Inst", tags_xml=tag, extra_datatypes_xml=datatype)
        n += _write(TAGS_OUT, inst_l5x, f"stringoverhead_typenamelen_{label}_1_instance",
                    f"Custom string type maxlen=100, type name '{type_name}' ({len(type_name)} chars), "
                    f"1 instance -- same type-name-length isolation, instance shape",
                    "string_tagoverhead")
    return n


# ---------------------------------------------------------------------------
# B. Constant="true", builtin + custom -- single processor (1756-L81E, the
#    same default every other file in this project uses).
#
#    2026-08-26 CORRECTION (James, direct field knowledge): the original
#    version of this group crossed Constant with processor family (L8 vs
#    5069), which was unnecessary and actively broke the capture batch --
#    "5069 and l8/l9 processors use the same calculations for constant
#    strings ... don't know why you would change that all of a sudden."
#    Real fact, logged for the record: L8/L9/5069 can MOV a STRING tag
#    directly; older L7/1769 processors required COP instead. Not a
#    sizing question, and not something that needed a processor-varying
#    test here -- dropped back to the same single default processor every
#    other file uses. The processor-varying files also happened to
#    surface a real tooling issue (a "Local" module name collision when
#    Studio 5000's same-instance file-switch changes processor identity
#    mid-batch, see OQ-STRINGCONSTFAIL) -- moot now that this group no
#    longer varies processor at all.
# ---------------------------------------------------------------------------

def group_constant_flag() -> int:
    n = 0
    custom_type = custom_string_type_xml("CStrConstTest", 82)
    for const_label, const in [("const", True), ("nonconst", False)]:
        builtin_tag = tag_xml("StrConstTag", "STRING", string_max_len=82, constant=const)
        l5x = build_l5x(target_name=f"StrConst{const_label.title()}", tags_xml=builtin_tag)
        n += _write(TAGS_OUT, l5x, f"stringconst_builtin_{const_label}",
                    f"1 built-in STRING tag, Constant={const} -- James: does marking a STRING tag "
                    f"Constant change its size",
                    "string_tagoverhead")

        custom_tag = tag_xml("CStrConstTag", "CStrConstTest", string_max_len=82, constant=const)
        l5x = build_l5x(target_name=f"CStrConst{const_label.title()}",
                         tags_xml=custom_tag, extra_datatypes_xml=custom_type)
        n += _write(TAGS_OUT, l5x, f"stringconst_custom_{const_label}",
                    f"1 custom string (maxlen=82) tag, Constant={const} -- same Constant question "
                    f"for a custom StringFamily type",
                    "string_tagoverhead")
    return n


# ---------------------------------------------------------------------------
# C. COP/CPS on a STRING's own .DATA (SINT array) and .LEN (DINT) members
# ---------------------------------------------------------------------------

def group_cop_string_members() -> int:
    n = 0
    custom_type = custom_string_type_xml("CStrCopTest", 82)
    builtin_src = tag_xml("SrcStr", "STRING", string_max_len=82)
    custom_src = tag_xml("SrcCStr", "CStrCopTest", string_max_len=82)
    data_dest = tag_xml("DataDest", "SINT", dimensions=(82,))
    len_dest = tag_xml("LenDest", "DINT")

    variants = [
        ("builtin_data", "COP(SrcStr.DATA[0],DataDest[0],82);", "\n".join([builtin_src, data_dest]), ""),
        ("builtin_len", "COP(SrcStr.LEN,LenDest,1);", "\n".join([builtin_src, len_dest]), ""),
        ("custom_data", "COP(SrcCStr.DATA[0],DataDest[0],82);", "\n".join([custom_src, data_dest]), custom_type),
        ("custom_len", "COP(SrcCStr.LEN,LenDest,1);", "\n".join([custom_src, len_dest]), custom_type),
    ]
    for label, instr, tags, extra_dt in variants:
        for count in [1, 10]:
            fn = lambda i, instr=instr: instr
            rungs = rungs_xml(count, fn)
            l5x = build_l5x(target_name=f"CopStr{label.title().replace('_', '')}N{count}",
                             tags_xml=tags, extra_rungs_xml=rungs, extra_datatypes_xml=extra_dt)
            n += _write(LOGIC_OUT, l5x, f"stringcop_{label}_n{count:02d}",
                        f"{count} rungs of {instr} -- COP on a STRING's own {label.split('_')[1].upper()} "
                        f"member ({'built-in' if 'builtin' in label else 'custom'} STRING) -- James: "
                        f"confirm the DATA SINT array and LEN element are valid COP/CPS operands, and "
                        f"size like an ordinary SINT-array/DINT COP with no STRING-specific surcharge",
                        "logic_instr")
    return n


# ---------------------------------------------------------------------------
# D. Array-of-STRING count sweep -- the existing 2-point data (n=5/50) for
#    BOTH builtin and custom string arrays shows a real residual the
#    scalar-tag padding fix (group A-C above / the 2026-08-25 udt.py fix)
#    does NOT explain -- builtin shows a growing per-element gap (+2/
#    element), custom100 shows an even bigger, ALSO-growing gap once the
#    scalar padding fix is applied to its per-element size (was flat +6
#    before the fix, is +24/+204 -- i.e. growing -- after). This is
#    NOT the same mechanism as the scalar case; more count points needed
#    to fit it rather than guessing from 2 points. See OQ-STRINGARRAYPAD.
# ---------------------------------------------------------------------------

def group_string_array_countsweep() -> int:
    n = 0
    for count in [1, 10, 25, 100]:
        tag = string_array_tag_xml("StrArr", count, max_len=82)
        l5x = build_l5x(target_name=f"StringArrayCsN{count}", tags_xml=tag)
        n += _write(TAGS_OUT, l5x, f"stringarray_builtin_n{count:03d}",
                     f"ONE array-of-STRING tag, {count} built-in STRING elements -- additional count-sweep "
                     f"point (existing n5/n50 data shows a real +2/element residual, unexplained, needs "
                     f"more points to fit)",
                     "string_array")

    custom_type = custom_string_type_xml("CStrArrCsTest", 100)
    for count in [1, 10, 25, 100]:
        tag = string_array_tag_xml("CStrArrCs", count, max_len=100, data_type="CStrArrCsTest")
        l5x = build_l5x(target_name=f"CustomStringArrayCsN{count}", tags_xml=tag, extra_datatypes_xml=custom_type)
        n += _write(TAGS_OUT, l5x, f"stringarray_custom100_cs_n{count:03d}",
                     f"ONE array-of-custom-string tag, {count} elements of a 100-char custom string type -- "
                     f"additional count-sweep point (existing n5/n50 data shows a real, growing residual "
                     f"once the scalar nearest-8 padding fix is applied to the per-element size -- the "
                     f"scalar fix does not transfer cleanly to the array context, needs its own fit)",
                     "string_array")
    return n


def main() -> None:
    total = 0
    for fn in [group_typename_length, group_constant_flag, group_cop_string_members,
               group_string_array_countsweep]:
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
