"""AOI Parameter Required/Visible flag sweep, on non-motion AOIs.

Real semantics, established against the real exports rather than guessed:

  Required="true"  -- the parameter occupies a call-site argument slot and a
                      value must be supplied there. InOut parameters behave
                      this way unconditionally.
  Required="false"
  Visible="true"   -- the parameter is shown on the ladder line but is NOT a
                      call-site argument slot. It is never passed.
  both false       -- the parameter is hidden from the ladder line entirely
                      and is reachable only through the tag browser.

So a call site supplies exactly the Required (plus InOut) parameters, in
declaration order, after the leading instance tag:
`AoiName(InstanceTag,arg1,arg2,...)`. Tags and literal constants both appear
directly as arguments.

Across the real exports there are 917 AOI call sites and the argument count
after the instance tag equals the Required count at all 917. Those same
exports declare 120 Required="false" Visible="true" parameters, so this is
not an artifact of the real AOIs having no optional parameters -- one of them
declares three Required and four Visible-only parameters and is called with
three arguments everywhere. Required is not a prefix of the parameter list
either (13 of 48 real definitions interleave optional parameters between
required ones), so the unpassed parameters are not merely trailing ones.
Declaration position is irrelevant; the Required flag is the whole rule.

Every prior generator batch hardcoded Required="false" Visible="false" on
every Input/Output parameter (see builders.py's `_aoi_parameter_xml`) and
never varied it. This generator does, using the non-motion, plain-atomic-type
AOI shapes gen_aoi_sweep.py established.

A call that supplies a Visible-only parameter does not build: it draws
"Invalid number of arguments for instruction". Two files here once did that
and are gone -- there is no valid file that wires an optional parameter,
because wiring one is not a thing a call site can do. `lint.py`'s
`aoi_call_arg_count_mismatch` now enforces exact equality with the Required
count, so the shape cannot be reintroduced.

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
    finding that AOI-typed tags size identically to UDT
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
    # (a real AOIs mix all three within one definition).
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
        # No "allvisibleoptional" entry: with nothing Required there is no
        # call slot at all, so the only legal call is the 0-argument one
        # "allhidden" already covers.
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
    # 2 Required + 2 Visible-only DINT Input params, called with the 2
    # Required ones. This is the real-corpus shape: the optional parameters
    # exist in the definition, are shown on the ladder line, and are never
    # passed. There is deliberately no all-4-wired counterpart -- that call
    # does not build.
    params = [
        MemberSpec("P0", "DINT", required=True, visible=True),
        MemberSpec("P1", "DINT", required=True, visible=True),
        MemberSpec("P2", "DINT", required=False, visible=True),
        MemberSpec("P3", "DINT", required=False, visible=True),
    ]
    aoi_name = "ReqVisOmit"

    required_only_args = ["CallArg0", "CallArg1"]
    arg_tags_xml = "\n".join(tag_xml(a, "DINT") for a in required_only_args)
    _instance_with_call(
        aoi_name, params, required_only_args, arg_tags_xml,
        "reqvis_2req2optional_call_optomitted",
        "AOI with 2 required + 2 visible-optional DINT Input params, 1 instance, "
        "call site supplies the 2 required ones (the only legal arity)",
    )


def main() -> None:
    group_def_flag_combos()
    group_call_site_full()
    group_call_site_omitted_optional()
    print("\nDone. 7 files.")


if __name__ == "__main__":
    main()
