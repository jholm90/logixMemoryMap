"""Separates the three things the captured defscale sweeps confounded.

Written 2026-09-11 after reconciling the 30 `defscale_*` captures. All four
sweeps came back PERFECTLY linear with zero residual, which is the good news
and the problem at once:

    defscale_aoidefs_n*   over-prediction  = +3 x n     (exact, 7 points)
    defscale_aoiinst_n*   over-prediction  = -264 - 157 x n   (exact, 7 pts)
    defscale_udts_n*      over-prediction  = -16 x n    (exact, 8 points)
    defscale_udttag_n*    over-prediction  = -19 x n    (exact, 8 points)

Subtracting the paired sweeps: an AOI DEFINITION is over-charged by 3 bytes,
an instantiated AOI is UNDER-charged by 160 bytes per unit plus 264 once, a
UDT definition is UNDER-charged by 16, and a UDT that has a tag is
under-charged by a further 3.

Applying those four numbers to the sixteen real programs moves mean absolute
error from 2.17% to 1.63%, files within 1% from 4 to 6, and within 2% from 9
to 11 -- and it moves every file UP, which is the direction the real files
need and the opposite direction to the module over-charge in
OQ-MODULEMARGINAL.

WHY IT IS NOT WIRED. Every one of those four sweeps varies TWO things at
once, and on a real program the two readings differ by a quarter of a
megabyte.

  `defscale_aoiinst_n` holds n definitions, each with exactly ONE instance
  tag AND exactly ONE calling rung. So n = definitions = instance tags =
  calls, and "160 per instance tag", "160 per AOI call" and "160 extra for a
  definition that is instantiated at all" fit the seven points identically.

  `defscale_udttag_n` holds n UDTs with exactly ONE tag each, so "3 per UDT
  tag" and "3 extra for a UDT that has any tag" fit the eight points
  identically.

On the real programs those readings are nowhere near each other. AccuTally
carries 902 AOI instances across 39 definitions and 33,574 UDT tags across
174 UDT definitions:

    per instance / per tag   ->  160 x 902  + 3 x 33574  = +245,042
    per definition           ->  160 x  39  + 3 x   174  =   +6,762

That is a 238 KB difference on one file, 4% of it. The same ambiguity as
OQ-MODULEMARGINAL's per-catalog-vs-per-file question, in a different cost
category, and it has to be measured rather than assumed for the same reason:
the tidier reading has been wrong before.

Every definition here is built from gen_defscale's own `_aoi_members()` and
`_udt_members()`, so the definitions are byte-identical to the captured
sweep and these files difference straight against it.

GROUP A -- AOI: definition count, instance count and call count separated.
    `dscale2_aoi_d001_t*_call`     ONE definition, n instance tags, n calls.
                                   Definition count is pinned at 1, so any
                                   slope here is per-instance, not per-def.
    `dscale2_aoi_d001_t*_nocall`   ONE definition, n instance tags, ZERO
                                   calls. Against the _call files this
                                   separates the tag from the call.
    `dscale2_aoi_d001_t001_c*`     ONE definition, ONE instance tag, called
                                   from n rungs. The converse control: call
                                   count varies with instance count pinned.
    `dscale2_aoi_d*_t*_nocall`     n definitions, one instance tag each, no
                                   calls -- the captured aoiinst shape minus
                                   the calls, at the same counts.

GROUP B -- `dscale2_aoi_arr*`: ONE definition, ONE tag that is an ARRAY of n
    instances. If the cost is per instance it scales with n; if it is per
    tag it does not move at all. Real programs carry arrays of AOI
    instances, so this is not a corner case.

GROUP C -- UDT: definition count and tag count separated the same way.
    `dscale2_udt_u001_t*`   ONE UDT definition, n tags of it (to n=500,
                            since real files reach 33,574 UDT tags).
    `dscale2_udt_u005_t*`   5 UDTs, n tags each.
    `dscale2_udt_u025_t*`   25 UDTs, n tags each. The two grids test that
                            definition count and tag count are additive
                            rather than interacting.
    `dscale2_udt_arr*`      ONE UDT, ONE tag that is an array of n elements
                            -- per-element or per-tag, same question as
                            group B.

NOT COVERED, and reported rather than guessed: program-scoped structure
tags. A Program-scoped ATOMIC tag has a confirmed real shape
(`program_tag_xml`, dual L5K+Decorated), but nothing in the real corpus has
been read for a Program-scoped UDT or AOI-instance tag, and real programs
put most of their instances there. Building one from a guessed shape would
put an unverified XML shape inside the experiment meant to settle the
question. It needs a real export first.

Run: python -m sample_gen.gen_defscale2
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml, udt_xml
from sample_gen.gen_defscale import _aoi_members, _udt_members
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, predicted_bytes
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "defscale"

# Instance counts bracket the real files (26-902 instances) from both sides.
INST_COUNTS = [1, 2, 5, 10, 20, 40, 60, 100]
# The sparse control counts, where a second arm only needs to confirm or
# break a slope rather than trace it.
CONTROL_COUNTS = [1, 5, 20, 60]
# UDT tag counts run to 500: real files reach 33,574 UDT tags, so even 500
# is still extrapolation, but it is 2.5x past the largest existing point.
UDT_TAG_COUNTS = [1, 2, 5, 10, 25, 50, 100, 200, 500]
ARRAY_COUNTS = [2, 10, 50]
UDT_ARRAY_COUNTS = [2, 10, 100, 500]


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    lint_or_raise(l5x, context=str(out_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(l5x, encoding="utf-8")
    append_manifest_row(out_name, description, "defscale", out_path, predicted_bytes(l5x))


def _aoi_defs(count: int) -> tuple[list[str], list[tuple[str, list[MemberSpec]]]]:
    """`count` definitions identical to gen_defscale's, so the two batches
    difference against each other with no shape term in between."""
    ins, outs, locals_ = _aoi_members()
    defs, storages = [], []
    for i in range(count):
        name = f"Aoi_D{i:03d}"
        aoi, storage = aoi_xml(
            name, input_params=ins, output_params=outs, local_tags=locals_,
            logic_rungs_xml=rung_xml(0, "OTE(OutBit);"),
        )
        defs.append(aoi)
        storages.append((name, storage))
    return defs, storages


def group_a_aoi_instances() -> int:
    n_files = 0

    # ONE definition, n instance tags, n calls -- and the same n instance
    # tags with ZERO calls at the control counts.
    defs, storages = _aoi_defs(1)
    aoi_name, storage = storages[0]
    for n in INST_COUNTS:
        inst_tags = "\n".join(tag_xml(f"Inst{i:03d}", aoi_name, udt_members=storage)
                              for i in range(n))
        calls = "\n".join(rung_xml(i, f"{aoi_name}(Inst{i:03d},0,0,OutBitTag);")
                          for i in range(n))
        _write(
            build_l5x(target_name=f"Dscale2AoiT{n:03d}",
                      tags_xml=inst_tags + "\n" + tag_xml("OutBitTag", "BOOL"),
                      extra_aoi_xml="\n".join(defs), extra_rungs_xml=calls),
            f"dscale2_aoi_d001_t{n:03d}_call",
            f"ONE AOI definition (identical to defscale's), {n} instance tags of it, each called "
            f"from its own rung. Definition count is PINNED AT 1, so any slope across this sweep "
            f"is per-instance and cannot be per-definition -- which is exactly what "
            f"defscale_aoiinst_n* could not say, because there n = definitions = instance tags = "
            f"calls all at once. Its measured -160/unit is worth 238 KB on AccuTally under the "
            f"per-instance reading and 6 KB under the per-definition reading.",
        )
        n_files += 1

        if n in CONTROL_COUNTS:
            _write(
                build_l5x(target_name=f"Dscale2AoiNc{n:03d}",
                          tags_xml=inst_tags, extra_aoi_xml="\n".join(defs)),
                f"dscale2_aoi_d001_t{n:03d}_nocall",
                f"ONE AOI definition, {n} instance tags, and ZERO calling rungs -- identical to "
                f"dscale2_aoi_d001_t{n:03d}_call with the logic removed. Differencing the pair "
                f"separates the cost of an instance's TAG from the cost of its CALL, which every "
                f"existing file confounds because it always has one call per instance.",
            )
            n_files += 1

    # ONE definition, ONE instance tag, called from n rungs -- the converse.
    # n=1 is deliberately skipped: one definition, one instance tag and one
    # call is byte-for-byte dscale2_aoi_d001_t001_call, and a second
    # sample_id pointing at identical content spends a conversion slot to
    # learn nothing.
    single_inst = tag_xml("Inst000", aoi_name, udt_members=storage)
    for n in [c for c in CONTROL_COUNTS if c > 1]:
        calls = "\n".join(rung_xml(i, f"{aoi_name}(Inst000,0,0,OutBitTag);") for i in range(n))
        _write(
            build_l5x(target_name=f"Dscale2AoiC{n:03d}",
                      tags_xml=single_inst + "\n" + tag_xml("OutBitTag", "BOOL"),
                      extra_aoi_xml="\n".join(defs), extra_rungs_xml=calls),
            f"dscale2_aoi_d001_t001_c{n:03d}",
            f"ONE AOI definition, ONE instance tag, called from {n} separate rungs against that "
            f"same backing tag. The converse control to dscale2_aoi_d001_t*: here CALL count "
            f"varies with instance count pinned at 1, so the two sweeps cross and the -160/unit "
            f"term is attributed to the tag or to the call outright rather than to whichever one "
            f"the fitter reaches first.",
        )
        n_files += 1

    # n definitions, one instance tag each, NO calls -- captured aoiinst
    # shape minus its logic, at the same counts.
    for d in (5, 20, 60):
        defs_d, storages_d = _aoi_defs(d)
        inst_tags = "\n".join(tag_xml(f"Inst_{name}", name, udt_members=st)
                              for name, st in storages_d)
        _write(
            build_l5x(target_name=f"Dscale2AoiD{d:03d}Nc", tags_xml=inst_tags,
                      extra_aoi_xml="\n".join(defs_d)),
            f"dscale2_aoi_d{d:03d}_t{d:03d}_nocall",
            f"{d} AOI definitions with ONE instance tag each and NO calling logic -- "
            f"defscale_aoiinst_n{d:03d} exactly, minus its {d} calling rungs. Differences "
            f"straight against that captured file to price the calls alone at real-file scale.",
        )
        n_files += 1
    return n_files


def group_b_aoi_arrays() -> int:
    defs, storages = _aoi_defs(1)
    aoi_name, storage = storages[0]
    n_files = 0
    for n in ARRAY_COUNTS:
        _write(
            build_l5x(target_name=f"Dscale2AoiArr{n:03d}",
                      tags_xml=tag_xml("InstArr", aoi_name, dimensions=(n,), udt_members=storage),
                      extra_aoi_xml="\n".join(defs)),
            f"dscale2_aoi_arr{n:03d}",
            f"ONE AOI definition and ONE tag that is an ARRAY of {n} instances of it, no calls. "
            f"If the measured -160/unit is per INSTANCE it scales with the {n} elements; if it is "
            f"per TAG it does not move across this sweep at all. Real programs carry arrays of AOI "
            f"instances, so this is a shape the model has to get right rather than a corner case.",
        )
        n_files += 1
    return n_files


def group_c_udt_tags() -> int:
    mems = _udt_members()
    n_files = 0
    for u in (1, 5, 25):
        types = [udt_xml(f"Udt_D{i:03d}", mems) for i in range(u)]
        counts = (UDT_TAG_COUNTS if u == 1 else [1, 10, 50] if u == 5 else [1, 10])
        for n in counts:
            tags = "\n".join(
                tag_xml(f"TagU{i:03d}N{j:03d}", f"Udt_D{i:03d}", udt_members=mems)
                for i in range(u) for j in range(n)
            )
            _write(
                build_l5x(target_name=f"Dscale2Udt{u:03d}T{n:03d}", tags_xml=tags,
                          extra_datatypes_xml="\n".join(types)),
                f"dscale2_udt_u{u:03d}_t{n:03d}",
                f"{u} UDT definition(s) (identical to defscale's) with {n} tag(s) of EACH, "
                f"{u * n} UDT tags in total. defscale_udttag_n* only ever built n UDTs with ONE "
                f"tag each, so its measured -19/unit cannot say whether the 3-byte term beyond "
                f"the -16/definition is per TAG or a one-off for a UDT that has any tag at all. "
                + ("Definition count is pinned at 1 here, so any slope is per-tag."
                   if u == 1 else
                   f"With u={u} and n swept, definition count and tag count are crossed, which "
                   f"also tests that the two terms are additive rather than interacting."),
            )
            n_files += 1

    types = [udt_xml("Udt_D000", mems)]
    for n in UDT_ARRAY_COUNTS:
        _write(
            build_l5x(target_name=f"Dscale2UdtArr{n:03d}",
                      tags_xml=tag_xml("TagArr", "Udt_D000", dimensions=(n,), udt_members=mems),
                      extra_datatypes_xml="\n".join(types)),
            f"dscale2_udt_arr{n:03d}",
            f"ONE UDT definition and ONE tag that is an array of {n} elements of it. Per-element "
            f"or per-tag for the 3-byte term, the same question group B asks for AOI instances. "
            f"Real programs are full of array-of-UDT tags, and the per-element reading is worth "
            f"100 KB on AccuTally's 33,574 UDT tags while the per-tag reading is worth a few "
            f"hundred bytes.",
        )
        n_files += 1
    return n_files


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    a = group_a_aoi_instances()
    b = group_b_aoi_arrays()
    c = group_c_udt_tags()
    print(f"Group A (AOI def/instance/call split): {a}")
    print(f"Group B (AOI instance arrays):         {b}")
    print(f"Group C (UDT def/tag split):           {c}")
    print(f"Total: {a + b + c}")


if __name__ == "__main__":
    main()
