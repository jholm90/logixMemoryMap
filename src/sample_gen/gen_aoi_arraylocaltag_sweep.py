"""OQ-AOIARRAYDIMENSION array-LocalTag isolation sweep (James, 2026-09-03:
"the two localTag needs more generated tests - generate more than enough
tests to validate this").

Both real data points on file for an AOI array LocalTag
(aoi_array_localtag_def_only: +404/2.05%, aoi_array_localtag_1_instance:
+400/1.98%) are near-identical regardless of instance presence, at the
SAME single dimension (100) and type (DINT) -- not enough to tell whether
the gap is a flat per-array-LocalTag declaration cost or actually scales
with dimension/element size. The current aoi_definition formula
(memory_model.yaml) charges `per_declared_item` once per declared
Parameter/LocalTag regardless of its `dimension` -- i.e. today's model
predicts ZERO effect from array size, so if the real gap DOES scale with
dimension this is a genuine missing term, not just a fixed offset.

Five isolating groups, each varying exactly one axis:

  A. group_dimension_def_only -- DINT array LocalTag, 0 instances, 7
     dimension points (10/25/50/100/250/500/1000). Isolates whether the
     gap scales with array size at all.
  B. group_dimension_1_instance -- same 7 dimensions, 1 instance. Confirms
     group A's shape holds (or doesn't) once real storage exists too.
  C. group_type_def_only -- fixed dimension=50, 0 instances, across
     SINT/INT/DINT/REAL/BOOL. Isolates whether the gap depends on
     per-element byte width.
  D. group_type_1_instance -- same 5 types at dimension=50, 1 instance.
  E. group_multiplicity -- 1/2/3 independent DINT[50] array LocalTags in
     the SAME AOI, 0 instances. Isolates whether the gap is additive per
     array-LocalTag declared, or a one-time AOI-level cost.

27 files total -- every one answers a specific axis of this one question,
not filler.

Run: python -m sample_gen.gen_aoi_arraylocaltag_sweep
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"

_DIMENSIONS = [10, 25, 50, 100, 250, 500, 1000]
_TYPES = ["SINT", "INT", "DINT", "REAL", "BOOL"]


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _def_only(aoi_name: str, locals_: list[MemberSpec]) -> str:
    definition, _storage = aoi_xml(aoi_name, [], [], [], locals_)
    return build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)


def _one_instance(aoi_name: str, locals_: list[MemberSpec]) -> str:
    definition, storage = aoi_xml(aoi_name, [], [], [], locals_)
    tag = tag_xml("TestInstance", aoi_name, udt_members=storage)
    return build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)


def group_dimension_def_only() -> None:
    for dim in _DIMENSIONS:
        aoi_name = f"ArrLocalDimN{dim}AOI"
        locals_ = [MemberSpec("Buffer", "DINT", dimension=dim)]
        l5x = _def_only(aoi_name, locals_)
        _write(l5x, f"aoi_arraylocal_dim_n{dim:05d}_def_only",
               f"AOI with a {dim}-element DINT array LocalTag, 0 instances -- dimension-scaling isolation point")


def group_dimension_1_instance() -> None:
    for dim in _DIMENSIONS:
        aoi_name = f"ArrLocalDimN{dim}Inst1AOI"
        locals_ = [MemberSpec("Buffer", "DINT", dimension=dim)]
        l5x = _one_instance(aoi_name, locals_)
        _write(l5x, f"aoi_arraylocal_dim_n{dim:05d}_1_instance",
               f"AOI with a {dim}-element DINT array LocalTag, 1 instance -- dimension-scaling isolation point")


def group_type_def_only() -> None:
    for t in _TYPES:
        aoi_name = f"ArrLocalType{t}AOI"
        locals_ = [MemberSpec("Buffer", t, dimension=50)]
        l5x = _def_only(aoi_name, locals_)
        _write(l5x, f"aoi_arraylocal_type_{t.lower()}_n00050_def_only",
               f"AOI with a 50-element {t} array LocalTag, 0 instances -- element-byte-width isolation point")


def group_type_1_instance() -> None:
    for t in _TYPES:
        aoi_name = f"ArrLocalType{t}Inst1AOI"
        locals_ = [MemberSpec("Buffer", t, dimension=50)]
        l5x = _one_instance(aoi_name, locals_)
        _write(l5x, f"aoi_arraylocal_type_{t.lower()}_n00050_1_instance",
               f"AOI with a 50-element {t} array LocalTag, 1 instance -- element-byte-width isolation point")


def group_multiplicity() -> None:
    for count in [1, 2, 3]:
        aoi_name = f"ArrLocalMult{count}AOI"
        locals_ = [MemberSpec(f"Buffer{i}", "DINT", dimension=50) for i in range(count)]
        l5x = _def_only(aoi_name, locals_)
        _write(l5x, f"aoi_arraylocal_multiplicity_n{count:02d}_def_only",
               f"AOI with {count} independent 50-element DINT array LocalTag(s), 0 instances -- "
               f"additive-per-array-LocalTag isolation point")


def main() -> None:
    group_dimension_def_only()
    group_dimension_1_instance()
    group_type_def_only()
    group_type_1_instance()
    group_multiplicity()
    total = len(_DIMENSIONS) * 2 + len(_TYPES) * 2 + 3
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
