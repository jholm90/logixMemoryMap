"""Cross-category ADDITIVITY -- the one thing every sweep so far assumed.

This project's formulas were each fitted by scaling ONE thing at a time,
and within a category they hold perfectly, at any size:

    instr_cpt_n{10..5000}          27 KB -> 2.28 MB   flat -23 bytes
    randommix (27,267 rungs, 24 types)  50 KB -> 1.39 MB   flat -23 bytes
    stringoverhead_custom*         18 KB -> 1.11 MB   0 or +8

A constant, not a rate. Pure logic and pure data are exact to megabyte
scale, and mixing two dozen instruction types changes nothing.

Composite files, which mix UDTs, AOIs, arrays, modules and rungs at once,
do not behave that way at all -- and the way they fail is the finding:

    composite  <200 KB      n= 27   median -3.09%
    composite  200KB-1MB    n= 14   median -3.35%
    composite  1-3 MB       n=124   median +2.53%
    real programs           n= 16   median -1.69%  (flat across sizes)

The sign FLIPS with size on synthetic composites while real programs sit
at -1.7% regardless. Since every single-category sweep is exact at every
size, a size-dependent term cannot be the explanation. What is left is an
INTERACTION: the categories are not additive when combined, and the
composite generator scales all of them together so it can never say which
pair is responsible.

This batch says which, by construction. For each PAIR of categories it
builds a 3x3 grid at levels (none, mid, high) and nothing else varies.
Additivity is then a direct subtraction rather than a fit:

    residual(a,b) = cost(a,b) - cost(a,0) - cost(0,b) + cost(0,0)

Zero means the two categories are additive. Anything else is the
interaction term, measured, with its sign and size, for that specific
pair. Four categories give six pairs:

    D  data        UDT-typed tags, a fixed 10-member UDT
    L  logic       rungs of a fixed instruction mix
    A  AOI         instances of one fixed AOI definition
    M  modules     real 1756-IB16 blocks on the local chassis

The corner cells repeat across pairs on purpose -- every (0,0), and each
axis point, is built more than once. Those repeats are free replication:
if two files that should be byte-identical are not, the batch says so
before any interaction is read out of it.
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import (
    MemberSpec,
    aoi_xml,
    module_1756_digital_input_xml,
    rung_xml,
    tag_xml,
    udt_xml,
)
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, predicted_bytes
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "additivity"
CATEGORY = "additivity"

# Levels per category. Chosen so the high corner stays near 1 MB -- big
# enough to sit in the band where composites flip sign, small enough that
# 54 files convert in reasonable time.
LEVELS = {
    "D": (0, 40, 400),      # UDT-typed tags
    "L": (0, 400, 4000),    # rungs
    "A": (0, 20, 200),      # AOI instances
    "M": (0, 4, 16),        # I/O modules
}
LEVEL_NAME = ("n", "m", "h")   # none / mid / high

PAIRS = (("D", "L"), ("D", "A"), ("D", "M"), ("L", "A"), ("L", "M"), ("A", "M"))

UDT_NAME = "AddUdtProbe"
AOI_NAME = "AddAoiProbe"

_UDT_MEMBERS = [MemberSpec(f"Mbr{i:02d}", "DINT") for i in range(10)]
_AOI_INPUTS = [MemberSpec("InA", "DINT", required=True)]
_AOI_OUTPUTS = [MemberSpec("OutA", "BOOL", required=True)]
_AOI_LOCALS = [MemberSpec("Wrk", "DINT")]


def _aoi():
    return aoi_xml(
        AOI_NAME,
        input_params=_AOI_INPUTS,
        output_params=_AOI_OUTPUTS,
        local_tags=_AOI_LOCALS,
        logic_rungs_xml=rung_xml(0, "OTE(OutA);"),
    )


def _write(l5x: str, name: str, description: str) -> None:
    out = OUT_ROOT / f"{name}.L5X"
    lint_or_raise(l5x, context=str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(l5x, encoding="utf-8")
    append_manifest_row(name, description, CATEGORY, out, predicted_bytes(l5x))
    print(f"Wrote {out}")


def _build(d: int, l: int, a: int, mods: int) -> str:
    """One cell of the grid. Everything not named by the two axes is zero,
    so the only thing separating two cells is the level of one category."""
    datatypes = udt_xml(UDT_NAME, _UDT_MEMBERS) if d else ""
    aoi_def, aoi_storage = _aoi() if a else ("", None)

    tags = []
    tags += [tag_xml(f"DataTag{i:04d}", UDT_NAME, udt_members=_UDT_MEMBERS) for i in range(d)]
    tags += [
        tag_xml(f"AoiInst{i:04d}", AOI_NAME, udt_members=aoi_storage)
        for i in range(a)
    ]
    # An AOI instance only exists as a cost if something calls it; the call
    # rungs are part of the A axis, not the L axis, and are excluded from
    # the L level so the two axes stay independent.
    rungs = [rung_xml(i, "XIC(Bit0)MOV(1,Dst0)ADD(Dst0,1,Dst0)OTE(Bit1);") for i in range(l)]
    rungs += [rung_xml(l + i, f"{AOI_NAME}(AoiInst{i:04d},0,Bit1);") for i in range(a)]
    if not rungs:
        rungs = [rung_xml(0, "NOP();")]
    # Operands every L rung needs, present in every file including the
    # zero cells so their own cost cancels in the subtraction.
    tags += [tag_xml("Bit0", "BOOL"), tag_xml("Bit1", "BOOL"), tag_xml("Dst0", "DINT")]

    modules_xml = ""
    if mods:
        modules_xml = "\n".join(
            module_1756_digital_input_xml(f"DiMod{i:02d}", slot=i + 1) for i in range(mods)
        )

    return build_l5x(
        target_name="AddProbe",
        tags_xml="\n".join(tags),
        extra_datatypes_xml=datatypes,
        extra_aoi_xml=aoi_def,
        extra_rungs_xml="\n".join(rungs),
        extra_modules_xml=modules_xml,
    )


def main() -> None:
    seen: set[tuple[int, int, int, int]] = set()
    for x, y in PAIRS:
        for ix, xv in enumerate(LEVELS[x]):
            for iy, yv in enumerate(LEVELS[y]):
                vals = {"D": 0, "L": 0, "A": 0, "M": 0}
                vals[x], vals[y] = xv, yv
                key = (vals["D"], vals["L"], vals["A"], vals["M"])
                if key in seen:
                    continue   # a corner already built by an earlier pair
                seen.add(key)
                sid = (f"addit_{x.lower()}{LEVEL_NAME[ix]}"
                       f"_{y.lower()}{LEVEL_NAME[iy]}")
                _write(
                    _build(**{"d": vals["D"], "l": vals["L"],
                              "a": vals["A"], "mods": vals["M"]}),
                    sid,
                    f"Additivity grid cell: {x}={xv}, {y}={yv}, every other "
                    f"category at zero. D=UDT-typed tags, L=rungs, A=AOI "
                    f"instances, M=1756-IB16 modules. With the three other "
                    f"cells of its 2x2 the residual "
                    f"cost(a,b)-cost(a,0)-cost(0,b)+cost(0,0) is the "
                    f"interaction between {x} and {y}, measured directly "
                    f"rather than fitted. OQ-COMPOSITESCALE.",
                )


if __name__ == "__main__":
    main()
