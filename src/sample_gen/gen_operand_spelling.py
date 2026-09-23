"""Operand spelling and structured addressing -- four questions, 50 files.

Resolving the operand-type surcharge and the tag-driven index through every
spelling took the real set from 2.86% to 1.66% with no constant changed
(OPEN_QUESTIONS.md OQ-REALUNDER, "Spelling, not cost"). No generated file had
ever carried the shapes involved. This batch measures them, and the three shapes
next to them that real programs use in bulk and nothing has priced.

Every file is on the realism floor (sample_gen/realism.py) and adds 500 rungs to
MainProgram/MainRoutine. Within each question every file declares the same tags,
so a pair differs only in rung text. Compare rungs close on OTE into a DINT
array bit, one distinct bit per rung.

OQ-TYPEDMEMBER + OQ-MIXEDTYPE (one shared inventory, 29 files)
  opsp_typed_{add,mov,grt}_{real,int}_{bare,member,arrelem}   18
      The same instruction and type spelled as a bare tag, a UDT member
      (`TmU.R0`) and a UDT-array element with a literal index (`TmUA[1].R0`).
      Wired rule: all three pay the same surcharge.
  opsp_typed_{add,mov,grt}_dint_bare                           3
      The DINT-rate controls.
  opsp_mixed_{mov_d2r,mov_r2d,mov_i2d,mov_d2i,add_drr,add_rdd,grt_rd,grt_id}   8
      Operand types mixed within one call, against the uniform twins above.
  The engine charges a mixed call by its first resolvable operand.

OQ-TYPEDMEMBER, AOI arm (2 files)
  opsp_aoi_add_{real,dint}   an AOI definition whose Logic is 100 rungs of
      ADD on REAL vs DINT local tags. The AOI's own parameters and locals now
      resolve; before, AOI logic paid no type surcharge at all.

OQ-INDIRECTUDT (14 files)
  opsp_ind_mov_e{04,08,12,76}_{idx,lit}   MOV(A[IuIdx].M,Dst) vs MOV(A[5].M,Dst),
      element sizes 4, 8, 12 and 76 bytes (UDTs of 1, 2, 3 and 19 DINTs)
  opsp_ind_xicmem_{idx,lit}               XIC(Ab[IuIdx].B) -- a BOOL member of an
      indexed UDT element
  opsp_ind_xicbool_{idx,lit}              XIC(IuB[IuIdx]) -- a BOOL array
  opsp_ind_equ_e76_{idx,lit}              EQU(A19[IuIdx].M,Dst)
  Calibrated only on MOV(DintArr[Idx],Dest). Each _idx against its _lit twin.

OQ-STRINGMOV (5 files)
  opsp_str_{mov,cop,movidx,movcustom,movdint}
      MOV(S1,S2), COP(S1,S2,1), MOV(SA[SmIdx],S2), MOV on a 20-character custom
      string type, and the DINT MOV control. 7,626 real MOVs carry a STRING.

1756-L81E at firmware 35.

Run: python -m sample_gen.gen_operand_spelling
"""

from __future__ import annotations

from pathlib import Path

from sample_gen import realism
from sample_gen.builders import (
    MemberSpec, aoi_xml, custom_string_type_xml, rung_xml, string_array_tag_xml, tag_xml, udt_xml,
)
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "opspell"
CATEGORY = "logic_instr"
RUNGS = 500
_Q_WORDS = -(-RUNGS // 32)


def _q(prefix: str, i: int) -> str:
    """A distinct output bit per rung: word i//32, bit i%32."""
    return f"{prefix}[{i // 32}].{i % 32}"


def _write(name: str, description: str, **arm) -> int:
    l5x = build_l5x(target_name=f"Opsp_{name}"[:40], **realism.with_baseline(**arm))
    out = OUT_ROOT / f"opsp_{name}.L5X"
    predicted = write_sample(l5x, out)
    append_manifest_row(f"opsp_{name}", description, CATEGORY, out, predicted)
    print(f"Wrote {out.name} (predicted {predicted:,})")
    return 1


def _rungs(fn) -> str:
    return "\n".join(rung_xml(i, fn(i)) for i in range(RUNGS))


# --- OQ-TYPEDMEMBER + OQ-MIXEDTYPE ------------------------------------------

_TM_MEMBERS = ([MemberSpec(f"R{i}", "REAL") for i in range(3)]
               + [MemberSpec(f"I{i}", "INT") for i in range(3)]
               + [MemberSpec(f"D{i}", "DINT") for i in range(3)])
_TM_CODE = {"real": "R", "int": "I", "dint": "D"}


def _tm_inventory() -> dict[str, str]:
    tags = [tag_xml(f"Tm{c}{i}", t) for c, t in (("D", "DINT"), ("R", "REAL"), ("I", "INT")) for i in range(3)]
    tags += [tag_xml("TmU", "TmUdt", udt_members=_TM_MEMBERS),
             tag_xml("TmUA", "TmUdt", dimensions=(4,), udt_members=_TM_MEMBERS),
             tag_xml("TmQ", "DINT", dimensions=(_Q_WORDS,))]
    return {"tags_xml": "\n".join(tags), "extra_datatypes_xml": udt_xml("TmUdt", _TM_MEMBERS)}


def _tm_operand(spelling: str, code: str, n: int) -> str:
    return {"bare": f"Tm{code}{n}", "member": f"TmU.{code}{n}", "arrelem": f"TmUA[1].{code}{n}"}[spelling]


_TM_SHAPES = {
    "add": lambda op, i: f"ADD({op(0)},{op(1)},{op(2)});",
    "mov": lambda op, i: f"MOV({op(0)},{op(1)});",
    "grt": lambda op, i: f"GRT({op(0)},{op(1)})OTE({_q('TmQ', i)});",
}


def group_typed() -> int:
    inv = _tm_inventory()
    n = 0
    for instr, shape in _TM_SHAPES.items():
        for type_name in ("real", "int"):
            code = _TM_CODE[type_name]
            for spelling in ("bare", "member", "arrelem"):
                op = lambda k, s=spelling, c=code: _tm_operand(s, c, k)
                example = shape(op, 0)
                n += _write(
                    f"typed_{instr}_{type_name}_{spelling}",
                    f"OQ-TYPEDMEMBER: {RUNGS} rungs of `{example}` -- {type_name.upper()} operands "
                    f"spelled as {'bare tags' if spelling == 'bare' else 'UDT members' if spelling == 'member' else 'members of a UDT-array element with a literal index'}. "
                    f"Differenced against opsp_typed_{instr}_{type_name}_bare (same type, bare spelling) "
                    f"and opsp_typed_{instr}_dint_bare (DINT rate). Same tags in every opsp_typed_*/"
                    f"opsp_mixed_* file.", **inv, extra_rungs_xml=_rungs(lambda i: shape(op, i)))
        op = lambda k: f"TmD{k}"
        n += _write(
            f"typed_{instr}_dint_bare",
            f"OQ-TYPEDMEMBER / OQ-MIXEDTYPE control: {RUNGS} rungs of `{shape(op, 0)}` on DINT tags, "
            f"the rate every weight was fitted at. Same tags in every opsp_typed_*/opsp_mixed_* file.",
            **inv, extra_rungs_xml=_rungs(lambda i: shape(op, i)))
    return n


_MIXED = {
    "mov_d2r": ("MOV(TmD0,TmR0);", "opsp_typed_mov_dint_bare and opsp_typed_mov_real_bare"),
    "mov_r2d": ("MOV(TmR0,TmD0);", "opsp_typed_mov_real_bare and opsp_typed_mov_dint_bare"),
    "mov_i2d": ("MOV(TmI0,TmD0);", "opsp_typed_mov_int_bare and opsp_typed_mov_dint_bare"),
    "mov_d2i": ("MOV(TmD0,TmI0);", "opsp_typed_mov_dint_bare and opsp_typed_mov_int_bare"),
    "add_drr": ("ADD(TmD0,TmR0,TmR1);", "opsp_typed_add_dint_bare and opsp_typed_add_real_bare"),
    "add_rdd": ("ADD(TmR0,TmD0,TmD1);", "opsp_typed_add_real_bare and opsp_typed_add_dint_bare"),
    "grt_rd": ("GRT(TmR0,TmD0)", "opsp_typed_grt_real_bare and opsp_typed_grt_dint_bare"),
    "grt_id": ("GRT(TmI0,TmD0)", "opsp_typed_grt_int_bare and opsp_typed_grt_dint_bare"),
}


def group_mixed() -> int:
    inv = _tm_inventory()
    n = 0
    for name, (text, twins) in _MIXED.items():
        fn = (lambda i, t=text: f"{t}OTE({_q('TmQ', i)});") if text.startswith("GRT") else (lambda i, t=text: t)
        n += _write(
            f"mixed_{name}",
            f"OQ-MIXEDTYPE: {RUNGS} rungs of `{fn(0)}` -- operand types mixed within one call. "
            f"Differenced against its uniform-type twins {twins}; the engine charges a mixed call "
            f"by its first resolvable operand. Same tags in every opsp_typed_*/opsp_mixed_* file.",
            **inv, extra_rungs_xml=_rungs(fn))
    return n


def group_aoi() -> int:
    n = 0
    for type_name in ("REAL", "DINT"):
        locals_ = [MemberSpec(f"L{i}", type_name) for i in range(3)]
        logic = "\n".join(rung_xml(i, "ADD(L0,L1,L2);") for i in range(100))
        definition, _storage = aoi_xml("OpspAoiAdd", [MemberSpec("In0", "DINT")], [MemberSpec("Out0", "BOOL")],
                                       [], locals_, logic_rungs_xml=logic)
        n += _write(
            f"aoi_add_{type_name.lower()}",
            f"OQ-TYPEDMEMBER, AOI arm: an AOI definition (no instance) whose Logic is 100 rungs of "
            f"ADD(L0,L1,L2) on {type_name} local tags. Differenced against opsp_aoi_add_"
            f"{'dint' if type_name == 'REAL' else 'real'}: does AOI-internal logic pay the operand-type "
            f"surcharge (ADD REAL +16)? Before the resolver it paid none.",
            tags_xml="", extra_aoi_xml=definition)
    return n


# --- OQ-INDIRECTUDT -----------------------------------------------------------

_ELEMENT_DINTS = {"e04": 1, "e08": 2, "e12": 3, "e76": 19}


def _iu_inventory() -> dict[str, str]:
    types, tags = [], [tag_xml("IuIdx", "DINT"), tag_xml("IuDst", "DINT"),
                       tag_xml("IuQ", "DINT", dimensions=(_Q_WORDS,)),
                       tag_xml("IuB", "BOOL", dimensions=(64,))]
    for label, k in _ELEMENT_DINTS.items():
        members = [MemberSpec("M", "DINT")] + [MemberSpec(f"P{j}", "DINT") for j in range(k - 1)]
        types.append(udt_xml(f"IuUdt{label}", members))
        tags.append(tag_xml(f"IuA{label}", f"IuUdt{label}", dimensions=(20,), udt_members=members))
    bmembers = [MemberSpec("B", "BOOL"), MemberSpec("M", "DINT")]
    types.append(udt_xml("IuUdtBool", bmembers))
    tags.append(tag_xml("IuAb", "IuUdtBool", dimensions=(20,), udt_members=bmembers))
    return {"tags_xml": "\n".join(tags), "extra_datatypes_xml": "\n".join(types)}


def group_indirect() -> int:
    inv = _iu_inventory()
    arms = {f"mov_{label}": (f"MOV(IuA{label}[{{ix}}].M,IuDst);", f"a {4 * k}-byte UDT element's DINT member")
            for label, k in _ELEMENT_DINTS.items()}
    arms["xicmem"] = ("XIC(IuAb[{ix}].B)OTE({q});", "a BOOL member of a UDT-array element")
    arms["xicbool"] = ("XIC(IuB[{ix}])OTE({q});", "a BOOL array element")
    arms["equ_e76"] = ("EQU(IuAe76[{ix}].M,IuDst)OTE({q});", "a 76-byte UDT element's DINT member, compared")
    n = 0
    for arm, (template, what) in arms.items():
        for kind, ix in (("idx", "IuIdx"), ("lit", "5")):
            fn = lambda i, t=template, x=ix: t.format(ix=x, q=_q("IuQ", i))
            n += _write(
                f"ind_{arm}_{kind}",
                f"OQ-INDIRECTUDT: {RUNGS} rungs of `{fn(0)}` -- {what}, "
                f"{'indexed by a tag' if kind == 'idx' else 'at a literal index (the control)'}. "
                f"Differenced against opsp_ind_{arm}_{'lit' if kind == 'idx' else 'idx'}. The index cost "
                f"(84) was calibrated only on MOV(DintArr[Idx],Dest). Same tags in every opsp_ind_* file.",
                **inv, extra_rungs_xml=_rungs(fn))
    return n


# --- OQ-STRINGMOV -------------------------------------------------------------

def group_string() -> int:
    tags = [tag_xml(f"SmS{i}", "STRING", string_max_len=82) for i in (1, 2)]
    tags += [tag_xml(f"SmC{i}", "SmStr20", string_max_len=20) for i in (1, 2)]
    tags += [string_array_tag_xml("SmSA", 8), tag_xml("SmIdx", "DINT"),
             tag_xml("SmD1", "DINT"), tag_xml("SmD2", "DINT")]
    inv = {"tags_xml": "\n".join(tags), "extra_datatypes_xml": custom_string_type_xml("SmStr20", 20)}
    arms = {
        "mov": ("MOV(SmS1,SmS2);", "a STRING to a STRING by MOV"),
        "cop": ("COP(SmS1,SmS2,1);", "the same copy by COP"),
        "movidx": ("MOV(SmSA[SmIdx],SmS2);", "an indexed STRING-array element by MOV"),
        "movcustom": ("MOV(SmC1,SmC2);", "a 20-character custom string type by MOV"),
        "movdint": ("MOV(SmD1,SmD2);", "a DINT by MOV (the control)"),
    }
    n = 0
    for arm, (text, what) in arms.items():
        n += _write(
            f"str_{arm}",
            f"OQ-STRINGMOV: {RUNGS} rungs of `{text}` -- {what}. The engine charges a STRING MOV as a "
            f"DINT MOV; 7,626 real MOVs carry a STRING. Differenced against opsp_str_movdint and the "
            f"other opsp_str_* files. Same tags in all five.",
            **inv, extra_rungs_xml=_rungs(lambda i, t=text: t))
    return n


def main() -> None:
    n = group_typed() + group_mixed() + group_aoi() + group_indirect() + group_string()
    print(f"\nDone. {n} files.")


if __name__ == "__main__":
    main()
