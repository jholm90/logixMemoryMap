"""A DriveAxis-shaped AOI: AXIS parameter + nested AOI instance.

James, 2026-09-05: *"I want you to emulate something like the DriveAxis AOI
with axis input and a nested aoi instance as I think there's room for
improvement and testing there."*

He is right that there is room, and the corpus shows why. `DriveAxis` is
the single largest AOI definition charge in MurrayBros at **18,080 bytes**
-- more than the whole task/program shell of that file -- and NOTHING in
the generated corpus resembles it. Two structural features it has that no
synthetic file covers:

  1. **An AXIS_CIP_DRIVE parameter.** Every AXIS_* test in this project is
     a controller-scope TAG. An axis passed as an AOI PARAMETER is a
     different thing: an InOut/reference-shaped parameter to a predefined
     motion structure. Whether it costs the axis's full structure size,
     a reference, or nothing is completely unmeasured. Real usage is not
     rare -- MurrayBros alone has three (DriveAxis, HomeToTorque,
     VirtualAxis).
  2. **A nested AOI instance as a LocalTag.** MurrayBros has 14 of these
     (TS_PF525 holds a TS_VFD, T_DST holds three T_ADDs, TierPinchAOI
     holds a Debounce). The engine resolves them -- `Stacker` sizes
     through PTimer/Debounce fine -- but resolving is not the same as
     being CORRECT, and there is no isolation test proving the nested
     instance costs what the model says.

Also covered because the same real file forced the question: a **UDT with
an AOI-typed member**. MurrayBros has **125** of them. That path is
exercised by real files constantly and by zero synthetic ones.

The design is a ladder, not a single replica. A replica would confirm one
number and explain nothing; each group below varies ONE thing against a
fixed baseline so the cost of that thing is read directly:

  daxis_baseline          the AOI with no axis param and no nesting
  daxis_axis_{cip,virtual,servo}
                          + one AXIS_* parameter, nothing else changed.
                          Subtracting the baseline gives the axis-param
                          cost, per axis type.
  daxis_axisn_k{1,2,3}    axis parameter COUNT 1..3 -- per-parameter or
                          once-per-definition?
  daxis_nest_k{0,1,2,4}   nested AOI LocalTag count. k=0 is the baseline,
                          so the slope is the nested-instance cost.
  daxis_nest_depth{1,2,3} nesting DEPTH (A holds B holds C) at constant
                          total instance count -- does depth cost more
                          than breadth, which is what a naive recursive
                          sizer would get wrong?
  daxis_udtaoi_k{1,2,4}   a UDT with N AOI-typed members -- the 125-member
                          real pattern, isolated.
  daxis_full              all of it together at DriveAxis's real scale
                          (20 params / 60 locals / 53 rungs), as the
                          composite check that the isolated parts add up.

The inner AOI is deliberately small and fixed across every file, so its own
size never varies and cannot be confused with the cost of nesting it.

Run: python -m sample_gen.gen_driveaxis_aoi
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import (
    MemberSpec, aoi_xml, rung_xml, rungs_xml, tag_xml, udt_xml,
)
from sample_gen.gen_axis_composite import _AXIS_TAG_XML
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, predicted_bytes
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "driveaxis"

# The nested AOI: small, fixed, identical in every file that uses it, so
# its own definition cost is a constant and only the NESTING varies.
_INNER_NAME = "InnerHelper"
_INNER_IN = [MemberSpec("InA", "DINT", required=True)]
_INNER_OUT = [MemberSpec("OutA", "BOOL", required=True)]
_INNER_LOCAL = [MemberSpec("Work", "DINT")]


def _inner():
    return aoi_xml(_INNER_NAME, input_params=_INNER_IN, output_params=_INNER_OUT,
                   local_tags=_INNER_LOCAL, logic_rungs_xml=rung_xml(0, "OTE(OutA);"))


def _write(l5x: str, name: str, description: str) -> None:
    out = OUT_ROOT / f"{name}.L5X"
    lint_or_raise(l5x, context=str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(l5x, encoding="utf-8")
    append_manifest_row(name, description, "driveaxis", out, predicted_bytes(l5x))
    print(f"Wrote {out}")


def _outer(name: str, extra_params=None, extra_locals=None, n_rungs: int = 4):
    """The DriveAxis-shaped outer AOI, with a fixed baseline of members so
    every file differs only by what the caller adds."""
    ins = [MemberSpec("Enable", "BOOL", required=True),
           MemberSpec("Cmd", "DINT", required=True)]
    outs = [MemberSpec("Done", "BOOL", required=True)]
    locals_ = [MemberSpec("Work1", "REAL"), MemberSpec("Work2", "DINT")]
    return aoi_xml(
        name,
        input_params=ins + list(extra_params or []),
        output_params=outs,
        local_tags=locals_ + list(extra_locals or []),
        logic_rungs_xml=rungs_xml(n_rungs, lambda i: "XIC(Enable)OTE(Done);"),
    )


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    inner_xml, inner_storage = _inner()

    # --- baseline: no axis parameter, no nesting -------------------------
    outer, storage = _outer("DaxOuter")
    _write(
        build_l5x(target_name="DaxBase",
                  tags_xml=tag_xml("Inst", "DaxOuter", udt_members=storage),
                  extra_aoi_xml=outer),
        "daxis_baseline",
        "DriveAxis-shaped AOI with NO axis parameter and NO nested AOI -- the "
        "control every other file in this batch subtracts against",
    )

    # --- one AXIS_* parameter, by axis type ------------------------------
    for axis_type in ("AXIS_CIP_DRIVE", "AXIS_VIRTUAL", "AXIS_SERVO"):
        p = MemberSpec("Drive_Axis", axis_type, required=True)
        outer, storage = _outer("DaxOuter", extra_params=[p])
        _write(
            build_l5x(target_name=f"DaxAx{axis_type[5:9]}",
                      tags_xml="\n".join([_AXIS_TAG_XML,
                                          tag_xml("Inst", "DaxOuter", udt_members=storage)]),
                      extra_aoi_xml=outer),
            f"daxis_axis_{axis_type[5:].lower()}",
            f"Baseline + ONE {axis_type} AOI parameter. Minus daxis_baseline this "
            f"is the cost of passing an axis INTO an AOI -- every existing AXIS_* "
            f"test in this project is a controller TAG, never a parameter",
        )

    # --- axis parameter COUNT --------------------------------------------
    for k in (1, 2, 3):
        ps = [MemberSpec(f"Axis{i}", "AXIS_CIP_DRIVE", required=True) for i in range(k)]
        outer, storage = _outer("DaxOuter", extra_params=ps)
        _write(
            build_l5x(target_name=f"DaxAxN{k}",
                      tags_xml="\n".join([_AXIS_TAG_XML,
                                          tag_xml("Inst", "DaxOuter", udt_members=storage)]),
                      extra_aoi_xml=outer),
            f"daxis_axisn_k{k}",
            f"{k} AXIS_CIP_DRIVE parameter(s) on one AOI -- per-parameter cost or "
            f"once-per-definition?",
        )

    # --- nested AOI instance COUNT ---------------------------------------
    for k in (0, 1, 2, 4):
        locs = [MemberSpec(f"Helper{i}", _INNER_NAME, nested_members=tuple(inner_storage))
                for i in range(k)]
        outer, storage = _outer("DaxOuter", extra_locals=locs)
        _write(
            build_l5x(target_name=f"DaxNest{k}",
                      tags_xml=tag_xml("Inst", "DaxOuter", udt_members=storage),
                      extra_aoi_xml="\n".join([inner_xml, outer])),
            f"daxis_nest_k{k}",
            f"{k} nested {_INNER_NAME} AOI instance(s) as LocalTags of the outer AOI "
            f"-- the real MurrayBros pattern (14 real occurrences). Inner AOI is "
            f"byte-identical in every file so only the nesting varies",
        )

    # --- UDT with AOI-typed members --------------------------------------
    for k in (1, 2, 4):
        mems = [MemberSpec(f"Aoi{i}", _INNER_NAME, nested_members=tuple(inner_storage))
                for i in range(k)] + [MemberSpec("Plain", "DINT")]
        _write(
            build_l5x(target_name=f"DaxUdtAoi{k}",
                      tags_xml=tag_xml("UdtInst", "UdtWithAoi", udt_members=mems),
                      extra_datatypes_xml=udt_xml("UdtWithAoi", mems),
                      extra_aoi_xml=inner_xml),
            f"daxis_udtaoi_k{k}",
            f"UDT with {k} AOI-typed member(s) -- MurrayBros has 125 of these and "
            f"the generated corpus has none. Engine resolves the path today; this "
            f"proves whether it resolves to the RIGHT number",
        )

    # --- composite at real DriveAxis scale --------------------------------
    ps = [MemberSpec("Drive_Axis", "AXIS_CIP_DRIVE", required=True)]
    ps += [MemberSpec(f"B{i}", "BOOL", required=True) for i in range(13)]
    ps += [MemberSpec(f"R{i}", "REAL", required=True) for i in range(3)]
    locs = [MemberSpec("Helper0", _INNER_NAME, nested_members=tuple(inner_storage))]
    locs += [MemberSpec(f"LR{i}", "REAL") for i in range(30)]
    locs += [MemberSpec(f"LD{i}", "DINT") for i in range(18)]
    outer, storage = _outer("DaxFull", extra_params=ps, extra_locals=locs, n_rungs=53)
    _write(
        build_l5x(target_name="DaxFull",
                  tags_xml="\n".join([_AXIS_TAG_XML,
                                      tag_xml("Inst", "DaxFull", udt_members=storage)]),
                  extra_aoi_xml="\n".join([inner_xml, outer])),
        "daxis_full",
        "Composite at the real DriveAxis's scale (1 axis param + 16 atomic params, "
        "60 local tags incl. 1 nested AOI, 53 rungs). Checks that the isolated "
        "costs above actually ADD UP on something the size of the real thing -- "
        "the real DriveAxis is charged 18,080 bytes today, unvalidated",
    )
    print("\nDone.")


if __name__ == "__main__":
    main()
