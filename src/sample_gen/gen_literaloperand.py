"""Price an IMMEDIATE NUMERIC LITERAL in an instruction operand -- OQ-LITERALOPERAND.

THE MEASUREMENT THAT OPENED THIS. One rung, one project, edited in Logix
Designer and compiled by Studio, Capacity read twice:

    74,224  MAM(axVirtual,MAM,1,Position,Speed,% of Maximum,AccelDecel,
                % of Maximum,AccelDecel,% of Maximum,Trapezoidal,Jerk,
                Jerk,% of Maximum,Disabled,Current,0,None,0,0)
    74,248  MAM(axVirtual,MAM,1,99.99,99.99,% of Maximum,99.99,
                % of Maximum,99.99,% of Maximum,Trapezoidal,99.99,
                99.99,% of Maximum,Disabled,Current,0,None,0,0)

Six operand slots moved from a tag reference to the immediate `99.99`.
+24 bytes over 6 slots = +4.000 per slot, six for six. The engine charges
ZERO for this: run on both rung texts it returns 320 bytes either way.

It is not a new constant. `memory_model.yaml`
`cpt_expression.real_dest.per_float_literal` is already 4, fitted across 12
files. The same 4 now appears in MAM, an unrelated instruction priced by an
unrelated code path, which is what a general law looks like rather than a
per-instruction quirk. Literals are priced ONLY inside CPT expressions,
CMP operands and ST statements.

WHY THE BENCH NUMBER DOES NOT SETTLE IT. Across the seventeen real programs
there are 52,195 unpriced literal operand slots -- 12.1% of all 432,850
operand slots, 208,780 bytes at 4 each, 25.4% of the +822,938 residual. But
51,265 of those are INTEGER literals and only 930 are float, so the measured
case covers 1.8% of the mass. Fitting the integer rate against the real set
gives mean-optimal 2 and max-optimal 6.5; that disagreement is itself evidence
that a single flat rate is the wrong shape and the cost is type-dependent.
Charging 51,265 slots at a rate extrapolated 55x beyond its evidence is the
move that produced every bad constant in this project.

THE HYPOTHESIS. An immediate costs the width of its type, stored inline --
REAL 4 (measured), DINT 4, INT 2, SINT 1, LINT 8, matching the atomic-type
table in docs/MEMORY_MODEL.md. The competing hypothesis is that the cost
follows the SLOT's declared width rather than the literal's written form.
Arms A and B separate those.

EVERY FILE HOLDS THE SOURCE TAG DECLARED *AND* REFERENCED. That is the
property that made the bench measurement clean: `Position`, `Speed`,
`AccelDecel` and `Jerk` are still declared and still referenced by the four
EQU instructions in BOTH versions, so nothing measured here is a tag being
deleted. Every pair below carries the same held-fixed EQU referencing its
source tag, in both members. Drop that and the literal term is confounded with
tag-declaration cost, which is 84+ bytes per tag and would swamp a 4-byte
effect.

ARM A -- `litop_type_{sint,int,dint,lint,real}_{tag,lit}_n01000`, 10 files.
    1,000 MOV rungs, one pair per destination type. The tag member moves a
    source tag of that type; the literal member moves a type-natural literal
    into the same destination. (literal member - tag member) / 1000 IS the
    per-type rate, directly, with no fitting. This is the arm the whole
    question turns on: it is the only one that can produce the rate table for
    the 51,265 integer slots.

ARM B -- `litop_form_{small,intrange,dintrange,floatform}_n01000`, 4 files.
    1,000 MOV rungs into the SAME DINT destination, varying only the literal:
    `5` (fits SINT), `300` (needs INT), `70000` (needs DINT), `5.0` (float
    written form, same value as the first). Discriminates three hypotheses at
    once -- if all four are equal the cost follows the destination's declared
    width and arm A's table is indexed by slot type; if they scale with
    magnitude it follows the value; if only `5.0` differs it follows the
    written form.

ARM C -- `litop_pool_{same,tworep,alldistinct}_n01000`, 3 files. 1,000 ADD
    rungs, two literal operands each, same destination tag throughout: both
    literals one value in every rung (2,000 slots, 1 distinct); two values
    repeated across rungs (2,000 slots, 2 distinct); every literal distinct
    (2,000 slots, 2,000 distinct). Separates a per-SLOT cost from a
    constant-POOL cost. Not optional: `OQ-SERIESOUTPUT`'s candidate B died
    exactly this way, by assuming per-occurrence when the real law was
    per-distinct. It matters more here than anywhere -- real ladder reuses `0`
    and `1` massively, so if there is a pool the 205,060-byte integer exposure
    is a small fraction of that.

ARM D -- `litop_fold_{zero,one,two}_n01000`, 3 files. 1,000 MOV rungs into a
    DINT with literal `0`, `1`, `2`. Tests whether Studio special-cases 0 and
    1, which is a plausible compiler optimisation and would matter out of all
    proportion to the arm's size: `0` and `1` are the most common literals in
    real ladder, so if they are free the real exposure collapses. `2` is the
    control -- the smallest value that cannot be a folded special case.

ARM E -- `litop_family_{mov,equ,jsr}_n01000`, 3 files. The same DINT literal
    12345 in a MOV source operand, an EQU comparison operand and a JSR
    parameter, 1,000 each. The bench measurement is MAM only; MOV and EQU
    carry 18,924 of the real literal slots between them and JSR 2,631, so this
    arm decides whether the law generalises to where the mass actually is.

ARM F -- `litop_bool_{alltag,zero,one,dint}_n01000`, 4 files. The BOOL
    question: does a boolean input slot treat 0/1 differently? Probed through
    an AOI shaped on the real `DigitalSensor` (BOOL inputs plus DINT inputs,
    878 call sites across the real set), because an AOI Input parameter is the
    operand slot where a literal can legally reach a BOOL. All four files hold
    1,000 call sites of the same AOI and move only what is passed to one
    parameter: all tags, then literal `0`, then literal `1`, then a literal
    into the DINT parameter instead as the same-file control.

    HONEST SCOPE. Real `DigitalSensor` call sites pass exactly two arguments,
    both tags -- instance plus the one Required input -- in all 886 of them;
    the optional inputs are set on the instance tag, never at the call site.
    So a literal into a BOOL parameter is NOT an attested real shape. This arm
    is a MECHANISM probe, kept because BOOL is the one atomic width the
    hypothesis says should behave differently (1 bit, not 1 byte) and because
    0/1 folding is the highest-leverage unknown in arm D. It must not be cited
    as real-shape evidence.

    The parameters are Required="false" Visible="true", which is the flag
    combination that permits a literal OR a tag at the call site. Required=
    "true" demands a wired tag and would reject the literal outright.

ARM G -- `litop_mam_{tag,lit}_n01000`, 2 files. The bench measurement itself,
    reproduced inside the generated pipeline at 1,000 rungs instead of 1. The
    operand list is TRANSPLANTED verbatim from the rung Studio compiled --
    "transplant, never compose", the rule that exists because bare composed
    MAM/MAJ/MAS/MRP rungs failed every rung once already. Only the tag NAMES
    are substituted, for verified_tags.py equivalents of the same types
    (`Axis1` AXIS_VIRTUAL for `axVirtual`, `MCD` MOTION_INSTRUCTION for the
    `MAM` tag), because those XML blocks are themselves verbatim real and
    renaming them would break that guarantee. This pair should return +4,000
    bytes; if it does not, the generated pipeline does not reproduce the bench
    and nothing else in this batch can be trusted either. It is deliberately
    last and deliberately isolated so a MAM import failure cannot take the
    other 27 files with it.

29 files. Every one 1756-L81E at v35 -- comparability against the ~2,500
existing captures, enforced by lint's non_standard_processor /
non_standard_firmware rules.

Verify with `python scripts/confound_check.py --family '^litop_'` -- every
consecutive pair within an arm must move exactly one dimension.

Run: python -m sample_gen.gen_literaloperand
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import (
    MemberSpec, aoi_xml, rung_xml, tag_xml, tags_xml,
)
from sample_gen.manifest import append_manifest_row, write_sample, write_sample_unmodeled
from sample_gen.verified_tags import tags as verified_tags
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
CATEGORY = "literal_operand"

N = 1000

# One literal per destination type, each the natural written form for that
# type and in range for it. SINT is -128..127, INT -32768..32767.
ARM_A_TYPES = (
    ("sint", "SINT", "5"),
    ("int", "INT", "5"),
    ("dint", "DINT", "5"),
    ("lint", "LINT", "5"),
    ("real", "REAL", "5.0"),
)

# Fixed DINT destination; only the literal moves. Ordered narrow -> wide so a
# magnitude-driven cost shows up as a monotone staircase.
ARM_B_LITERALS = (
    ("small", "5", "fits in a SINT"),
    ("intrange", "300", "needs an INT, will not fit a SINT"),
    ("dintrange", "70000", "needs a DINT, will not fit an INT"),
    ("floatform", "5.0", "the float written form of arm B's first value"),
)

ARM_D_LITERALS = (
    ("zero", "0", "the most common literal in real ladder"),
    ("one", "1", "the second most common"),
    ("two", "2", "the control -- smallest value that cannot be a folded special case"),
)

FAMILY_LITERAL = "12345"


def _write(name: str, l5x: str, description: str) -> None:
    out = OUT / f"{name}.L5X"
    append_manifest_row(name, description, CATEGORY, out, write_sample(l5x, out))


def _write_unmodeled(name: str, l5x: str, description: str) -> None:
    """An AXIS_* tag makes predicted_bytes uncomputable (OQ-AXISSTRUCT), so
    arm G logs predicted 0 and is differenced pair-against-pair instead."""
    out = OUT / f"{name}.L5X"
    write_sample_unmodeled(l5x, out)
    append_manifest_row(name, description, CATEGORY, out, 0)


def _build(tags: str, rungs: list[str], **kw) -> str:
    return build_l5x(
        target_name="LitOperandProbe",
        tags_xml=tags,
        extra_rungs_xml="\n".join(rung_xml(i, t) for i, t in enumerate(rungs)),
        **kw,
    )


def _arm_a() -> int:
    """Per-destination-type rate. The arm the question turns on."""
    for slug, dtype, literal in ARM_A_TYPES:
        tags = tags_xml([("LitSrc", dtype), ("LitDst", dtype)])
        # The EQU is byte-identical in both members and keeps LitSrc both
        # DECLARED and REFERENCED in the literal file too -- the property that
        # made the bench measurement clean.
        guard = "EQU(LitSrc,LitSrc)"
        for kind, operand in (("tag", "LitSrc"), ("lit", literal)):
            _write(
                f"litop_type_{slug}_{kind}_n{N:05d}",
                _build(tags, [f"{guard}MOV({operand},LitDst);"] * N),
                f"{N} MOV rungs into a {dtype} destination, source operand = "
                f"{'the ' + dtype + ' tag LitSrc' if kind == 'tag' else 'the immediate literal ' + literal}. "
                f"Arm A of the literal-operand sweep, pair {slug}, and the measurement "
                f"OQ-LITERALOPERAND turns on: (literal file - tag file) / {N} is the "
                f"per-slot cost of an immediate {dtype} literal, directly, with nothing "
                f"fitted. The bench measured +4.000 for a REAL literal in a REAL-typed "
                f"motion parameter; that case is 930 of the 52,195 unpriced literal slots "
                f"in the seventeen real programs and the other 51,265 are integers at an "
                f"unmeasured rate, which is why this arm exists. Hypothesis: an immediate "
                f"costs the width of its type inline -- SINT 1, INT 2, DINT 4, LINT 8, "
                f"REAL 4. LitSrc is DECLARED AND REFERENCED in BOTH files, by a "
                f"byte-identical EQU, so this measures the operand and not a deleted tag. "
                f"OQ-LITERALOPERAND.",
            )
    return len(ARM_A_TYPES) * 2


def _arm_b() -> int:
    """Literal form and magnitude against a FIXED destination width."""
    tags = tags_xml([("LitSrc", "DINT"), ("LitDst", "DINT")])
    for slug, literal, note in ARM_B_LITERALS:
        _write(
            f"litop_form_{slug}_n{N:05d}",
            _build(tags, [f"EQU(LitSrc,LitSrc)MOV({literal},LitDst);"] * N),
            f"{N} MOV rungs into the SAME DINT destination with the immediate literal "
            f"{literal} -- {note}. Arm B of the literal-operand sweep. The destination "
            f"type, the instruction, the rung count and the tag population are identical "
            f"across all four files; the only thing that moves is the literal itself. "
            f"Discriminates three hypotheses at once. All four equal => the cost follows "
            f"the DESTINATION's declared width, and arm A's table is indexed by slot type. "
            f"A staircase 5 < 300 < 70000 => it follows the VALUE's required width. Only "
            f"5.0 differing => it follows the WRITTEN FORM. Arm A alone cannot separate "
            f"these because it moves slot type and literal form together. "
            f"OQ-LITERALOPERAND.",
        )
    return len(ARM_B_LITERALS)


def _arm_c() -> int:
    """Per-slot or per-distinct-value. The trap that killed OQ-SERIESOUTPUT's
    candidate B, and the one that decides whether the real exposure is
    205,060 bytes or a small fraction of it."""
    tags = tags_xml([("LitSrc", "DINT"), ("LitDst", "DINT")])
    shapes = (
        ("same", lambda r: ("7", "7"), "one distinct value over all 2,000 slots"),
        ("tworep", lambda r: ("7", "9"), "two distinct values, repeated in every rung"),
        ("alldistinct", lambda r: (str(2 * r + 1), str(2 * r + 2)),
         "2,000 distinct values, one per slot"),
    )
    for slug, fn, note in shapes:
        rungs = []
        for r in range(N):
            a, b = fn(r)
            rungs.append(f"EQU(LitSrc,LitSrc)ADD({a},{b},LitDst);")
        _write(
            f"litop_pool_{slug}_n{N:05d}",
            _build(tags, rungs),
            f"{N} ADD rungs with two immediate literal operands each -- 2,000 literal "
            f"slots -- carrying {note}. Same destination tag, same instruction, same rung "
            f"count, same slot count in all three files; only the NUMBER OF DISTINCT "
            f"VALUES moves. Arm C of the literal-operand sweep, and it separates a "
            f"per-SLOT cost from a constant-POOL cost. If alldistinct > same there is a "
            f"pool and the term is per-distinct-value. This is not optional: "
            f"OQ-SERIESOUTPUT's candidate B died by assuming per-occurrence when the real "
            f"law was per-distinct, and it matters more here than anywhere because real "
            f"ladder reuses 0 and 1 massively -- a pool would mean the 205,060-byte "
            f"integer exposure across the seventeen is a small fraction of that. "
            f"OQ-LITERALOPERAND.",
        )
    return len(shapes)


def _arm_d() -> int:
    """Does Studio fold 0 and 1?"""
    tags = tags_xml([("LitSrc", "DINT"), ("LitDst", "DINT")])
    for slug, literal, note in ARM_D_LITERALS:
        _write(
            f"litop_fold_{slug}_n{N:05d}",
            _build(tags, [f"EQU(LitSrc,LitSrc)MOV({literal},LitDst);"] * N),
            f"{N} MOV rungs into a DINT with the immediate literal {literal} -- {note}. "
            f"Arm D of the literal-operand sweep: does Studio special-case 0 and 1? A "
            f"plausible compiler optimisation, and it matters out of all proportion to "
            f"three files, because 0 and 1 are the most common literals in real ladder -- "
            f"if they are free, the real integer exposure collapses from 205,060 bytes to "
            f"a fraction of it and this whole question drops down the queue. 2 is the "
            f"control: the smallest value that cannot plausibly be a folded special case. "
            f"Cross-checks against arm B's `small` file, which is the same shape at 5. "
            f"OQ-LITERALOPERAND.",
        )
    return len(ARM_D_LITERALS)


def _arm_e() -> int:
    """Does the law reach past motion parameters to where the mass is?"""
    mov_tags = tags_xml([("LitSrc", "DINT"), ("LitDst", "DINT")])
    equ_tags = tags_xml([("LitSrc", "DINT"), ("LitDst", "BOOL")])
    # The callee's receiver is its own tag, and the SBR rung terminates in
    # NOP() -- the house pattern (gen_jsr_decompose et al). A bare
    # SBR(x); is condition-only and lint rejects it, correctly.
    jsr_tags = tags_xml([("LitSrc", "DINT"), ("LitDst", "DINT"), ("LitRecv", "DINT")])
    sub_routine = (
        '<Routine Name="LitTarget" Type="RLL"><RLLContent>'
        + rung_xml(0, "SBR(LitRecv)NOP();") + "\n"
        + rung_xml(1, "RET();")
        + '</RLLContent></Routine>'
    )
    cases = (
        ("mov", mov_tags, f"EQU(LitSrc,LitSrc)MOV({FAMILY_LITERAL},LitDst);", {},
         "a MOV source operand", "9,835 real literal slots"),
        ("equ", equ_tags, f"EQU(LitSrc,{FAMILY_LITERAL})OTE(LitDst);", {},
         "an EQU comparison operand", "9,089 real literal slots"),
        ("jsr", jsr_tags, f"EQU(LitSrc,LitSrc)JSR(LitTarget,1,{FAMILY_LITERAL});",
         {"extra_routines_xml": sub_routine},
         "a JSR input parameter", "2,631 real literal slots"),
    )
    for slug, tags, rung, kw, where, mass in cases:
        _write(
            f"litop_family_{slug}_n{N:05d}",
            _build(tags, [rung] * N, **kw),
            f"{N} rungs putting the immediate DINT literal {FAMILY_LITERAL} in {where} "
            f"-- {mass} across the seventeen real programs. Arm E of the literal-operand "
            f"sweep: does the law generalise past the motion parameter block the bench "
            f"measured, to the instructions that actually carry the mass? MOV and EQU "
            f"hold 18,924 of the 52,195 unpriced real literal slots between them and JSR "
            f"2,631, against MAM's 1,088. Each file differences against its own "
            f"all-tag control in arm A (`litop_type_dint_tag_n{N:05d}`, the identical "
            f"MOV shape) and against the other two files here. If the three rates differ, "
            f"the cost is per-instruction-family and a single global literal term is the "
            f"wrong model. OQ-LITERALOPERAND.",
        )
    return len(cases)


def _arm_f() -> int:
    """The BOOL question: does a boolean input slot treat 0/1 differently?

    Probed through an AOI because an AOI Input parameter is the only operand
    slot where a literal can legally reach a BOOL.

    THE FLAGS ARE Required="true", AND THE FIRST CUT OF THIS HAD THEM BACKWARDS.
    It used Required="false" Visible="true" on the documented belief that this
    was the pair permitting a literal. Studio rejected every rung of all four
    files -- including the all-tag control, so it was never about literals --
    with "Invalid number of arguments for instruction".

    The rule, read off 917 real AOI call sites in a real export rather than
    inferred: a call site passes EXACTLY the Required parameters, unanimously,
    and a Visible-but-optional parameter is set on the instance tag instead of
    at the call. 375 of those 917 carry an immediate literal, and 128 of them
    put a literal 0 or 1 in a Required BOOL parameter -- which is this arm's
    question, occurring 128 times in one real program. A Required parameter
    does not demand a wired tag.
    """
    params = [
        MemberSpec("RawInput", "BOOL", required=True, visible=True),
        MemberSpec("NormallyOpen", "BOOL", required=True, visible=True),
        MemberSpec("DbTimeHigh", "DINT", required=True, visible=True),
    ]
    aoi, storage = aoi_xml(
        "LitSensor",
        input_params=params,
        output_params=[MemberSpec("Sts", "BOOL")],
        logic_rungs_xml=(
            '<Rung Number="0" Type="N">'
            '<Text><![CDATA[XIC(RawInput)OTE(Sts);]]></Text></Rung>'
        ),
        description=(
            "Shaped on the real DigitalSensor AOI -- BOOL inputs plus DINT "
            "inputs -- to give an immediate literal a legal path into a BOOL "
            "operand slot."
        ),
    )
    # One instance tag plus the three source tags, identical in all four files.
    inst = tag_xml("Sensor", "LitSensor", udt_members=storage)
    src = tags_xml([("RawIn", "BOOL"), ("NormOpen", "BOOL"), ("TimeHigh", "DINT")])
    tags = inst + "\n" + src
    # The moving parameter is the SECOND one (NormallyOpen, a BOOL) except in
    # the `dint` control, where the third (DbTimeHigh) moves instead. Exactly
    # one call-site argument differs between any file and `alltag`.
    cases = (
        ("alltag", "RawIn,NormOpen,TimeHigh", "every parameter wired to a tag"),
        ("zero", "RawIn,0,TimeHigh", "the BOOL parameter NormallyOpen given the literal 0"),
        ("one", "RawIn,1,TimeHigh", "the BOOL parameter NormallyOpen given the literal 1"),
        ("dint", "RawIn,NormOpen,12345",
         "the DINT parameter DbTimeHigh given the literal 12345, as the same-file control"),
    )
    for slug, args, note in cases:
        _write(
            f"litop_bool_{slug}_n{N:05d}",
            _build(tags, [f"LitSensor(Sensor,{args});"] * N, extra_aoi_xml=aoi),
            f"{N} call sites of one AOI with {note}. Arm F of the literal-operand sweep, "
            f"and the BOOL question: does a boolean input slot price 0 and 1 differently "
            f"from a wider type? BOOL is the one atomic width where the "
            f"cost-is-the-type's-width hypothesis predicts something different -- a bit, "
            f"not a byte -- and 0/1 folding is the highest-leverage unknown in arm D. The "
            f"AOI definition, the instance tag, the three source tags and the rung count "
            f"are identical across all four files; exactly ONE call-site argument moves. "
            f"The parameters are Required=false Visible=true, the flag pair that permits "
            f"a literal or a tag at the call site -- Required=true demands a wired tag and "
            f"would reject the literal. HONEST SCOPE: all 886 real DigitalSensor call "
            f"sites pass exactly two TAG arguments and set the optional inputs on the "
            f"instance tag, so a literal into a BOOL parameter is NOT an attested real "
            f"shape. This is a mechanism probe and must not be cited as real-shape "
            f"evidence. OQ-LITERALOPERAND.",
        )
    return len(cases)


def _arm_g() -> int:
    """The bench measurement, reproduced in the generated pipeline at n=1000.

    The operand list is TRANSPLANTED verbatim from the rung Studio compiled.
    Only tag names are substituted, for verified_tags.py blocks of the same
    types, because those blocks are themselves verbatim real and renaming
    them would break that guarantee.
    """
    tags = (verified_tags("Axis1", "MCD") + "\n"
            + tags_xml([("Position", "REAL"), ("Speed", "REAL"),
                        ("AccelDecel", "REAL"), ("Jerk", "REAL")]))
    guard = ("EQU(Position,Position)EQU(Speed,Speed)"
             "EQU(AccelDecel,AccelDecel)EQU(Jerk,Jerk)")

    def mam(pos: str, spd: str, acc: str, jrk: str) -> str:
        return (f"MAM(Axis1,MCD,1,{pos},{spd},% of Maximum,{acc},% of Maximum,"
                f"{acc},% of Maximum,Trapezoidal,{jrk},{jrk},% of Maximum,"
                f"Disabled,Current,0,None,0,0)")

    cases = (
        ("tag", mam("Position", "Speed", "AccelDecel", "Jerk"),
         "the four REAL tags, exactly as the bench control"),
        ("lit", mam("99.99", "99.99", "99.99", "99.99"),
         "the immediate 99.99 in all six slots, exactly as the bench variant"),
    )
    for slug, body, note in cases:
        _write_unmodeled(
            f"litop_mam_{slug}_n{N:05d}",
            _build(tags, [f"{guard}{body}NOP();"] * N),
            f"{N} rungs of the bench-measured MAM shape with {note}. Arm G of the "
            f"literal-operand sweep: the measurement that opened OQ-LITERALOPERAND, "
            f"reproduced inside the generated pipeline at {N} rungs instead of one. The "
            f"bench read 74,224 against 74,248 on a single rung -- +24 over six operand "
            f"slots, +4.000 each -- so this pair should differ by {6 * 4 * N:,} bytes. If "
            f"it does not, the generated pipeline does not reproduce the bench and nothing "
            f"else in this batch can be trusted, which is why the pair is here at all. The "
            f"operand list is TRANSPLANTED verbatim from the rung Studio itself compiled "
            f"(transplant, never compose -- bare composed MAM/MAJ/MAS/MRP rungs failed "
            f"every rung once already); only the tag names are substituted, for "
            f"verified_tags.py blocks of the same types, Axis1 (AXIS_VIRTUAL) and MCD "
            f"(MOTION_INSTRUCTION), because those blocks are verbatim real and renaming "
            f"them would break that. predicted_bytes is 0 because an AXIS_* tag makes it "
            f"uncomputable (OQ-AXISSTRUCT) -- this pair is differenced against itself, not "
            f"against a prediction. OQ-LITERALOPERAND.",
        )
    return len(cases)


def main() -> None:
    n = 0
    for arm in (_arm_a, _arm_b, _arm_c, _arm_d, _arm_e, _arm_f, _arm_g):
        written = arm()
        print(f"  {arm.__name__:10s} {written:2d} files")
        n += written
    print(f"{n} files written to {OUT}")


if __name__ == "__main__":
    main()
