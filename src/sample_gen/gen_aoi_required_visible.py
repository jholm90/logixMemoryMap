"""AOI Parameter Required/Visible flag sweep (James, 2026-08-23): "You need
more work on your aoi analysis. Use some non-motion AOIs to start. The
samples I gave had the required flag checked for non-inout tags and this
requires a tag to be entered for that parameter on the calling instance.
If the required flag is not set, but the visible one is - it requires a
value to be present on the calling instance. If neither required or
visible is set then there is nowhere for that parameter to be used on the
calling instance and it is hidden from the ladder line and only visible in
the tag browser."

Real semantics confirmed against the corpus, not guessed: every prior
generator batch hardcoded Required="false" Visible="false" on every
Input/Output parameter (see builders.py's `_aoi_parameter_xml`, "a safe
default matching most of his examples") -- never actually varied it. This
generator does, using the same non-motion, plain-atomic-type AOI shapes
gen_aoi_sweep.py already established.

Real call-site argument syntax confirmed from
samples/local/SJ_Gormley_20251112_r02.L5X (multiple AOI calls, e.g.
`PTimer(NE_OverWidthPTMR,AxisPosition,100)`): `AoiName(InstanceTag,arg1,
arg2,...)`, positional args in Parameter declaration order, tags and
literal constants both appear directly as args. Cross-referencing that
same file's PTimer AOI *definition* against its real call: PTimer has 4
non-hidden Input params (2 Required="true", 2 Required="false"
Visible="true"), but the real call only supplies 2 values -- confirming
Required="false"/Visible="true" params CAN be omitted from the call
entirely (not guessed: this is the real corpus behavior). This generator
therefore never guesses an "omitted middle argument" shape (unclear
whether that needs a blank placeholder) -- it only ever omits OPTIONAL
params from the END of the argument list (matching the real PTimer
example's own pattern) or supplies all of them, never testing a
skip-in-the-middle shape.

Two things tested per AOI-flag combination:
  1. Definition-only (0 instances) -- does the Required/Visible attribute
     itself cost anything in the type definition storage?
  2. 1 instance WITH a real call-site rung invoking the AOI instruction,
     wiring every non-hidden param -- does the call site (estimated-tier
     logic, or some exact-tier thing) cost differently depending on how
     many params are actually wired vs how many exist as hidden storage?
     A separate "optional params omitted" variant re-uses the same
     all-visible-optional AOI but leaves the optional ones out of the call
     (matching the real PTimer precedent), to directly test whether
     omission itself changes size.

Run: python -m sample_gen.gen_aoi_required_visible
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi_reqvis", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _def_only(aoi_name: str, params: list[MemberSpec], out_name: str, desc: str) -> None:
    definition, _ = aoi_xml(aoi_name, params, [], [], [])
    l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
    _write(l5x, f"{out_name}_def_only", f"{desc}, 0 instances")


def _instance_with_call(
    aoi_name: str, params: list[MemberSpec], call_args: list[str], call_arg_tags_xml: str,
    out_name: str, desc: str,
) -> None:
    """1 instance tag + an actual rung calling the AOI instruction (a new
    test surface -- every prior AOI generator only ever created a backing
    tag, never an actual instruction call in logic, per the confirmed
    2026-08-20 finding that AOI-typed tags size identically to UDT
    instances with no logic parsing needed for THAT question. This
    specifically targets the calling-instance/Required/Visible question
    instead, which does need a real call.)."""
    definition, storage = aoi_xml(aoi_name, params, [], [], [])
    tag = tag_xml("TestInstance", aoi_name, udt_members=storage)
    call_args_str = ",".join(call_args)
    instr = f'{aoi_name}(TestInstance{"," + call_args_str if call_args_str else ""});'
    rung = rung_xml(0, instr)
    l5x = build_l5x(
        target_name=aoi_name, tags_xml=tag + "\n" + call_arg_tags_xml,
        extra_aoi_xml=definition, extra_rungs_xml=rung,
    )
    _write(l5x, out_name, desc)


# ---------------------------------------------------------------------------
# A. Required/Visible combo sweep, definition-only -- fixed at 4 DINT Input
#    params, only the Required/Visible attributes vary. Isolates whether
#    these flags cost anything in the AOI's own type-definition storage.
# ---------------------------------------------------------------------------

def group_def_flag_combos() -> None:
    combos = {
        "allhidden": dict(required=False, visible=False),   # existing default elsewhere
        "allrequired": dict(required=True, visible=True),   # Required implies Visible in real Logix
        "allvisibleoptional": dict(required=False, visible=True),
    }
    for combo_name, flags in combos.items():
        params = [MemberSpec(f"P{i}", "DINT", **flags) for i in range(4)]
        aoi_name = f"ReqVis{combo_name.capitalize()}"
        _def_only(aoi_name, params, f"reqvis_{combo_name}_n4",
                  f"AOI with 4 DINT Input params, all Required={flags['required']}/Visible={flags['visible']}")

    # Mixed: 2 required, 1 visible-optional, 1 hidden -- the realistic case
    # (James's own real AOIs mix all three within one definition).
    mixed = [
        MemberSpec("P0", "DINT", required=True, visible=True),
        MemberSpec("P1", "DINT", required=True, visible=True),
        MemberSpec("P2", "DINT", required=False, visible=True),
        MemberSpec("P3", "DINT", required=False, visible=False),
    ]
    _def_only("ReqVisMixed", mixed, "reqvis_mixed_n4",
              "AOI with 4 DINT Input params, mixed: 2 required, 1 visible-optional, 1 hidden")


# ---------------------------------------------------------------------------
# B. Same combos, but WITH a real call-site rung -- wiring every non-hidden
#    param to a real tag. Compares against group A's def_only numbers to
#    isolate any call-site-specific cost (estimated-tier logic, or an
#    exact-tier cost the def_only variant wouldn't show).
# ---------------------------------------------------------------------------

def group_call_site_full() -> None:
    combos = {
        "allhidden": ([], dict(required=False, visible=False)),
        "allrequired": (["CallArg0", "CallArg1", "CallArg2", "CallArg3"], dict(required=True, visible=True)),
        "allvisibleoptional": (["CallArg0", "CallArg1", "CallArg2", "CallArg3"], dict(required=False, visible=True)),
    }
    for combo_name, (arg_names, flags) in combos.items():
        params = [MemberSpec(f"P{i}", "DINT", **flags) for i in range(4)]
        aoi_name = f"ReqVisCall{combo_name.capitalize()}"
        arg_tags_xml = "\n".join(tag_xml(a, "DINT") for a in arg_names)
        _instance_with_call(
            aoi_name, params, arg_names, arg_tags_xml,
            f"reqvis_{combo_name}_call_full",
            f"AOI with 4 DINT Input params (Required={flags['required']}/Visible={flags['visible']}), "
            f"1 instance, call site wires all {len(arg_names)} non-hidden params",
        )


def group_call_site_omitted_optional() -> None:
    # Real corpus precedent (PTimer): a Required=false/Visible=true param
    # CAN be omitted from the call entirely, from the END of the arg list.
    # Params: 2 required (must always be wired) + 2 visible-optional. Two
    # variants: all 4 wired (baseline, matches group_call_site_full's
    # mixed-equivalent) vs only the 2 required ones wired, optional ones
    # omitted entirely -- tests whether omission itself changes size.
    params = [
        MemberSpec("P0", "DINT", required=True, visible=True),
        MemberSpec("P1", "DINT", required=True, visible=True),
        MemberSpec("P2", "DINT", required=False, visible=True),
        MemberSpec("P3", "DINT", required=False, visible=True),
    ]
    aoi_name = "ReqVisOmit"

    all_args = ["CallArg0", "CallArg1", "CallArg2", "CallArg3"]
    arg_tags_xml = "\n".join(tag_xml(a, "DINT") for a in all_args)
    _instance_with_call(
        aoi_name, params, all_args, arg_tags_xml,
        "reqvis_2req2optional_call_allwired",
        "AOI with 2 required + 2 visible-optional DINT Input params, 1 instance, call site wires all 4",
    )

    required_only_args = ["CallArg0", "CallArg1"]
    arg_tags_xml2 = "\n".join(tag_xml(a, "DINT") for a in required_only_args)
    _instance_with_call(
        aoi_name, params, required_only_args, arg_tags_xml2,
        "reqvis_2req2optional_call_optomitted",
        "AOI with 2 required + 2 visible-optional DINT Input params, 1 instance, "
        "call site wires only the 2 required (matches real PTimer precedent of omitting optional trailing params)",
    )


def main() -> None:
    group_def_flag_combos()
    group_call_site_full()
    group_call_site_omitted_optional()
    print("\nDone. 9 files.")


if __name__ == "__main__":
    main()
