"""Real-shaped AOI population tests, built from what actually correlates
with the MurrayBros under-estimate.

2026-09-05: the generated projects exist to test things seen in the real
projects whose significance was not understood -- not to restack shapes
whose answer was already known before the file was built.

That is a fair hit and this file is the response. A vocabulary diff of the
real corpus against every file this project has ever generated found **60
XML element types that appear in real exports and have never once been
generated**, and the AOI-population shape below is one of the things that
diff exposed.

WHY THESE FEATURES. The residual on all nine real programs was regressed
against structure (feat2, 2026-09-05). Everything at the top is AOI
internals -- not file size, which is what MurrayBros was being blamed on:

    AOI params typed AXIS_*   r=+0.889   ~21,356/unit
    rungs INSIDE AOI defs     r=+0.848   ~242/unit
    AOI definitions           r=+0.838   ~4,023/unit
    AOI local tags            r=+0.835   ~260/unit

MurrayBros is not out to lunch because it is small. It is **AOI-dense**:
453 AOI parameters, 280 local tags and 349 internal rungs inside 923 KB.
MRFP carries comparable AOI counts in a file 2.5x larger and lands at
-0.51%. Same processor, same firmware.

WHY THE EXISTING TESTS COULD NOT FIND THIS. The AOI-internal ladder that
set `aoi_logic_composite_surcharge_per_instr = 0` measured internal rungs
inside ONE definition with XIC/OTE content, and it was right about that.
It never varied the NUMBER of definitions, and never went near a real
parameter or local-tag count. Real AOIs here run 5-51 params (median 16),
0-60 locals (median 13), 0-54 rungs (median 12). The generated corpus tops
out at one definition with a handful of members -- so the per-definition
cost has been extrapolated ~19x on every real file.

The four correlates above are mutually collinear (an AOI-heavy program has
more of all of them), so fitting any one of them from the real files would
be the same mistake that produced three wrong surcharge fits and the
reversed shell hypothesis. These files break that collinearity instead.

  mbshape_asbuilt          19 definitions reproducing MurrayBros's real
                           (params, locals, rungs) profile per AOI. The
                           control: if this under-predicts by roughly the
                           same ~7%, the cause is confirmed to live in the
                           AOI population and nowhere else.

  mbshape_params_{05,10,20}   Total AOI parameters scaled, definition count
  mbshape_locals_{05,10,20}   and everything else held fixed. Three separate
  mbshape_rungs_{05,10,20}    ladders, one per member kind, so the per-param,
                           per-local and per-rung rates separate instead of
                           moving together.

  mbshape_defs_{n05,n19,n40}  THE KEY DISCRIMINATOR. The same TOTAL params,
                           locals and rungs redistributed over 5, 19 and 40
                           definitions. If the missing cost is per
                           DEFINITION these three separate sharply; if it
                           is per MEMBER they land on the same number. No
                           existing file can tell those two apart.

  mbshape_axis_{k0,k3}     Identical files except three AOIs carry an
                           AXIS_CIP_DRIVE parameter. Isolates the strongest
                           single correlate (+0.889) directly. The model
                           currently charges 22,656 bytes per axis
                           parameter -- the entire axis structure, per
                           parameter -- which is very likely wrong.

Every AOI here is storage-shaped (parameters hidden, not Required/Visible),
which is how most real AOI parameters are declared and which keeps the call
site a plain `Aoi(Instance);` rather than a 50-argument line.

Run: python -m sample_gen.gen_murraybros_shape
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, rungs_xml, tag_xml
from sample_gen.gen_axis_composite import _AXIS_TAG_XML
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, predicted_bytes
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "mbshape"

# MurrayBros's real AOI population, read straight out of the file:
# (params, locals, rungs) per definition. Median 16/13/12, max 51/60/54.
REAL_PROFILE = [
    (20, 60, 53), (50, 25, 54), (50, 21, 28), (37, 30, 36), (47, 17, 25),
    (46, 13, 11), (51, 4, 12), (27, 10, 15), (8, 27, 27), (18, 11, 12),
    (16, 13, 22), (11, 13, 10), (11, 8, 11), (5, 13, 0), (11, 5, 11),
    (11, 4, 9), (15, 0, 1), (9, 4, 6), (10, 2, 6),
]
TOTAL_P = sum(p for p, _, _ in REAL_PROFILE)   # 453
TOTAL_L = sum(l for _, l, _ in REAL_PROFILE)   # 280
TOTAL_R = sum(r for _, _, r in REAL_PROFILE)   # 349


def _members(prefix: str, n: int) -> list[MemberSpec]:
    """A realistic type mix, not 40 identical DINTs -- real AOI members are
    mostly BOOL and REAL with some DINT, and type affects packing."""
    types = ["BOOL", "BOOL", "REAL", "DINT", "BOOL", "REAL"]
    return [MemberSpec(f"{prefix}{i}", types[i % len(types)]) for i in range(n)]


def _build(name: str, profile, axis_indices=(), description: str = "") -> None:
    defs, tags = [], []
    for idx, (np_, nl, nr) in enumerate(profile):
        params = _members("P", np_)
        if idx in axis_indices:
            params = [MemberSpec("Drive_Axis", "AXIS_CIP_DRIVE")] + params[1:]
        aoi_name = f"MbAoi{idx:02d}"
        aoi, storage = aoi_xml(
            aoi_name,
            input_params=params,
            local_tags=_members("L", nl),
            logic_rungs_xml=rungs_xml(nr, lambda i: "XIC(EnableIn)OTE(EnableOut);") if nr else "",
        )
        defs.append(aoi)
        tags.append(tag_xml(f"Inst{idx:02d}", aoi_name, udt_members=storage))
    tags_xml = "\n".join(tags)
    if axis_indices:
        tags_xml = _AXIS_TAG_XML + "\n" + tags_xml
    l5x = build_l5x(target_name=name.replace("_", "")[:20],
                    tags_xml=tags_xml, extra_aoi_xml="\n".join(defs))
    out = OUT_ROOT / f"{name}.L5X"
    lint_or_raise(l5x, context=str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(l5x, encoding="utf-8")
    append_manifest_row(name, description, "mbshape", out, predicted_bytes(l5x))
    print(f"Wrote {out}")


def _scaled(profile, which: int, factor: float):
    out = []
    for t in profile:
        v = list(t)
        v[which] = max(int(round(v[which] * factor)), 0)
        out.append(tuple(v))
    return out


def _redistribute(n_defs: int):
    """Same totals, spread over n_defs definitions."""
    per_p, per_l, per_r = TOTAL_P // n_defs, TOTAL_L // n_defs, TOTAL_R // n_defs
    prof = [(per_p, per_l, per_r) for _ in range(n_defs)]
    # push the remainder onto the first definition so totals match exactly
    rp, rl, rr = TOTAL_P - per_p * n_defs, TOTAL_L - per_l * n_defs, TOTAL_R - per_r * n_defs
    prof[0] = (prof[0][0] + rp, prof[0][1] + rl, prof[0][2] + rr)
    return prof


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    _build("mbshape_asbuilt", REAL_PROFILE, description=(
        f"19 AOI definitions reproducing MurrayBros's REAL per-AOI profile "
        f"({TOTAL_P} params / {TOTAL_L} locals / {TOTAL_R} internal rungs). Control "
        f"file: if this under-predicts by roughly MurrayBros's ~7%, the missing "
        f"cost is confirmed to live in the AOI population"))

    for label, which, tot in (("params", 0, TOTAL_P), ("locals", 1, TOTAL_L), ("rungs", 2, TOTAL_R)):
        for tag, factor in (("05", 0.5), ("10", 1.0), ("20", 2.0)):
            _build(f"mbshape_{label}_{tag}", _scaled(REAL_PROFILE, which, factor),
                   description=(
                       f"MurrayBros AOI profile with total AOI {label} scaled x{factor} "
                       f"(~{int(tot*factor)}), definition count and the other two member "
                       f"kinds held FIXED -- separates the per-{label[:-1]} rate from the "
                       f"other collinear AOI correlates"))

    for n in (5, 19, 40):
        _build(f"mbshape_defs_n{n:02d}", _redistribute(n), description=(
            f"The SAME totals ({TOTAL_P} params / {TOTAL_L} locals / {TOTAL_R} rungs) "
            f"spread over {n} AOI definitions instead of 19. Key discriminator: if the "
            f"missing cost is per-DEFINITION these separate sharply; if per-MEMBER they "
            f"land on the same number. No existing file can tell those apart"))

    for tag, idx in (("k0", ()), ("k3", (0, 8, 10))):
        _build(f"mbshape_axis_{tag}", REAL_PROFILE, axis_indices=idx, description=(
            f"MurrayBros AOI profile with {len(idx)} AXIS_CIP_DRIVE parameter(s) "
            f"(MurrayBros has 3). Isolates the strongest single residual correlate "
            f"(r=+0.889); the model charges 22,656 bytes per axis parameter today"))

    print("\nDone.")


if __name__ == "__main__":
    main()
