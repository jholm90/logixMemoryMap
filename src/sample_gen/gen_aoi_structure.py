"""AOI STRUCTURAL cost space -- the batch that has to work on other
people's AOIs, not the.

2026-09-05: *"Like I said previously Murray AOIs are the same on
other projects. What new tests are you going to generate now for
improving?"* and, the same day: *"Keep in mind that I plan on sharing this
for people outside my company and their code will be very different and
use different aois."*

Those two together rule out the obvious move. MurrayBros' residual
correlates hardest with AOI structure (aoiaxisparam +0.889, aoirungs
+0.848, aoidefs +0.838, aoilocals +0.835), and the tempting fix is to fit
per-AOI corrections against the shared definitions that appear across the
nine projects. That fit would be worth exactly nothing to a stranger
importing an L5X full of AOIs this project has never seen. The cost has to
be a function of AOI *structure*, so every file here varies one structural
property and holds the rest fixed.

WHAT THE MODEL CURRENTLY PRICES, read straight out of
`compute_aoi_definition_cost` + `AoiDefinitionModel.bytes_for`:

    base 1184
  + per-type rate (BOOL 16 / SINT 18 / INT 18 / LINT 24, single-type defs
    only) or flat 20 per declared item
  + AOI TYPE-name length buckets

and that is all. Everything below is therefore priced at exactly ZERO
today, which is a hypothesis nothing has ever tested:

  1. **Member name length.** The AOI's own type name is priced; its
     members' names are not. Real corpus: 2,120 AOI Parameters/LocalTags,
     mean name length 12.1 chars, max 32. Tag names elsewhere in this
     model cost 8 bytes per 8-character chunk. If AOI members follow any
     similar rule, a real AOI-dense file is under-charged by tens of KB --
     and a stranger's naming convention moves it, which is exactly the
     kind of term that must not be fitted from one company's files.
  2. **Member descriptions.** 803 of those 2,120 carry one. No generated
     file has ever emitted a single member description, so "descriptions
     are free" is an assumption, not a measurement. (Routine COMMENTS were
     measured free -- OQ-STCOMMENT -- but a comment lives in ladder text
     and a member description lives in the type definition; they are not
     the same storage.)
  3. **InOut parameters.** `compute_aoi_definition_cost` skips them
     entirely, so an AOI with 48 InOut params is charged identically to
     one with none. 94 real InOut params on file, and they are the ONLY
     legal way to pass an array, a STRING, a MESSAGE or a UDT into an AOI
     -- so a stranger's AOI library will be full of them.
  4. **Predefined-structure members.** TIMER (557 real member uses),
     DateTime (120), COUNTER (66), STRING (58), MOTION_INSTRUCTION (36),
     MESSAGE (15) -- every one falls off the end of the per-type table
     onto the flat atomic rate. Never generated once before today; see
     predefined_members.py.
  5. **Array dimensions.** An AOI member is counted once whether it is
     scalar or `Dimensions="1024"`. 46 real dimensioned AOI members.
  6. **Member counts past the fitted range.** Real AOIs run to 102 params
     / 128 locals / 85 internal rungs (median 12/11/11). The generated
     corpus tops out around 6/2/1. This is the identical extrapolation
     shape as OQ-SHELLSCALE (a constant fitted at n=2, applied at n=200,
     wrong by 8 bytes/unit) and OQ-DEFSCALE -- both real, both caught only
     by building the ladder.
  7. **Extra internal routines.** 7 of 81 real AOI definitions carry an
     EnableInFalse and/or Prescan routine besides Logic.

GROUPS (56 files, every one answering a live question -- 2026-08-25: 
*"Don't just fill up the minimum 60 test roster with filler work"*):

  aoistr_namelen_c{04..40}        7  member NAME length, 20 DINT params
  aoistr_desc_l{000..256} + 4     8  member/AOI-level DESCRIPTION text
  aoistr_inout_n{00,04,16,48}     4  InOut param count (priced 0 today)
  aoistr_predef_*                11  TIMER/COUNTER/MOTION/STRING/MESSAGE
  aoistr_dim_*                    9  array-dimensioned members
  aoistr_scale_*                 12  params/locals/rungs to the real p90
  aoistr_routines_n{1,2,3}        3  internal routine count, rungs fixed
  aoistr_real_{median,p90}        2  composite: do the isolated parts add?

Everything is definition-only except the two composites: an instance tag
would add its own tag_overhead + member storage on top and blur the exact
quantity being measured. Platform is the wrapper default 1756-L81E
fw35.05, chosen deliberately -- it is the same processor and firmware as
MurrayBros and MRFP_Edger, so nothing here is confounded by the baseline
question in OQ-BASELINE-PROCFW.

Run: python -m sample_gen.gen_aoi_structure
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row
from sample_gen.predefined_members import predef_array_member, predef_member
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoistructure"
CATEGORY = "aoistructure"

# One fixed AOI type name across the whole batch. AOI type-name length IS
# priced (name_length_bucket_bytes), so letting it vary would contaminate
# every other reading here. 15 chars = bucket 1 for all 55 files.
AOI_TYPE = "AoiStructProbe"


def _write(l5x: str, name: str, description: str) -> None:
    from sample_gen.manifest import write_sample

    out = OUT_ROOT / f"{name}.L5X"
    predicted = write_sample(l5x, out)
    append_manifest_row(name, description, CATEGORY, out, predicted)
    print(f"Wrote {out}")


def _member_name(prefix: str, index: int, total_len: int) -> str:
    """A valid Logix identifier of EXACTLY total_len characters.

    Padding is filler LETTERS, not underscores. Real Logix name rules,
    confirmed by a real Studio 5000 import failure on this batch
    ("Error creating 'Parameter' (Invalid name.)" on `InParam00___`):

      - no TRAILING underscore
      - no SEQUENTIAL underscores
      - no LEADING digit

    The first version padded with "_" to hit an exact length, which
    violates the first two rules at once and broke 52 of the 56 files here.
    Length is still exact, because the whole point of the namelen group is
    that only the character count varies -- the filler just has to be legal.
    """
    if total_len < 3:
        raise ValueError("member names need room for a 2-digit index plus a letter")
    stem = f"{prefix[: total_len - 2]}{index:02d}"
    return stem + "x" * (total_len - len(stem))


def _def_only(aoi_definition: str, target: str) -> str:
    """A project carrying nothing but the AOI definition under test. The
    same `*_def_only` convention the existing 127 AOI calibration files
    use -- no instance tag, so the number captured is the definition's own
    cost and nothing else."""
    return build_l5x(target_name=target, tags_xml="", extra_aoi_xml=aoi_definition)


def _dint_params(count: int, name_len: int = 12, description: str | None = None):
    return [
        MemberSpec(_member_name("InParam", i, name_len), "DINT",
                   required=True, description=description)
        for i in range(count)
    ]


def _dint_locals(count: int, name_len: int = 12, description: str | None = None):
    return [
        MemberSpec(_member_name("LocalWrk", i, name_len), "DINT", description=description)
        for i in range(count)
    ]


def _group_namelen() -> None:
    """20 DINT Input params, IDENTICAL in every way except how many
    characters their names use. Any slope is pure member-name cost."""
    for n in (4, 8, 12, 16, 20, 28, 40):
        definition, _ = aoi_xml(AOI_TYPE, input_params=_dint_params(20, name_len=n))
        _write(
            _def_only(definition, f"AoiNameLen{n:02d}"),
            f"aoistr_namelen_c{n:02d}",
            f"AOI definition only: 20 DINT Input params whose member names are "
            f"exactly {n} characters. Member NAME length is priced at 0 by the "
            f"current model (only the AOI TYPE name is priced); real AOI members "
            f"average 12.1 chars and run to 32, and tag names elsewhere in this "
            f"model cost 8 bytes per 8-char chunk. Slope across c04..c40 is the "
            f"per-member name cost, if any.",
        )


def _group_description() -> None:
    """Member descriptions at four text lengths, then descriptions on
    locals too, then the AOI's own Description/RevisionNote."""
    for n in (0, 16, 64, 256):
        desc = ("D" * n) if n else None
        definition, _ = aoi_xml(AOI_TYPE, input_params=_dint_params(20, description=desc))
        _write(
            _def_only(definition, f"AoiDesc{n:03d}"),
            f"aoistr_desc_l{n:03d}",
            f"AOI definition only: 20 DINT Input params, each carrying a "
            f"{n}-character <Description> ({n}=0 is the no-description baseline). "
            f"803 of 2,120 real AOI members carry a description and no generated "
            f"file has ever emitted one, so 'member descriptions are free' has "
            f"never been measured. l016->l256 also separates a flat per-described-"
            f"member cost from a per-character one.",
        )

    definition, _ = aoi_xml(
        AOI_TYPE, input_params=_dint_params(20), local_tags=_dint_locals(20)
    )
    _write(
        _def_only(definition, "AoiDescAllBase"),
        "aoistr_desc_all_l000",
        "AOI definition only: 20 DINT Input params AND 20 DINT LocalTags, no "
        "descriptions anywhere. The baseline aoistr_desc_all_l064 is differenced "
        "against -- without it that file's extra 20 LocalTags would be confounded "
        "with the description cost it exists to measure.",
    )

    definition, _ = aoi_xml(
        AOI_TYPE,
        input_params=_dint_params(20, description="D" * 64),
        local_tags=_dint_locals(20, description="D" * 64),
    )
    _write(
        _def_only(definition, "AoiDescAll"),
        "aoistr_desc_all_l064",
        "AOI definition only: 20 DINT Input params AND 20 DINT LocalTags, all 40 "
        "carrying a 64-character description. Paired with aoistr_desc_l064 (params "
        "described, locals absent) it says whether a LocalTag description costs the "
        "same as a Parameter description.",
    )

    definition, _ = aoi_xml(AOI_TYPE, input_params=_dint_params(20), description="D" * 256)
    _write(
        _def_only(definition, "AoiDescSelf"),
        "aoistr_aoidesc_l256",
        "AOI definition only: 20 plain DINT Input params, but the AOI DEFINITION "
        "itself carries a 256-character <Description>. Real AOIs almost all have "
        "one (PTimer 'Position Based Timer', fbInput 'Force IO + Debounce'); the "
        "model prices it at 0.",
    )

    definition, _ = aoi_xml(AOI_TYPE, input_params=_dint_params(20), revision_note="R" * 256)
    _write(
        _def_only(definition, "AoiRevNote"),
        "aoistr_aoirevnote_l256",
        "AOI definition only: same 20 plain DINT Input params, but with a "
        "256-character <RevisionNote> instead. Real revision notes are long "
        "(HomeToTorque's runs to several sentences of change history) and, like "
        "the description, are priced at 0.",
    )


def _group_inout() -> None:
    """InOut params are skipped outright by compute_aoi_definition_cost, so
    all four of these files are predicted IDENTICAL. Any spread is a
    straight measurement of an unpriced item."""
    for n in (0, 4, 16, 48):
        definition, _ = aoi_xml(
            AOI_TYPE,
            input_params=_dint_params(8),
            inout_params=[MemberSpec(_member_name("IoRef", i, 12), "DINT") for i in range(n)],
        )
        _write(
            _def_only(definition, f"AoiInOut{n:02d}"),
            f"aoistr_inout_n{n:02d}",
            f"AOI definition only: fixed 8 DINT Input params plus {n} DINT InOut "
            f"params. compute_aoi_definition_cost skips InOut entirely, so all four "
            f"files in this sweep are predicted to the same byte -- any spread in "
            f"the captured numbers is an unpriced declaration cost. InOut is the "
            f"only legal way to pass an array/STRING/MESSAGE/UDT into an AOI, so a "
            f"third-party AOI library will be full of them.",
        )


def _group_predefined() -> None:
    """Predefined-structure members: never generated before today."""
    definition, _ = aoi_xml(AOI_TYPE, local_tags=_dint_locals(8))
    _write(
        _def_only(definition, "AoiPredefBase"),
        "aoistr_predef_base_n00",
        "AOI definition only: 8 plain DINT LocalTags. The shared baseline every "
        "aoistr_predef_* file below is differenced against -- each of those swaps "
        "DINT for a predefined structure type at the same member count.",
    )

    for type_name, why in (
        ("TIMER", "557 real AOI member uses, the single most common non-atomic AOI member type"),
        ("COUNTER", "66 real AOI member uses"),
        ("MOTION_INSTRUCTION", "36 real AOI member uses, and motion-heavy files are where this project's residual is worst"),
        ("STRING", "58 real AOI member uses; STRING is 88 bytes of storage against DINT's 4, so if declaration cost tracks storage at all this is where it shows"),
    ):
        for n in (1, 8):
            locals_ = [
                predef_member(_member_name("PdfMbr", i, 12), type_name) for i in range(n)
            ] + _dint_locals(8 - min(n, 8))
            definition, _ = aoi_xml(AOI_TYPE, local_tags=locals_)
            _write(
                _def_only(definition, f"AoiPdf{type_name[:6].title()}{n:02d}"),
                f"aoistr_predef_{type_name.split('_')[0].lower()}_n{n:02d}",
                f"AOI definition only: {n} {type_name} LocalTag(s) substituted for "
                f"{n} of the 8 DINT LocalTags in aoistr_predef_base_n00, total member "
                f"count held at 8. {type_name} has no entry in the per-type rate "
                f"table, so it is charged the flat atomic rate today ({why}).",
            )

    for n in (1, 8):
        definition, _ = aoi_xml(
            AOI_TYPE,
            local_tags=_dint_locals(8),
            inout_params=[MemberSpec(_member_name("MsgRef", i, 12), "MESSAGE") for i in range(n)],
        )
        _write(
            _def_only(definition, f"AoiPdfMsg{n:02d}"),
            f"aoistr_predef_msg_inout_n{n:02d}",
            f"AOI definition only: the 8-DINT-LocalTag baseline plus {n} MESSAGE "
            f"InOut Parameter(s). MESSAGE can only ever be an InOut param (real: "
            f"MsgModuleReset, MESSAGE_Fault, MESSAGE_Alarm), so this file is charged "
            f"identically to the baseline today -- it is both the MESSAGE test and a "
            f"second, independent read on the InOut sweep above.",
        )


def _group_dimensions() -> None:
    definition, _ = aoi_xml(AOI_TYPE, local_tags=_dint_locals(4))
    _write(
        _def_only(definition, "AoiDimBase"),
        "aoistr_dim_base",
        "AOI definition only: 4 scalar DINT LocalTags. Baseline for the "
        "aoistr_dim_* sweeps -- an AOI member counts as one declared item today "
        "whether it is scalar or Dimensions=\"1024\".",
    )

    for d in (8, 64, 512):
        locals_ = [MemberSpec(_member_name("ArrLocal", 0, 12), "DINT", dimension=d)] + _dint_locals(3)
        definition, _ = aoi_xml(AOI_TYPE, local_tags=locals_)
        _write(
            _def_only(definition, f"AoiDimLocal{d:03d}"),
            f"aoistr_dim_local_atomic_d{d:03d}",
            f"AOI definition only: one DINT LocalTag dimensioned to {d} elements "
            f"plus 3 scalar DINT LocalTags (4 declared items, same as "
            f"aoistr_dim_base). The model charges the array member exactly what it "
            f"charges a scalar; {d} DINTs is {d * 4} bytes of real storage.",
        )

    for d in (8, 64):
        locals_ = [predef_array_member(_member_name("ArrTmr", 0, 12), "TIMER", d)] + _dint_locals(3)
        definition, _ = aoi_xml(AOI_TYPE, local_tags=locals_)
        _write(
            _def_only(definition, f"AoiDimTimer{d:03d}"),
            f"aoistr_dim_local_timer_d{d:03d}",
            f"AOI definition only: one TIMER LocalTag dimensioned to {d} elements "
            f"plus 3 scalar DINT LocalTags. Crosses the two unpriced properties "
            f"(predefined structure AND dimension) to check they compose rather "
            f"than interact -- the real `Motion` MOTION_INSTRUCTION[7] LocalTag in "
            f"SJ_Gormley is exactly this shape.",
        )

    for d in (8, 64, 512):
        definition, _ = aoi_xml(
            AOI_TYPE,
            local_tags=_dint_locals(4),
            inout_params=[MemberSpec(_member_name("ArrRef", 0, 12), "DINT", dimension=d)],
        )
        _write(
            _def_only(definition, f"AoiDimInOut{d:03d}"),
            f"aoistr_dim_inout_d{d:03d}",
            f"AOI definition only: the 4-scalar-DINT-LocalTag baseline plus one "
            f"DINT InOut Parameter dimensioned to {d}. Array InOut params are the "
            f"real corpus shape (LOG_HMIDisplay Dimensions=\"25\", BitArray "
            f"Dimensions=\"1024\") and are doubly invisible to the model: InOut is "
            f"skipped, and dimension is ignored.",
        )


def _group_scale() -> None:
    """Extend each axis from the real MEDIAN to the real p90 and past it.
    The model predicts a dead-straight line in all three sweeps, so any
    curvature is unambiguous -- the same construction that caught
    OQ-SHELLSCALE's 8-bytes-per-unit slope error."""
    for n in (12, 24, 48, 102):
        definition, _ = aoi_xml(AOI_TYPE, input_params=_dint_params(n))
        _write(
            _def_only(definition, f"AoiScaleParam{n:03d}"),
            f"aoistr_scale_param_n{n:03d}",
            f"AOI definition only: {n} DINT Input params (real corpus: median 12, "
            f"p90 45, max 102). per_declared_item was fitted at 2-8 params and is "
            f"applied to real AOIs an order of magnitude larger; this sweep spans "
            f"the real range so a real file interpolates instead of extrapolating.",
        )

    for n in (11, 32, 64, 128):
        definition, _ = aoi_xml(AOI_TYPE, local_tags=_dint_locals(n))
        _write(
            _def_only(definition, f"AoiScaleLocal{n:03d}"),
            f"aoistr_scale_local_n{n:03d}",
            f"AOI definition only: {n} DINT LocalTags (real corpus: median 11, p90 "
            f"30, max 128). Same construction as the param sweep on the other "
            f"declaration axis -- the model charges a LocalTag and a Parameter the "
            f"identical per_declared_item rate, which this pair also tests.",
        )

    for n in (11, 24, 48, 85):
        definition, _ = aoi_xml(
            AOI_TYPE,
            input_params=_dint_params(4),
            logic_rungs_xml=rungs_xml(n, lambda i: "XIC(EnableIn)MOV(InParam00xxx,InParam01xxx);"),
        )
        _write(
            _def_only(definition, f"AoiScaleRung{n:03d}"),
            f"aoistr_scale_rung_n{n:03d}",
            f"AOI definition only: fixed 4 DINT Input params, {n} identical internal "
            f"Logic rungs (real corpus: median 11 internal rungs, p90 36, max 85). "
            f"AOI-internal logic is priced through the same per-instruction weights "
            f"as program logic plus the aoi_logic_composite_surcharge; that surcharge "
            f"was fitted on files carrying 21-216 combined AOI+JSR instructions and "
            f"real AOI-dense files carry far more.",
        )


def _group_routines() -> None:
    """Internal routine COUNT at constant total rung count. 24 rungs split
    1/2/3 ways, so anything that moves is per-routine, not per-rung."""
    body = "XIC(EnableIn)MOV(InParam00xxx,InParam01xxx);"
    for n in (1, 2, 3):
        per = 24 // n
        kwargs = {"logic_rungs_xml": rungs_xml(per, lambda i: body)}
        if n >= 2:
            kwargs["enable_in_false_rungs_xml"] = rungs_xml(per, lambda i: body)
        if n >= 3:
            kwargs["prescan_rungs_xml"] = rungs_xml(per, lambda i: body)
        definition, _ = aoi_xml(AOI_TYPE, input_params=_dint_params(4), **kwargs)
        _write(
            _def_only(definition, f"AoiRoutines{n}"),
            f"aoistr_routines_n{n}",
            f"AOI definition only: 24 internal rungs split across {n} internal "
            f"routine(s) (Logic{'/EnableInFalse' if n >= 2 else ''}"
            f"{'/Prescan' if n >= 3 else ''}), total rung and instruction count "
            f"held constant. 7 of 81 real AOI definitions have more than one "
            f"internal routine; no generated file ever had. A program Routine "
            f"costs a measured 264 bytes of shell -- this asks whether an AOI's "
            f"internal routine costs the same, something else, or nothing.",
        )


def _group_composite() -> None:
    """The check that the isolated parts add up. Both files use REAL-shaped
    naming and commenting rather than the sterile fixed-width names above,
    because that is what a stranger's file will look like."""
    shapes = (
        ("median", 12, 11, 11, 2, 1),
        ("p90", 45, 30, 36, 6, 3),
    )
    for label, n_param, n_local, n_rung, n_timer, n_inout in shapes:
        params = [
            MemberSpec(f"Cmd{i:02d}_Setpoint"[:32], "DINT", required=True,
                       description=f"Setpoint {i} for the controlled element")
            for i in range(n_param)
        ]
        locals_ = [
            predef_member(f"DwellTmr{i:02d}", "TIMER", description=f"Dwell timer {i}")
            for i in range(n_timer)
        ] + [
            MemberSpec(f"WorkAccumulator{i:02d}"[:32], "REAL",
                       description=f"Working accumulator {i}")
            for i in range(n_local - n_timer)
        ]
        inouts = [MemberSpec(f"SharedBuffer{i:02d}", "DINT", dimension=32) for i in range(n_inout)]
        definition, storage = aoi_xml(
            AOI_TYPE,
            input_params=params,
            local_tags=locals_,
            inout_params=inouts,
            description="Composite AOI at the real corpus " + label + " structural size",
            revision_note="Generated composite -- see gen_aoi_structure.py",
            logic_rungs_xml=rungs_xml(n_rung, lambda i: "XIC(EnableIn)MOV(Cmd00_Setpoint,Cmd01_Setpoint);"),
        )
        # Every Required Input param has to be wired at the call site, and
        # each dimensioned InOut takes a whole array tag bare (real corpus
        # shape -- see the AOI-call exemption in lint.py).
        arg_names = [f"Arg{i:02d}" for i in range(n_param)]
        buf_names = [f"SharedBuf{i:02d}" for i in range(n_inout)]
        call_args = ",".join(arg_names + buf_names)
        instance_tags = "\n".join(
            [tag_xml("AoiInst", AOI_TYPE, udt_members=storage)]
            + [tag_xml(a, "DINT") for a in arg_names]
            + [tag_xml(b, "DINT", dimensions=(32,)) for b in buf_names]
        )
        l5x = build_l5x(
            target_name=f"AoiReal{label.title()}",
            tags_xml=instance_tags,
            extra_aoi_xml=definition,
            extra_rungs_xml=rung_xml(0, f"{AOI_TYPE}(AoiInst,{call_args});"),
        )
        _write(
            l5x,
            f"aoistr_real_{label}",
            f"Composite, INSTANTIATED (the only two files in this batch that are "
            f"not definition-only): one AOI at the real corpus {label} structural "
            f"size -- {n_param} described Input params, {n_local} locals of which "
            f"{n_timer} are TIMERs, {n_inout} dimensioned InOut params, {n_rung} "
            f"internal rungs, real-shaped variable-length member names, an AOI "
            f"description and a revision note. Every property the isolation groups "
            f"measure separately appears here at once, so it is the check that the "
            f"parts add rather than interact.",
        )


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    _group_namelen()
    _group_description()
    _group_inout()
    _group_predefined()
    _group_dimensions()
    _group_scale()
    _group_routines()
    _group_composite()


if __name__ == "__main__":
    main()
