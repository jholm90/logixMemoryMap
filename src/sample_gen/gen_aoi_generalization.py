"""AOI generalization batch (2026-08-25): confirms whether the two new
formulas found this session hold beyond the single AOI shape each was
derived from, per docs/AOI_KNOWLEDGE_MAP.md's own next-step call-outs.

  A. group_boolpack_membercount -- the array-of-instances BOOL-packing
     formula (marginal_bytes_per_instance = 124 - 4*bool_member_count) was
     confirmed at EXACTLY ONE total member count (30, across 8 real data
     points -- see AOI_KNOWLEDGE_MAP.md unknown #2). Every point landed on
     the formula with ~zero residual, but that's not proof the "-4/bool"
     rate or the "124" pure-atomic intercept hold at a different total
     member count -- it's equally plausible the real mechanism depends on
     total member count, not just BOOL count. Repeats the same ratio-sweep
     methodology at member_count=10/20/60 (bracketing the confirmed 30) --
     for each, 5 ratio points (0%/~10%/50%/~90%/100% BOOL) at 3 instance
     counts (1/10/25) for a genuine 2-interval marginal-cost check per
     ratio, not just a 2-point line.

  B. group_boolpack_layout -- same 30-member/15-BOOL shape the original
     "exactly 64/instance" half-BOOL finding was built on, but with BOOL
     members positioned differently (all-first / all-last / interspersed)
     instead of always grouped together. Tests whether the formula depends
     on BOOL *count* alone (as hypothesized) or also on member *layout*.

  C. group_defcost_paramtype -- the AOI-definition-cost formula
     (~1200 + 18*param_count) was confirmed ONLY with DINT Input params.
     Repeats the same paramcount_n02/04/08_def_only shape with INT, BOOL,
     and REAL Input params instead, to see whether 18/param holds for
     other atomic types or is DINT-specific.

  D. group_defcost_direction -- same formula, same DINT type, but Output
     and InOut param direction instead of Input (at n=4/8, matching the
     confirmed Input points) -- tests whether direction affects
     definition cost at all.

Run: python -m sample_gen.gen_aoi_generalization
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

AOI_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"


def _write(l5x: str, out_name: str, description: str, category: str) -> int:
    out_path = AOI_OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, category, out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 1


# ---------------------------------------------------------------------------
# A. BOOL-packing ratio sweep at other total member counts
# ---------------------------------------------------------------------------

def _ratio_points(member_count: int) -> list[int]:
    pts = sorted({0, max(1, round(member_count * 0.1)), member_count // 2,
                  member_count - max(1, round(member_count * 0.1)), member_count})
    return pts


def group_boolpack_membercount() -> int:
    n = 0
    for member_count in [10, 20, 60]:
        for bool_count in _ratio_points(member_count):
            atomic_count = member_count - bool_count
            aoi_name = f"AoiMcGen{member_count}B{bool_count}"
            inputs = ([MemberSpec(f"InB{i}", "BOOL") for i in range(bool_count)]
                      + [MemberSpec(f"InA{i}", "DINT") for i in range(atomic_count)])
            definition, storage = aoi_xml(aoi_name, inputs, [], [], [])
            out_prefix = f"aoipack_mc{member_count:02d}_b{bool_count:02d}"
            for count in [1, 10, 25]:
                tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(count,), udt_members=storage)
                l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
                n += _write(l5x, f"{out_prefix}_array_n{count:02d}",
                            f"AOI, {bool_count} BOOL + {atomic_count} DINT Input params "
                            f"({member_count} total members), array of {count} instances -- "
                            f"BOOL-packing member-count generalization (vs. the 30-member confirmation)",
                            "aoi_array_packing")
    return n


# ---------------------------------------------------------------------------
# B. BOOL-packing layout sweep (30 members, 15 BOOL, position varies)
# ---------------------------------------------------------------------------

def group_boolpack_layout() -> int:
    n = 0
    bool_members = [MemberSpec(f"InB{i}", "BOOL") for i in range(15)]
    atomic_members = [MemberSpec(f"InA{i}", "DINT") for i in range(15)]
    interspersed = []
    for b, a in zip(bool_members, atomic_members):
        interspersed.append(b)
        interspersed.append(a)
    layouts = {
        "boolfirst": bool_members + atomic_members,
        "boollast": atomic_members + bool_members,
        "interspersed": interspersed,
    }
    for label, inputs in layouts.items():
        aoi_name = f"AoiLayout{label.title()}"
        definition, storage = aoi_xml(aoi_name, inputs, [], [], [])
        out_prefix = f"aoipack_layout_{label}"
        for count in [1, 25]:
            tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(count,), udt_members=storage)
            l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
            n += _write(l5x, f"{out_prefix}_array_n{count:02d}",
                        f"AOI, 15 BOOL + 15 DINT Input params, {label} layout (30 total members), "
                        f"array of {count} instances -- does BOOL-packing depend on member position, "
                        f"not just count",
                        "aoi_array_packing")
    return n


# ---------------------------------------------------------------------------
# C. AOI definition cost across param TYPES (Input, DINT confirmed already)
# ---------------------------------------------------------------------------

def group_defcost_paramtype() -> int:
    n = 0
    for dtype in ["INT", "BOOL", "REAL"]:
        for count in [2, 4, 8]:
            params = [MemberSpec(f"P{i}", dtype) for i in range(count)]
            aoi_name = f"AoiDefType{dtype}N{count:02d}"
            definition, _ = aoi_xml(aoi_name, params, [], [], [])
            l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
            n += _write(l5x, f"aoidefcost_type{dtype.lower()}_n{count:02d}_def_only",
                        f"AOI with {count} {dtype} Input params, 0 instances -- definition-cost "
                        f"param-TYPE generalization (vs. the DINT-only confirmation, ~1200+18/param)",
                        "aoi")
    return n


# ---------------------------------------------------------------------------
# D. AOI definition cost across param DIRECTION (DINT, Input confirmed already)
# ---------------------------------------------------------------------------

def group_defcost_direction() -> int:
    n = 0
    for direction in ["output", "inout"]:
        for count in [4, 8]:
            params = [MemberSpec(f"P{i}", "DINT") for i in range(count)]
            aoi_name = f"AoiDefDir{direction.title()}N{count:02d}"
            if direction == "output":
                definition, _ = aoi_xml(aoi_name, [], params, [], [])
            else:
                definition, _ = aoi_xml(aoi_name, [], [], params, [])
            l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
            n += _write(l5x, f"aoidefcost_dir{direction}_n{count:02d}_def_only",
                        f"AOI with {count} DINT {direction.title()} params, 0 instances -- definition-cost "
                        f"param-DIRECTION generalization (vs. the Input-only confirmation)",
                        "aoi")
    return n


def main() -> None:
    total = 0
    for fn in [group_boolpack_membercount, group_boolpack_layout,
               group_defcost_paramtype, group_defcost_direction]:
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
