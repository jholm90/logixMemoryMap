"""Targeted test batch to close the specific gaps blocking model fixes
(James, 2026-09-04: "can you generate a dozen or more tests that will help
you fix your models and answer some questions that you want explored?").

Every file here answers ONE named, currently-blocking question. Nothing is
filler -- see docs/FUTURE_TESTS.md for the full ordered list this is drawn
from, and CLAUDE.md's "don't just fill up the minimum roster" rule.

Deliberately NOT included, because the data already exists: the
structural-module point-count/class ladders (OQ-MODULESTRUCTURAL). Every
catalog those need -- 1756-IA32/IB16/IF8/OF4/OF8/OA16, 1794-IA16/IB16/
IB32/IR8/OA8/OE4, 1734-IB8/OB8/OA4/OB2EP/IE2C/IE4C/OE2C/IR2 -- ALREADY has
a valid error-free single-module capture in manifest.csv. That model can
be fitted from what's on file; re-capturing it would waste real bench
time.

GROUPS
------
A. group_cpt_realdest_operator_counts (4 files)
   cpt_expression.real_dest was wired 2026-09-04 exact on 29/29 real rows,
   but ONLY at operator counts 1, 2 and 5. `extra_operator` (40) is
   confirmed between n=1 and n=2 and reproduces n=5 only via a separate
   +4 `five_plus_operator_extra` that currently rests on n=5 ALONE. These
   fill in n = 3, 4, 6, 8 so that term is either explained or dropped:
   if the true rule is a flat 40/operator, n=3/4 land 4 low and n=6/8
   land 4 high against the current model; if it is a real step at 5, n=3/4
   land exact and n=6/8 land exact too.

B. group_cpt_realdest_pow_multi (3 files)
   `single_pow_extra` (+8) is confirmed at n_ops=1 ONLY. A multi-operator
   REAL-destination expression containing ** is completely untested, so
   the model currently charges POW nothing extra beyond one operator.
   Three shapes at 2/3/5 operators, each with exactly one **.

C. group_cpt_realdest_operand_types (3 files)
   The int->float conversion charge (40/operand) is confirmed for DINT
   tags and int literals. SINT/INT/LINT are ASSUMED to convert the same
   way (they are in _CPT_INTEGER_OPERAND_TYPES) and BOOL is deliberately
   excluded with zero real evidence either way. One file each isolates
   SINT, LINT and BOOL operands in an otherwise-identical REAL-dest CPT.

D. group_jsr_namelen_crossed (4 files)
   Two separately-EXACT findings on valid data are both unwired because
   one cell is missing: distinct-target count gives +125/target (6/6
   points, d = 125n - 280) at a fixed 16-char name, and target-name length
   gives +80 per 8 chars (5/5 points) at a fixed 10 targets. Whether the
   name cost is PER TARGET or PER FILE is not decidable from those two
   1-D slices -- they only cross at (n=10, len=16). These cross them:
   n=20 and n=40, each at len=16 and len=32. If per-target, the len32
   files gain 2x what the len16 files do; if per-file, they gain the same.

E. group_jsr_paramtype_count (4 files)
   A STRING/UDT-typed JSR parameter carries a real surcharge that is NOT
   linear in parameter count: at 100 calls the measured deltas are n=1
   -> +271, n=3 -> +2,307, n=5 -> +3,939 (per-param 2.7 / 7.7 / 7.9).
   Something changes between 1 and 3 params. n = 2, 4, 6, 8 resolve the
   shape.

F. group_module_repeat_marginal (4 files)
   Whether the 2nd/4th/Nth copy of a module costs the same as the 1st is
   still genuinely open -- and the one apparently-clean answer this
   project had was fitted on the axis_scale_* sweep, EVERY file of which
   built with errors (error_count = drives+1), so it was an artifact and
   was reverted. This re-asks the question on a deliberately boring,
   error-free shape: N copies of ONE simple 1756 discrete input module in
   a plain local chassis, N = 1/2/4/8, nothing else varying. Simple
   discrete I/O is chosen specifically because it has no motion, safety,
   or connection-variant content to fail the build.

Run: python -m sample_gen.gen_model_gap_closers
"""

from __future__ import annotations

import re
from pathlib import Path

from sample_gen.builders import MemberSpec, rung_xml, tag_xml, udt_xml
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

LOGIC_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
MODULE_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

# Same pool shape as gen_cmpcpt_layout.py / gen_cpt_comprehensive.py so every
# new row subtracts cleanly against the existing cmpcpt_*/cptmix_* corpus.
_POOL_TAGS_XML = (
    "\n".join(tag_xml(f"L{i}", "DINT") for i in range(8)) + "\n"
    + "\n".join(tag_xml(f"R{i}", "REAL") for i in range(6)) + "\n"
    + "\n".join(tag_xml(f"S{i}", "SINT") for i in range(4)) + "\n"
    + "\n".join(tag_xml(f"N{i}", "LINT") for i in range(4)) + "\n"
    + "\n".join(tag_xml(f"B{i}", "BOOL") for i in range(4))
)

_RUNGS_PER_FILE = 100  # amortises the per-file constant; same scale as cmpcpt n=100


def _write_logic(out_name: str, l5x: str, description: str) -> None:
    out_path = LOGIC_OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _cpt_file(out_name: str, target: str, expr: str, description: str) -> None:
    rungs = "\n".join(rung_xml(i, f"CPT({expr});") for i in range(_RUNGS_PER_FILE))
    l5x = build_l5x(target_name=target, tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
    _write_logic(out_name, l5x, description)


# --- A. REAL-dest CPT at the untested operator counts -----------------------

_REALDEST_SHAPES = {
    3: "R2,R0+R1*R3-R4",
    4: "R2,R0+R1*R3-R4/R5",
    6: "R2,R0+R1*R3-R4/R5+R1*R3",
    8: "R2,R0+R1*R3-R4/R5+R1*R3-R4/R5",
}


def group_cpt_realdest_operator_counts() -> None:
    for n_ops, expr in _REALDEST_SHAPES.items():
        _cpt_file(
            f"cptrd_opcount_n{n_ops:02d}", f"CptRdOps{n_ops:02d}", expr,
            f"{_RUNGS_PER_FILE} rungs of CPT({expr}) -- REAL destination, all-REAL operands, "
            f"{n_ops} operators. Closes cpt_expression.real_dest's operator-count coverage gap: "
            f"the model is exact on 29/29 real rows but only at n_ops 1, 2 and 5, so its "
            f"five_plus_operator_extra (+4) rests on n=5 alone. n=3/4 and n=6/8 decide whether "
            f"that is a real step at 5 operators or an artifact of the single shape it was fit "
            f"from. All-REAL operands deliberately, so the per-int-operand conversion term is 0 "
            f"here and only the operator-count term is under test.",
        )


# --- B. POW inside a multi-operator REAL-dest expression --------------------

_REALDEST_POW_SHAPES = {
    2: "R2,R0**R1+R3",
    3: "R2,R0**R1+R3*R4",
    5: "R2,R0**R1+R3*R4-R5/R1",
}


def group_cpt_realdest_pow_multi() -> None:
    for n_ops, expr in _REALDEST_POW_SHAPES.items():
        _cpt_file(
            f"cptrd_powmulti_n{n_ops:02d}", f"CptRdPow{n_ops:02d}", expr,
            f"{_RUNGS_PER_FILE} rungs of CPT({expr}) -- REAL destination, all-REAL operands, "
            f"{n_ops} operators, exactly one of them **. cpt_expression.real_dest's "
            f"single_pow_extra (+8) is confirmed at n_ops=1 ONLY; a multi-operator REAL-dest "
            f"expression containing ** is currently charged no POW premium at all. These say "
            f"whether the +8 is per-** (so it should apply at any operator count) or specific "
            f"to the lone-operator case.",
        )


# --- C. Which operand types actually carry the conversion charge ------------

_REALDEST_OPERAND_SHAPES = {
    "sint": ("R2,S0+S1*S2-R0", "SINT"),
    "lint": ("R2,N0+N1*N2-R0", "LINT"),
    "bool": ("R2,B0+B1*B2-R0", "BOOL"),
}


def group_cpt_realdest_operand_types() -> None:
    for slug, (expr, type_name) in _REALDEST_OPERAND_SHAPES.items():
        _cpt_file(
            f"cptrd_operand_{slug}", f"CptRdOperand{type_name.title()}", expr,
            f"{_RUNGS_PER_FILE} rungs of CPT({expr}) -- REAL destination with 3 {type_name} "
            f"operands, matched 3-operator shape. cpt_expression.real_dest charges "
            f"per_int_operand (40) for every non-float operand, but that rate is only really "
            f"measured on DINT tags and integer literals: SINT/INT/LINT are ASSUMED to convert "
            f"identically (they sit in sizing/logic.py's _CPT_INTEGER_OPERAND_TYPES) and BOOL is "
            f"deliberately EXCLUDED with zero real evidence either way. Each of these isolates "
            f"one type so the assumption is either confirmed or replaced with a real per-type "
            f"rate."
            + (
                " HEADS UP on this one specifically: it is not confirmed that Logix even ACCEPTS "
                "a BOOL operand inside CPT arithmetic. If this file fails to build, that failure "
                "IS the answer -- it settles the open question by ruling BOOL out entirely, and "
                "the exclusion in _CPT_INTEGER_OPERAND_TYPES becomes correct-by-construction "
                "rather than an untested assumption. Skip-list it and move on; do not treat it "
                "as a generator bug to chase."
                if type_name == "BOOL" else ""
            ),
        )


# --- D. JSR target-name length CROSSED with target count --------------------

def _padded_name(prefix: str, i: int, total_length: int, index_width: int) -> str:
    """Exact-length valid Logix identifier, index kept intact so names in a
    group are always distinct. Same helper (and same real generator bug it
    was written to avoid -- silently collapsing every name to one string at
    short lengths) as gen_jsr_multi_distinct_targets_scale.py."""
    idx = str(i).zfill(index_width)
    fill_len = max(total_length - len(prefix) - len(idx), 0)
    name = f"{prefix}{'X' * fill_len}{idx}"
    if len(name) > total_length:
        keep = max(total_length - len(idx), 1)
        name = f"{prefix[:keep]}{idx}"
    return name


def _jsr_target_xml(name: str) -> str:
    return (
        f'<Routine Name="{name}" Type="RLL">'
        f"<RLLContent>{rung_xml(0, 'NOP();')}</RLLContent>"
        "</Routine>"
    )


def group_jsr_namelen_crossed() -> None:
    for n_targets in (20, 40):
        for length in (16, 32):
            names = [_padded_name("T", i, length, index_width=2) for i in range(n_targets)]
            targets_xml = "\n".join(_jsr_target_xml(t) for t in names)
            call_rungs = "\n".join(rung_xml(i, f"JSR({t},0);") for i, t in enumerate(names))
            l5x = build_l5x(
                target_name=f"JsrCross{n_targets:02d}L{length:02d}", tags_xml="",
                extra_rungs_xml=call_rungs, extra_routines_xml=targets_xml,
            )
            out_name = f"jsr_crossed_n{n_targets:02d}_namelen{length:02d}"
            out_path = LOGIC_OUT.parent / "logic" / f"{out_name}.L5X"
            bytes_ = write_sample(l5x, out_path)
            append_manifest_row(
                out_name,
                f"{n_targets} distinct 0-param JSR targets, every target name EXACTLY {length} "
                f"characters -- the missing crossed cell for OQ-JSRPARAMCOST. Two findings are "
                f"each exact on valid data but neither can be wired: distinct-target COUNT gives "
                f"+125/target (6/6 points, d = 125n - 280) measured at a fixed 16-char name, and "
                f"target-NAME LENGTH gives +80 per 8 chars (5/5 points) measured at a fixed 10 "
                f"targets. Those two 1-D slices only intersect at (n=10, len=16), so whether the "
                f"name cost is PER TARGET or PER FILE is undecidable. Crossing n=20/40 with "
                f"len=16/32 decides it: per-target means the len32 file gains n x the len16 "
                f"file's step, per-file means both gain the same fixed amount.",
                "jsr_sbr_ret", out_path, bytes_,
            )
            print(f"Wrote {out_path} (predicted {bytes_} bytes)")


# --- E. STRING/UDT JSR parameter count ------------------------------------

_JSR_PARAM_CALLS = 100
_UDT_MEMBERS = [MemberSpec("A", "DINT"), MemberSpec("B", "REAL"), MemberSpec("C", "DINT")]


def group_jsr_paramtype_count() -> None:
    types_xml = udt_xml("JsrParamUdt", _UDT_MEMBERS)
    for n_params in (2, 4, 6, 8):
        params = [f"P{i}" for i in range(n_params)]
        tags_xml = "\n".join(tag_xml(p, "JsrParamUdt", udt_members=_UDT_MEMBERS) for p in params)
        sbr_args = ",".join(params)
        target = (
            '<Routine Name="JsrUdtTarget" Type="RLL"><RLLContent>'
            + rung_xml(0, f"SBR({sbr_args});")
            + rung_xml(1, "RET();")
            + "</RLLContent></Routine>"
        )
        call_rungs = "\n".join(
            rung_xml(i, f"JSR(JsrUdtTarget,{n_params},{sbr_args});")
            for i in range(_JSR_PARAM_CALLS)
        )
        l5x = build_l5x(
            target_name=f"JsrUdtParam{n_params:02d}", tags_xml=tags_xml,
            extra_datatypes_xml=types_xml, extra_rungs_xml=call_rungs,
            extra_routines_xml=target,
        )
        out_name = f"jsr_paramtype_udt_n{n_params:02d}_r00100"
        out_path = LOGIC_OUT / f"{out_name}.L5X"
        bytes_ = write_sample(l5x, out_path)
        append_manifest_row(
            out_name,
            f"{_JSR_PARAM_CALLS} JSR calls passing {n_params} UDT-typed parameters -- fills the "
            f"gap in OQ-JSRPARAMCOST's STRING/UDT parameter surcharge, which is real but NOT "
            f"linear in parameter count: the existing valid captures give n=1 -> +271, n=3 -> "
            f"+2,307, n=5 -> +3,939 at 100 calls (per-param 2.7, then 7.7, then 7.9), so "
            f"something changes between 1 and 3 params and nothing on file resolves it. Even "
            f"n = 2/4/6/8 across the same shape gives the curve.",
            "jsr_sbr_ret", out_path, bytes_,
        )
        print(f"Wrote {out_path} (predicted {bytes_} bytes)")


# --- F. Repeated-module marginal cost, on an error-free shape ---------------

_REPEAT_CATALOG = "1756-IB16"
_REPEAT_COUNTS = (1, 2, 4, 8)


def _module_block(catalog: str, index: int, slot: int) -> str:
    """One real 1756-IB16 Module block, renamed and re-slotted. Content is
    reused verbatim from gen_module_sweep.py's own real captured chain --
    only Name and the local-backplane slot Address change, the same
    convention every other rack generator in this project uses."""
    xml, _source, _chain_len = _MODULE_CHAINS[catalog]
    blocks = re.findall(r"<Module\b.*?</Module>", xml, re.DOTALL)
    block = blocks[-1]
    block = re.sub(r'(<Module\b[^>]*?\bName=")[^"]+(")', rf"\g<1>RepeatMod{index:02d}\g<2>",
                   block, count=1)
    block = re.sub(r'(<Port\b[^>]*?\bAddress=")\d+(")', rf"\g<1>{slot}\g<2>", block, count=1)
    return block


def group_module_repeat_marginal() -> None:
    for n in _REPEAT_COUNTS:
        modules_xml = "\n".join(_module_block(_REPEAT_CATALOG, i, i + 1) for i in range(n))
        l5x = build_l5x(
            target_name=f"ModRepeat{n:02d}", tags_xml="", extra_modules_xml=modules_xml,
        )
        out_name = f"modrepeat_1756_ib16_n{n:02d}"
        out_path = MODULE_OUT / f"{out_name}.L5X"
        bytes_ = write_sample(l5x, out_path)
        append_manifest_row(
            out_name,
            f"{n} identical real {_REPEAT_CATALOG} discrete input modules in one plain 1756 "
            f"local chassis, nothing else varying -- re-asks OQ-MODULEIO's multi-module marginal "
            f"question on a shape that will actually BUILD CLEAN. The only previous answer this "
            f"project had was fitted on the 18-file axis_scale_* sweep, every file of which has "
            f"error_count = drives+1, so its beautifully linear per-extra-drive discount was an "
            f"artifact of drives failing to build and was reverted (see docs/TESTING_PLAN.md). "
            f"Simple discrete I/O is chosen deliberately: no motion, safety or connection-variant "
            f"content to fail the build. Does module #2/#4/#8 cost the same as module #1?",
            "modules", out_path, bytes_,
        )
        print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def main() -> None:
    group_cpt_realdest_operator_counts()
    group_cpt_realdest_pow_multi()
    group_cpt_realdest_operand_types()
    group_jsr_namelen_crossed()
    group_jsr_paramtype_count()
    group_module_repeat_marginal()
    total = 4 + 3 + 3 + 4 + 4 + 4
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
