"""Three closeout probes, each splitting a term this corpus measured but could
not attribute. Written 2026-09-14 out of the segment 14/17/20 reviews.

Every one of the three exists because a measured number is currently fitted
against one point in the variable that would separate a per-call cost from a
per-item cost -- the collinearity trap this project has hit seven times. None of
them is a sweep for its own sake; each is the minimum that resolves one term.

  A. EN2T count sweep, 4 files (OQ-MODULEMARGINAL).
     modmarg_ob32chain_* gives a flat 2,320 per additional EN2T-plus-OB32 chain
     against a modelled 3,544, exact at three counts -- one equation, two
     unknowns, because every copy adds both an EN2T and the OB32 behind it.
     These files repeat the EN2T ALONE, every copy under Local with no
     downstream child, so differencing against the chain sweep at matching
     counts gives 1756-EN2T's own first-instance and repeat rates and leaves
     rack-aliased 1756-OB32 by subtraction.

     It answers a second question at the same time. The EN2T's own
     first-instance rate is wrong in BOTH directions across its three captured
     connection variants -- modulesweep_1756_en2t_variant_1conn is 1,248 over,
     _noconn 1,872 over, _1conn2 908 UNDER -- which is the signature of a cost
     that tracks the connection configuration rather than the catalog, the same
     shape problem already proven for ETHERNET-MODULE. A count sweep on ONE
     variant separates the per-instance rate from that variant spread.

  B. CPT destination/operand type mismatch, 4 files (OQ-CPTARRANGE).
     cptdest_* measured two real under-charges exactly and linearly over a 100x
     count span: a DINT destination with REAL operands is +48 per CPT, a REAL
     destination with DINT operands +4. Both were measured with ALL FOUR operands
     mismatched, so +48 is equally 48 per call or 12 per operand. Sweeping the
     operand count cannot separate those -- n operands forces n-1 operators, so
     the two move together -- so these files pin cptdest's exact shape and sweep
     how many of its four operands are the odd type: 1 and 2, against cptdest's
     own 4. Per-operand reads 12/24/48, per-call a flat 48.

  C. Platform content-unit decomposition, 3 files (OQ-REAL5069 spillover).
     platform_plateql* over-predicts by exactly 12n + 32 on both processors,
     where each unit is one UDT tag PLUS one DINT tag PLUS one rung -- all three
     scaling together. Two of the three are independently exact elsewhere
     (dscale2_udt_u001_t{001..500} is flat in tag count over a 500x span,
     instr_* sits in the +-8 band to 5,000 instructions), but this family's rung
     is XIC(PeBit0)MOV(0,PeDint0000)OTE(PeBit1) -- three instructions with a
     LITERAL MOV source -- which no isolating family covers. These three files
     carry one component each at a fixed count of 100, against the same UDT and
     the same baseline, so the 12 lands on whichever one moves.

Everything is 1756-L81E at v35, per CLAUDE.md.

Run: python -m sample_gen.gen_segment_closeout
"""

from __future__ import annotations

import re
from pathlib import Path

from sample_gen.builders import MemberSpec, rung_xml, tag_xml, udt_xml
from sample_gen.gen_module_sweep_variants import _MODULE_VARIANTS
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_MODULES = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"
OUT_LOGIC = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
OUT_TAGS = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"

EN2T_COUNTS = (1, 2, 4, 8)
PLATFORM_UNITS = 100
UDT_NAME = "CloseUdt"
_UDT_MEMBERS = [MemberSpec(f"Mbr{i:02d}", "DINT") for i in range(8)]


def _write(l5x: str, out_dir: Path, name: str, description: str, category: str) -> int:
    out = out_dir / f"{name}.L5X"
    predicted = write_sample(l5x, out)
    append_manifest_row(name, description, category, out, predicted)
    print(f"Wrote {out} (predicted {predicted} bytes)")
    return 1


# ---------------------------------------------------------------------------
# A. EN2T alone, count-swept.
# ---------------------------------------------------------------------------

def arm_a_en2t_counts() -> int:
    """1756-EN2T repeated with NO downstream child, n = 1 / 2 / 4 / 8."""
    label, xml, source, _chain = _MODULE_VARIANTS["1756-EN2T"][0]
    assert xml.count("<Module ") == 1, "this arm needs the single-module variant"
    n = 0
    for count in EN2T_COUNTS:
        blocks = []
        for i in range(count):
            block = xml
            if i:
                block = block.replace('<Module Name="', f'<Module Name="C{i}_', 1)
            # Two collision classes, both caught by the pre-flight lint rather
            # than shipped: the backplane slot on the Upstream ICP port, and the
            # Ethernet address on the downstream port. Slots run from 1 since the
            # CPU holds slot 0.
            block = re.sub(r'(<Port Id="1" Address=")[^"]+(")',
                           lambda m: f"{m.group(1)}{i + 1}{m.group(2)}", block, count=1)
            block = re.sub(r'(Address=")192\.168\.[0-9]+\.[0-9]+(")',
                           lambda m: f"{m.group(1)}192.168.1.{40 + i}{m.group(2)}", block)
            blocks.append(block)
        l5x = build_l5x(target_name=f"CloseEn2tN{count:02d}", tags_xml="",
                        extra_modules_xml="\n".join(blocks))
        n += _write(
            l5x, OUT_MODULES, f"closeout_en2t_n{count:02d}",
            f"1756-EN2T x{count} ('{label}' shape, genericized structurally verbatim from "
            f"{source}), every copy directly under Local with NO downstream child module. "
            f"OQ-MODULEMARGINAL. modmarg_ob32chain_n{{01,02,04,08}} measures a flat 2,320 per "
            f"additional EN2T-plus-OB32 chain against a modelled 3,544 -- exact at three counts, "
            f"but one equation in two unknowns, because every copy there adds an EN2T AND the "
            f"OB32 behind it. Differencing this sweep against that one at the same count gives "
            f"1756-EN2T's own first-instance and repeat rates and leaves rack-aliased 1756-OB32 "
            f"by subtraction. It also separates the per-instance rate from the EN2T's "
            f"connection-variant spread, which currently runs 1,248 and 1,872 OVER on "
            f"modulesweep_1756_en2t_variant_1conn and _noconn and 908 UNDER on _1conn2 -- the "
            f"signature of a cost tracking the connection configuration rather than the catalog, "
            f"the same shape problem already proven for ETHERNET-MODULE.",
            "modules")
    return n


# ---------------------------------------------------------------------------
# B. CPT destination/operand type mismatch at two operand counts.
# ---------------------------------------------------------------------------

_CPT_CALLS = 100
# cptdest_*'s exact shape: four operand slots, three operators, one of them
# tier-2. Held byte-identical across every file in this arm.
_CPT_SLOTS = 4


def arm_b_cpt_type_mismatch() -> int:
    """cptdest_*'s two mismatched arms, with the MISMATCH COUNT swept.

    The tempting design -- vary the operand count -- cannot work: n operands in a
    flat expression forces n-1 operators, so operand count and operator count move
    together and the fit stays exactly as confounded as the four-operand
    measurement it was meant to unconfound.

    So the expression shape is pinned to cptdest's own -- four operand slots,
    three operators, one tier-2 -- and the only thing that moves is HOW MANY of
    those four slots hold the mismatched type. cptdest already supplies the
    4-of-4 point at +48 and +4; these files add 1-of-4 and 2-of-4:

        per MISMATCHED OPERAND   residual runs 12 / 24 / 48  (and 1 / 2 / 4)
        per CALL                 residual is flat at 48      (and at 4)

    Two readings, and they differ by 36 bytes per call on a 100-call file, which
    is 3,600 bytes against a baseline those files land on to the byte.
    """
    n = 0
    for dest_type, odd_type in (("DINT", "REAL"), ("REAL", "DINT")):
        base_type = dest_type
        for mismatched in (1, 2):
            # Slot types: `mismatched` of the four are the odd type, rest match
            # the destination. Slot ORDER is fixed with the odd ones first, and
            # position is already known not to matter -- cptpos_m{1..8} put a
            # tier-2 operator at eight different positions and seven of the eight
            # are byte-identical.
            slot_types = [odd_type] * mismatched + [base_type] * (_CPT_SLOTS - mismatched)
            names, tags = [], [tag_xml("CloseDest", dest_type)]
            for idx, t in enumerate(slot_types):
                name = f"{'R' if t == 'REAL' else 'L'}{idx}"
                names.append(name)
                tags.append(tag_xml(name, t))
            expr = f"{names[0]}+{names[1]}*{names[2]}+{names[3]}"
            rungs = "\n".join(rung_xml(i, f"CPT(CloseDest,{expr});") for i in range(_CPT_CALLS))
            l5x = build_l5x(
                target_name=f"CloseCpt{dest_type[0]}{odd_type[0]}M{mismatched}",
                tags_xml="\n".join(tags), extra_rungs_xml=rungs)
            n += _write(
                l5x, OUT_LOGIC,
                f"closeout_cptmix_d{dest_type.lower()}o{odd_type.lower()}_m{mismatched}",
                f"{_CPT_CALLS} identical CPT calls writing a {dest_type} destination, expression "
                f"`{expr}` -- cptdest_*'s exact shape, four operand slots and three operators with "
                f"one tier-2 -- of which {mismatched} of the 4 operands is {odd_type} and the rest "
                f"are {base_type}. OQ-CPTARRANGE. cptdest_* measured the all-mismatched case "
                f"exactly and linearly over a 100x count span (a DINT destination with REAL "
                f"operands is +48 per CPT, a REAL destination with DINT operands +4) but only at "
                f"4 of 4, where 48 is equally 48 per call or 12 per operand. Sweeping the operand "
                f"COUNT cannot separate those, because n operands forces n-1 operators; sweeping "
                f"the MISMATCH COUNT at a pinned shape does. Against cptdest's 4-of-4 point, a "
                f"per-operand term reads 12 / 24 / 48 and a per-call term reads a flat 48 -- 36 "
                f"bytes per call apart, 3,600 on this file, against a baseline the matched arms "
                f"land on to the byte.",
                "logic")
    return n


# ---------------------------------------------------------------------------
# C. Platform content unit, decomposed.
# ---------------------------------------------------------------------------

def arm_c_platform_unit() -> int:
    """The platform family's content unit, one component per file."""
    n = 0
    specs = (
        ("udttag", "one UDT tag per unit and nothing else"),
        ("dinttag", "one DINT tag per unit and nothing else"),
        ("rung", "one rung per unit and nothing else"),
    )
    for label, what in specs:
        tags, rungs, datatypes = [], [], ""
        if label == "udttag":
            tags = [tag_xml(f"CuUdt{i:04d}", UDT_NAME, udt_members=_UDT_MEMBERS)
                    for i in range(PLATFORM_UNITS)]
            datatypes = udt_xml(UDT_NAME, _UDT_MEMBERS)
            rungs = [rung_xml(0, "NOP();")]
        elif label == "dinttag":
            tags = [tag_xml(f"CuDint{i:04d}", "DINT") for i in range(PLATFORM_UNITS)]
            rungs = [rung_xml(0, "NOP();")]
        else:
            tags = [tag_xml("CuBit0", "BOOL"), tag_xml("CuBit1", "BOOL"),
                    tag_xml("CuDint0000", "DINT")]
            rungs = [rung_xml(i, f"XIC(CuBit0)MOV({i},CuDint0000)OTE(CuBit1);")
                     for i in range(PLATFORM_UNITS)]
        l5x = build_l5x(target_name=f"CloseUnit{label.capitalize()}",
                        tags_xml="\n".join(tags),
                        extra_datatypes_xml=datatypes,
                        extra_rungs_xml="\n".join(rungs))
        n += _write(
            l5x, OUT_TAGS, f"closeout_unit_{label}_n{PLATFORM_UNITS:03d}",
            f"{PLATFORM_UNITS} x {what}, on a standard 1756-L81E. OQ-REAL5069 spillover. "
            f"platform_plateql306_d* and platform_plateql81_d* over-predict by exactly 12n + 32 "
            f"-- identical to the byte on both processors, which is what closed the platform "
            f"question -- where each unit is one {UDT_NAME}-shaped UDT tag PLUS one DINT tag PLUS "
            f"one rung, all three scaling together. Two of the three are independently exact "
            f"elsewhere (dscale2_udt_u001_t{{001..500}} is flat in tag count over a 500x span, "
            f"instr_* sits in the universal +-8 band to 5,000 instructions), but that family's "
            f"rung is XIC(PeBit0)MOV(0,PeDint0000)OTE(PeBit1) -- three instructions with a LITERAL "
            f"MOV source -- which no isolating family covers. One component per file at a fixed "
            f"count puts the 12 on whichever one moves.",
            "tags")
    return n


def main() -> None:
    total = 0
    for fn in (arm_a_en2t_counts, arm_b_cpt_type_mismatch, arm_c_platform_unit):
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
