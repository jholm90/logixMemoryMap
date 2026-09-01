"""OQ-AOIDEF: does an AOI's internal Logic-routine CONTENT cost anything
beyond the already-confirmed Parameter/LocalTag declaration formula, and
does a second internal routine (real shape, not just Logic) cost its own
overhead? (2026-08-31, James: "So you closed aois but never put logic
inside? ... All aois have one subroutine but they can have more, see the
HomeToTorque aoi.")

Real, corpus-wide gap found in review: `aoi_xml()` (builders.py) has
hardcoded a self-closing `<Routine Name="Logic" Type="RLL"/>` for EVERY
AOI test file this project has ever generated -- $0 real internal-logic
content has ever been exercised in any AOI calibration file. The existing
`aoi_definition` formula (base + per_declared_item*count + name-length
term) is purely a Parameter/LocalTag declaration-cost model.

Real confidential-project review (not committed, never named beyond this
generic description) also found 8 of 39 real AOI definitions there have 2
internal RLL routines, not 1 -- e.g. HomeToTorque: Logic (21 rungs) +
EnableInFalse (1 rung). builders.py's aoi_xml() only ever supported a
single Logic routine before this fix (logic_rungs_xml/extra_routines_xml
added, backward-compatible -- confirmed byte-identical output for every
existing caller that doesn't pass the new params, only ExportDate
differs on any regeneration regardless of code changes).

Two groups:

  A. group_logic_content_scale -- Logic-routine content as the only
     variable (0/10/50/100 real instructions, held against a fixed
     Parameter/LocalTag shape identical across all 4 files so any
     Capacity change is unambiguously attributable to Logic content
     alone). If content is free (definition cost already captures
     everything), Capacity should stay flat; if not, it should scale.

  B. group_multi_routine -- the real HomeToTorque shape: Logic (21 real
     instructions) + a second EnableInFalse routine (1 rung), vs an
     otherwise-identical single-routine control (just Logic, same 21
     instructions, no second routine) -- isolates whether a second
     internal routine costs its own real overhead.

Run: python -m sample_gen.gen_aoi_internal_logic_isolation
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"

# James, 2026-08-31, real, caught on his own re-conversion: "conditional
# instructions like EQU with no operand at the end of the rung or a
# NOP() instruction. this is basic ladder logic." The original bare
# "EQU(In0,In1)" had no output instruction -- fixed to end in a real
# output (In2/Out0 are both BOOL, so XIC(In2)OTE(Out0) was already valid
# and stays unchanged; the bit-level XIC/XIO/OTE/OTU/OTL/ONS constraint
# doesn't apply here since neither operand is SINT/INT/DINT).
_MIX = ["MOV(In0,In1)", "XIC(In2)OTE(Out0)", "CLR(Loc0)", "ADD(In0,In1,Loc1)", "EQU(In0,In1)OTE(Out0)"]


def _logic_rungs(instr_count: int) -> str:
    if instr_count == 0:
        return ""
    pieces = []
    rung_idx = 0
    total = 0
    while total < instr_count:
        piece = _MIX[rung_idx % len(_MIX)]
        pieces.append(rung_xml(rung_idx, piece + ";"))
        total += piece.count("(")
        rung_idx += 1
    return "".join(pieces)


def _shape() -> tuple[list[MemberSpec], list[MemberSpec], list[MemberSpec]]:
    inputs = [MemberSpec("In0", "DINT"), MemberSpec("In1", "DINT"), MemberSpec("In2", "BOOL")]
    outputs = [MemberSpec("Out0", "BOOL")]
    locals_ = [MemberSpec("Loc0", "DINT"), MemberSpec("Loc1", "DINT")]
    return inputs, outputs, locals_


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_logic_content_scale() -> None:
    inputs, outputs, locals_ = _shape()
    for instr_count in (0, 10, 50, 100):
        aoi_name = f"AoiLogicScale{instr_count:03d}"
        logic_rungs = _logic_rungs(instr_count)
        definition, storage = aoi_xml(
            aoi_name, inputs, outputs, [], locals_, logic_rungs_xml=logic_rungs,
        )
        l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
        _write(
            l5x, f"aoi_logic_scale_{instr_count:03d}",
            f"AOI definition (3 In/1 Out/2 Local, def_only -- 0 instances), Logic routine "
            f"containing ~{instr_count} real instructions -- OQ-AOIDEF internal-logic-content "
            f"isolation: does Logic-routine content cost anything beyond the confirmed "
            f"Parameter/LocalTag declaration formula, or does it stay flat at every content "
            f"size the way this project's aoi_definition formula currently assumes?",
        )


def group_multi_routine() -> None:
    inputs, outputs, locals_ = _shape()
    logic_rungs = _logic_rungs(50)

    # Control: single Logic routine only.
    definition_ctl, _ = aoi_xml(
        "AoiMultiRoutineCtl", inputs, outputs, [], locals_, logic_rungs_xml=logic_rungs,
    )
    l5x_ctl = build_l5x(target_name="AoiMultiRoutineCtl", tags_xml="", extra_aoi_xml=definition_ctl)
    _write(
        l5x_ctl, "aoi_multiroutine_control",
        "AOI definition, same shape/Logic-content as aoi_multiroutine_real (50 real "
        "instructions), but ONLY the one Logic routine -- control for aoi_multiroutine_real.",
    )

    # Real shape: Logic + a second EnableInFalse routine, matching HomeToTorque
    # (confidential real project, not committed) exactly -- 1 rung, XIC/OTE shape.
    enable_in_false_xml = (
        '<Routine Name="EnableInFalse" Type="RLL">'
        f"<RLLContent>{rung_xml(0, 'XIC(In2)OTE(Out0);')}</RLLContent>"
        "</Routine>"
    )
    definition_real, _ = aoi_xml(
        "AoiMultiRoutineReal", inputs, outputs, [], locals_,
        logic_rungs_xml=logic_rungs, extra_routines_xml=enable_in_false_xml,
    )
    l5x_real = build_l5x(target_name="AoiMultiRoutineReal", tags_xml="", extra_aoi_xml=definition_real)
    _write(
        l5x_real, "aoi_multiroutine_real",
        "AOI definition with 2 internal RLL routines (Logic, 50 real instructions + "
        "EnableInFalse, 1 rung) -- the real shape found in a confidential project's HomeToTorque "
        "AOI (not committed, never named beyond this generic description). OQ-AOIDEF: does a "
        "second internal routine cost its own real overhead beyond aoi_multiroutine_control?",
    )


def main() -> None:
    group_logic_content_scale()
    group_multi_routine()
    print("\nDone. 6 files.")


if __name__ == "__main__":
    main()
