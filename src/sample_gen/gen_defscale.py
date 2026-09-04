"""Definition-COUNT scaling: how does cost grow with the NUMBER of AOI
definitions and UDT definitions in a project?

Why this batch exists (2026-09-04). After the shellscale_* batch settled
OQ-SHELLSCALE, the real-file residual was re-regressed against structure.
Programs and routines collapsed as explanations (r=+0.43 and +0.58, down
from +0.87/+0.83 before the shell refit -- they WERE the collinear
red herring the isolation showed them to be). What rose to the top:

    aoidefs   r=+0.878
    udts      r=+0.838

Then the corpus was checked before fitting anything, and the gap is stark.
Across all 1,961 captured non-real files, the maximum is **7 AOI
definitions** and **6 UDTs**, and 308 of the 312 files with any AOI at all
have exactly ONE. The nine real programs carry 11-39 AOI definitions and
53-174 UDTs. So every prediction on a real file extrapolates the
per-definition cost 5x to 30x beyond the largest point it was ever
measured at, on both axes at once.

That is precisely the shape of the mistake shellscale just caught:
routine_extra/program_extra were fitted on n=2 files, extrapolated to
n=200, and were each exactly 8 bytes/unit wrong -- invisible at n=2, worth
1.97% at n=200. The existing 127 def-isolation files vary what is INSIDE
one definition beautifully (param count, param type, local tags, name
length, packing) and never once vary how MANY definitions there are.

So: do not fit a per-definition scaling term off the real files, where
aoidefs/udts/tags/rungs are all mutually collinear. Measure it in
isolation, the same way shellscale did, and let the answer be whatever it
is -- including "flat, the current model is already right", which is a
perfectly good outcome and is what the JSR-target and AOI-internal content
sweeps both returned.

The four sweeps, each varying ONE count and holding everything else fixed:

  defscale_aoidefs_n*        N identical minimal AOI defs, ZERO instances.
                             Isolates pure definition cost.
  defscale_aoiinst_n*        N identical minimal AOI defs, ONE instance
                             each. Same span. Subtracting the two sweeps
                             separates definition cost from instance cost
                             AT SCALE, which no existing file does.
  defscale_udts_n*           N identical minimal UDTs, ZERO tags of them.
  defscale_udttag_n*         N identical minimal UDTs, ONE tag each.

Every definition in a given file is byte-identical to its siblings apart
from its name, and names are fixed-width (Aoi_D000/Udt_D000), so name
length contributes a constant per definition and cannot masquerade as a
count effect.

Run: python -m sample_gen.gen_defscale
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml, udt_xml
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, predicted_bytes
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "defscale"

# Spans chosen to bracket the real files from below AND above. Real
# programs sit at 11-39 AOI defs and 53-174 UDTs, so the AOI sweep runs to
# 60 and the UDT sweep to 200 -- a fitted slope is then interpolation on a
# real file, not extrapolation, which is the whole point of the batch.
AOI_COUNTS = [1, 2, 5, 10, 20, 40, 60]
UDT_COUNTS = [1, 2, 5, 10, 25, 50, 100, 200]


def _aoi_members() -> tuple[list[MemberSpec], list[MemberSpec], list[MemberSpec]]:
    """Deliberately small but NOT empty -- 2 inputs, 1 output, 2 local tags.

    An empty shell risks measuring only a header and missing any
    per-definition cost that scales with the definition's own member
    table; anything large risks the member cost swamping the count effect
    this batch is built to see.
    """
    # required=True on the call-site params: an AOI parameter that is
    # neither Required nor Visible does not appear in the calling rung's
    # argument list at all (storage-only), and lint correctly rejects a
    # call passing arguments the declaration does not accept. Local tags
    # are storage-only by definition and take no flag.
    return (
        [MemberSpec("InA", "DINT", required=True),
         MemberSpec("InB", "DINT", required=True)],
        [MemberSpec("OutBit", "BOOL", required=True)],
        [MemberSpec("Work1", "DINT"), MemberSpec("Work2", "DINT")],
    )


def _udt_members() -> list[MemberSpec]:
    return [
        MemberSpec("MemA", "DINT"),
        MemberSpec("MemB", "REAL"),
        MemberSpec("MemC", "BOOL"),
    ]


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    lint_or_raise(l5x, context=str(out_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(l5x, encoding="utf-8")
    append_manifest_row(out_name, description, "defscale", out_path, predicted_bytes(l5x))
    print(f"Wrote {out_path}")


def _build_aoi_files() -> None:
    ins, outs, locals_ = _aoi_members()
    for n in AOI_COUNTS:
        defs, storages = [], []
        for i in range(n):
            aoi_name = f"Aoi_D{i:03d}"
            aoi, storage = aoi_xml(
                aoi_name, input_params=ins, output_params=outs, local_tags=locals_,
                logic_rungs_xml=rung_xml(0, "OTE(OutBit);"),
            )
            defs.append(aoi)
            storages.append((aoi_name, storage))

        # --- defs only, zero instances -----------------------------------
        _write(
            build_l5x(target_name=f"AoiDefs{n}", tags_xml="",
                      extra_aoi_xml="\n".join(defs)),
            f"defscale_aoidefs_n{n:03d}",
            f"{n} identical minimal AOI definitions (2 In/1 Out/2 Local), ZERO "
            f"instances -- isolates per-DEFINITION cost vs definition COUNT",
        )

        # --- same defs, one instance each ---------------------------------
        inst_tags = "\n".join(
            tag_xml(f"Inst_{name}", name, udt_members=storage)
            for name, storage in storages
        )
        calls = "\n".join(
            rung_xml(i, f"{name}(Inst_{name},0,0,OutBitTag);")
            for i, (name, storage) in enumerate(storages)
        )
        _write(
            build_l5x(target_name=f"AoiInst{n}",
                      tags_xml=inst_tags + "\n" + tag_xml("OutBitTag", "BOOL"),
                      extra_aoi_xml="\n".join(defs), extra_rungs_xml=calls),
            f"defscale_aoiinst_n{n:03d}",
            f"{n} identical minimal AOI definitions, each with exactly ONE "
            f"instance + call -- paired with defscale_aoidefs_n{n:03d} to split "
            f"definition cost from instance cost at scale",
        )


def _build_udt_files() -> None:
    mems = _udt_members()
    for n in UDT_COUNTS:
        types = [udt_xml(f"Udt_D{i:03d}", mems) for i in range(n)]

        _write(
            build_l5x(target_name=f"UdtDefs{n}", tags_xml="",
                      extra_datatypes_xml="\n".join(types)),
            f"defscale_udts_n{n:03d}",
            f"{n} identical minimal UDT definitions (DINT/REAL/BOOL), ZERO tags "
            f"of any of them -- isolates per-UDT-DEFINITION cost vs UDT COUNT",
        )

        tags = "\n".join(
            tag_xml(f"Tag_Udt_D{i:03d}", f"Udt_D{i:03d}", udt_members=mems)
            for i in range(n)
        )
        _write(
            build_l5x(target_name=f"UdtTag{n}", tags_xml=tags,
                      extra_datatypes_xml="\n".join(types)),
            f"defscale_udttag_n{n:03d}",
            f"{n} identical minimal UDT definitions, each with exactly ONE tag "
            f"-- paired with defscale_udts_n{n:03d} to split definition cost "
            f"from instance cost at scale",
        )


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    _build_aoi_files()
    _build_udt_files()
    print(f"\nDone. {len(AOI_COUNTS)*2 + len(UDT_COUNTS)*2} files.")


if __name__ == "__main__":
    main()
