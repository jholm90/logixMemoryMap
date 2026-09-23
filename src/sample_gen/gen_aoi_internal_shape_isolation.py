"""Which AOI-internal rung shape is Studio rejecting? (OQ-AOIINTERNALLOGIC)

The AOI-internal-logic weighting is wired and was reported as "essentially
exact at every point tested, max error cut from 12.02% to 0.55%". It was fitted
against six files, and five of those six CAPTURED WITH BUILD ERRORS:

    aoi_logic_scale_000        0 errors     (the empty-shell baseline)
    aoi_logic_scale_010        1 error
    aoi_logic_scale_050        8 errors
    aoi_logic_scale_100       16 errors
    aoi_multiroutine_control   8 errors
    aoi_multiroutine_real      8 errors

No error text was ever recorded, and all six files had since been deleted from
the repo entirely, so nothing could be re-examined. The error count rises with
rung count, which means a REPEATING rung shape in the generator's 5-shape mix
is being rejected -- Studio imports the rest of the project, `actual_bytes` gets
filled in, and the capture silently measures a project missing a fraction of
the logic it was built to measure. Per CLAUDE.md that makes every one of those
rows SUSPECT: the measured bytes under-state the real cost, so the weighting
derived from them is very likely under-charging AOI internal logic. That
matters because real AOIs are logic-dense -- 39 real AOI definitions in one
production program carry 573 rungs between them.

An earlier attempt at this diagnosis is recorded here because it was WRONG and
the wrong answer is easy to reach twice: the suspect shape looked like
`MOV(In0,In1)`, on the theory that an AOI's Input parameters are read-only
inside its own logic. They are not. Real shipping AOIs write to their Input
parameters constantly -- `MOV(RawInput,RawMax)`, `OTU(HMI_ResetStats)` in the
real corpus -- because an Input is a local copy made at invocation, not a
reference; only InOut is by-reference and only Output flows back. Any rule
based on that premise fires on 133 committed files including all four real
production programs, which demonstrably compile.

Nor does arithmetic on the shape counts settle it. The mix cycles 5 shapes, so
at 13/42/78 rungs each shape appears a known number of times, and NO single
shape appears 1, 8 and 16 times respectively: `CLR(Loc0)` appears 8 and 16 at
n=50/100 but 3 at n=10, and `MOV(In0,In1)` appears 2, 8 and 15. Either the
error is not one-per-rung, or more than one shape is involved.

So this measures it instead of guessing. Each of the five mix shapes gets its
own file at three rung counts, with nothing else in the AOI's logic. The
recorded error count then names the offender directly: a shape rejected once
per rung shows error_count tracking the rung count in its own files and zero in
the other four shapes' files. A shape-independent cause shows up as every file
erroring equally, including the zero-logic control.

The rung mix is reproduced EXACTLY as the captured files have it, MOV(In0,In1)
included -- the point is to identify what the real captures hit, and changing
the shapes would measure a different question.

If this comes back with every file at zero errors, the cause was in the
surrounding project structure rather than the rungs, and the next step is the
raw Studio 5000 error-log line for one of the original six files rather than
another round of inference.

Run: python -m sample_gen.gen_aoi_internal_shape_isolation
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"

# Verbatim from gen_aoi_internal_logic_isolation.py's _MIX, in its order, so a
# shape's index here matches its index there.
SHAPES = (
    ("mov", "MOV(In0,In1)"),
    ("xicote", "XIC(In2)OTE(Out0)"),
    ("clr", "CLR(Loc0)"),
    ("add", "ADD(In0,In1,Loc1)"),
    ("equote", "EQU(In0,In1)OTE(Out0)"),
)
RUNG_COUNTS = (1, 5, 10)


def _shape_members() -> tuple[list[MemberSpec], list[MemberSpec], list[MemberSpec]]:
    """The same 3 In / 1 Out / 2 Local shape the captured sweep used, so the
    parameter declarations are not a variable here."""
    inputs = [MemberSpec("In0", "DINT"), MemberSpec("In1", "DINT"), MemberSpec("In2", "BOOL")]
    outputs = [MemberSpec("Out0", "BOOL")]
    locals_ = [MemberSpec("Loc0", "DINT"), MemberSpec("Loc1", "DINT")]
    return inputs, outputs, locals_


def _write(l5x: str, out_name: str, description: str) -> int:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 1


def _build(aoi_name: str, rungs_xml: str) -> str:
    inputs, outputs, locals_ = _shape_members()
    definition, _storage = aoi_xml(aoi_name, inputs, outputs, [], locals_,
                                   logic_rungs_xml=rungs_xml)
    return build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)


def group_one_shape_per_file() -> int:
    n = 0
    for label, instr in SHAPES:
        for count in RUNG_COUNTS:
            rungs = "".join(rung_xml(i, instr + ";") for i in range(count))
            aoi_name = f"AoiShp{label.capitalize()}N{count:02d}"
            n += _write(
                _build(aoi_name, rungs), f"aoishape_{label}_n{count:02d}",
                f"AOI definition (3 In / 1 Out / 2 Local), internal Logic routine containing "
                f"{count} identical rung(s) of `{instr};` and nothing else, 0 instances -- "
                f"OQ-AOIINTERNALLOGIC error-shape isolation. Five of the six files the "
                f"AOI-internal-logic weighting was fitted against captured WITH Studio build "
                f"errors (1 / 8 / 16 / 8 / 8 against a 0-error baseline), no error text was "
                f"recorded, and the files had since been deleted. The count rises with rung "
                f"count, so a repeating shape in that generator's 5-shape mix is being "
                f"rejected while Studio imports the rest -- which fills in actual_bytes from a "
                f"project missing part of its logic. Each shape now gets its own file at 1/5/10 "
                f"rungs so the recorded error count names the offender directly instead of "
                f"being inferred. Shapes are verbatim from the captured mix, MOV(In0,In1) "
                f"included; changing them would measure a different question")
    return n


def group_controls() -> int:
    """Zero-logic and full-mix controls.

    The zero-logic file separates a shape-specific cause from anything in the
    surrounding project structure: if it errors too, no rung is at fault. The
    full-mix file at 10 rungs reproduces aoi_logic_scale_010's own logic
    exactly, so its error count is directly comparable to that row's recorded 1.
    """
    n = 0
    n += _write(
        _build("AoiShpEmpty", ""), "aoishape_control_empty",
        "AOI definition (3 In / 1 Out / 2 Local), internal Logic routine EMPTY, 0 instances "
        "-- OQ-AOIINTERNALLOGIC error-shape isolation control. Separates a rung-shape cause "
        "from the surrounding project structure: if this errors as well then no rung is at "
        "fault. aoi_logic_scale_000 is the same idea and captured at 0 errors, but it has "
        "since been rebuilt from a changed builder, so this is the current-content control")
    mix_rungs = "".join(
        rung_xml(i, SHAPES[i % len(SHAPES)][1] + ";") for i in range(13))
    n += _write(
        _build("AoiShpMix13", mix_rungs), "aoishape_control_mix13",
        "AOI definition (3 In / 1 Out / 2 Local), internal Logic routine with 13 rungs of "
        "the same 5-shape cycle aoi_logic_scale_010 draws from (3/3/3/2/2), 0 instances "
        "-- OQ-AOIINTERNALLOGIC error-shape isolation control. Its error count is directly "
        "comparable to aoi_logic_scale_010's recorded 1 -- the BYTES are not, since the AOI "
        "type name is a different length and that carries its own cost. If this file "
        "reproduces that 1 then the per-shape files above localize it, and if it comes back "
        "clean then the original error was in something the sweep has since changed")
    return n


def _mix_rungs(instr_count: int) -> str:
    """The five-shape cycle packed until `instr_count` instructions are placed --
    the same packer gen_aoi_internal_logic_isolation._logic_rungs uses, so a file
    built here is directly comparable to an aoi_logic_scale_* file at the same
    count. Note the packer counts INSTRUCTIONS, not rungs: 10 instructions is 7
    rungs, not 10, which is why aoi_logic_scale_010 holds 7."""
    pieces = []
    rung_idx = 0
    total = 0
    while total < instr_count:
        piece = SHAPES[rung_idx % len(SHAPES)][1]
        pieces.append(rung_xml(rung_idx, piece + ";"))
        total += piece.count("(")
        rung_idx += 1
    return "".join(pieces)


_ENABLE_IN_FALSE_ROUTINE_XML = (
    '<Routine Name="EnableInFalse" Type="RLL">'
    f"<RLLContent>{rung_xml(0, 'XIC(In2)OTE(Out0);')}</RLLContent>"
    "</Routine>"
)


def group_error_reproduction() -> int:
    """Re-emit what the five errored calibration rows carry, under NEW ids.

    Those rows -- aoi_logic_scale_{010,050,100} at 1/8/16 errors and
    aoi_multiroutine_{control,real} at 8 -- were captured against
    content the repo no longer holds: the files were deleted, then rebuilt
    on a builder that had moved, and the step-2b gate reports all five
    STALE. Nothing can be concluded from those numbers; the shapes have to be
    re-captured, not re-read.

    Three files, not six. The 15-file single-shape sweep and aoishape_control_mix13
    already captured at ZERO errors and between them cover everything the 000 and
    010 points test -- aoi_logic_scale_010's Logic routine is 7 rungs carrying 10
    instructions of exactly those five shapes. What no clean-capture file covers is
    larger content and the second internal routine.

    New ids on purpose: regenerating in place would leave old captured
    actual_bytes attached to different content, the failure already documented for
    asmclose_1756_ob32_rackaliased.
    """
    n = 0
    inputs, outputs, locals_ = _shape_members()
    for label, instr_count, second_routine in (
        ("mix050", 50, False), ("mix100", 100, False), ("tworoutine", 50, True),
):
        aoi_name = "AoiErr" + label[0].upper() + label[1:]
        definition, _storage = aoi_xml(
            aoi_name, inputs, outputs, [], locals_,
            logic_rungs_xml=_mix_rungs(instr_count),
            extra_routines_xml=(_ENABLE_IN_FALSE_ROUTINE_XML if second_routine else ""),
)
        l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
        second = (", PLUS a second EnableInFalse routine of one rung -- the real "
                  "HomeToTorque shape" if second_routine else "")
        n += _write(
            l5x, f"aoierr_{label}",
            f"AOI definition (3 In / 1 Out / 2 Local), internal Logic routine carrying "
            f"{instr_count} instructions of the same five-shape mix aoi_logic_scale_* uses"
            f"{second}, 0 instances -- OQ-AOIINTERNALLOGIC error reproduction. The five errored "
            f"calibration rows were captured against content deleted and rebuilt "
            f" on a changed builder, so the step-2b gate reports all five STALE and "
            f"their error counts cannot be used. This re-emits the shape under a NEW id so the "
            f"count measures content the repo actually holds. Segment 15 captured all five shapes "
            f"individually, and the 13-rung mix, at ZERO errors -- so a clean result here means "
            f"the errors belonged to the old builder output and the thread closes, while an error "
            f"localizes the cause to content SIZE or the second routine, neither of which any "
            f"clean-capture file exercises.")
    return n


def main() -> None:
    total = 0
    for fn in (group_one_shape_per_file, group_controls, group_error_reproduction):
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
