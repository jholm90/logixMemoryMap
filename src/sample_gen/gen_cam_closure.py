"""Close CAM and CAM_PROFILE for the shape real programs actually use.

Both structures already have a standalone-TAG count sweep, and both fit
their formulas cleanly -- CAM at base + 12/element, CAM_PROFILE at
base(4) + 56/element, with the CAM_PROFILE sweep exact to the byte at
n=1/5/20/50. What that sweep does NOT cover is how these types appear in
real programs.

Across the real corpus, every single use is an ARRAY, and the dominant
shape is an array MEMBER INSIDE A UDT -- never a standalone tag:

    UDT members   CAM[20] x9   CAM[10] x8   CAM_PROFILE[20] x7
                  CAM_PROFILE[10] x6   CAM_PROFILE[30] x3   CAM[30] x2
    tags          dimensions 2, 5, 10, 11, 20, 30, 50, 100

Elmsdale's CamArray is the canonical shape and nothing like it has ever
been tested: one UDT carrying CAM[10] and CAM_PROFILE[10] side by side,
wrapped by an outer UDT, reached from a tag two levels down.

There are also ZERO scalar uses anywhere in the corpus -- no
Dimension="0" member, no undimensioned tag -- which is worth pinning
rather than assuming, since the engine cannot currently size one.

GROUP A -- camx_tag_{cam,prof}_n{002,010,011,030,100} (10 files)
    Extends the standalone-tag sweep onto the array sizes real programs
    actually declare. The existing sweep stopped at 50 and never tested
    11 or 100, both of which appear in real tags.

GROUP B -- camx_member_{cam,prof}_d{04,10,20,30} (8 files)
    One UDT, one CAM or CAM_PROFILE array member, at the four dimensions
    the real corpus uses. This is the shape the whole batch exists for:
    the formulas were fitted on standalone tags, and a UDT member is a
    different container. Differenced against GROUP A at the same count,
    any container-specific cost falls out.

GROUP C -- camx_mixed_d{10,20} (2 files)
    CAM and CAM_PROFILE together in one UDT, which is exactly Elmsdale's
    CamArray. Tests whether the two compose additively or whether sharing
    a UDT changes either one.

GROUP D -- camx_nested_i{01,05} (2 files)
    The mixed UDT wrapped inside an outer UDT, reached from a tag -- the
    real EdgerArbor -> SawCams -> CamArray depth. One instance and five,
    so per-instance cost separates from the one-time definition.

GROUP E -- camx_udtarray_n05 (1 file)
    An ARRAY of the mixed UDT: array-of-UDT-containing-array-of-
    predefined, which no test in this project covers at all.

GROUP F -- camx_multitag_{cam,prof}_t05 (2 files)
    Five separate tags of the same array type, against GROUP A's single
    tag at the same count. Separates per-tag overhead from per-element
    cost, which a single-tag sweep cannot do.

GROUP G -- camx_scalar_{cam,prof} (2 files)
    A UDT with a Dimension="0" CAM / CAM_PROFILE member. No real program
    does this and the engine cannot size it, so the question is simply
    whether Logix accepts it. A conversion failure here is a RESULT --
    it closes the scalar case as "not legal" rather than leaving it as an
    unsized hole. Recorded either way.

27 files, 1756-L81E v35.

Run: python -m sample_gen.gen_cam_closure
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, cam_profile_tag_xml, cam_tag_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "predefined"
CATEGORY = "cam_closure"

# The dimensions the real corpus actually declares, so every point tests a
# shape that exists rather than a round number.
REAL_TAG_DIMS = (2, 10, 11, 30, 100)
REAL_MEMBER_DIMS = (4, 10, 20, 30)


def _write(l5x: str, out_name: str, description: str) -> int:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, description, CATEGORY, out_path, 0)
    print(f"Wrote {out_path}")
    return 1


def _target(out_name: str) -> str:
    return "".join(p.capitalize() for p in out_name.split("_"))[:40]


def group_a_tag_sweep() -> int:
    n = 0
    for label, builder, type_name in (("cam", cam_tag_xml, "CAM"),
                                      ("prof", cam_profile_tag_xml, "CAM_PROFILE")):
        for count in REAL_TAG_DIMS:
            out = f"camx_tag_{label}_n{count:03d}"
            n += _write(
                build_l5x(target_name=_target(out), tags_xml=builder("CamData", count)),
                out,
                f"ONE standalone {type_name}[{count}] tag. Extends the existing count sweep onto "
                f"array sizes real programs declare -- that sweep stopped at 50 and never tested "
                f"11 or 100, both of which appear in real tags",
            )
    return n


def _member_udt(udt_name: str, members: list[MemberSpec]) -> str:
    return udt_xml(udt_name, members)


def group_b_udt_member() -> int:
    """The shape the batch exists for: the formulas were fitted on tags."""
    n = 0
    for label, type_name in (("cam", "CAM"), ("prof", "CAM_PROFILE")):
        for dim in REAL_MEMBER_DIMS:
            udt_name = f"CamHolder{label.capitalize()}{dim:02d}"
            out = f"camx_member_{label}_d{dim:02d}"
            n += _write(
                build_l5x(
                    target_name=_target(out),
                    extra_datatypes_xml=_member_udt(
                        udt_name, [MemberSpec("Profile", type_name, dimension=dim)]),
                    tags_xml=tag_xml("Holder", udt_name),
                ),
                out,
                f"ONE UDT carrying a single {type_name}[{dim}] member -- the shape real programs "
                f"actually use ({type_name}[{dim}] appears as a UDT member in the real corpus). "
                f"Differenced against camx_tag_{label}_n* at the same count, any cost specific to "
                f"the UDT container falls out",
            )
    return n


def _mixed_members(dim: int) -> list[MemberSpec]:
    """Elmsdale's CamArray, member for member."""
    return [MemberSpec("CAM", "CAM", dimension=dim),
            MemberSpec("CAMPROFILE", "CAM_PROFILE", dimension=dim)]


def group_c_mixed() -> int:
    n = 0
    for dim in (10, 20):
        udt_name = f"CamArrayMix{dim:02d}"
        out = f"camx_mixed_d{dim:02d}"
        n += _write(
            build_l5x(target_name=_target(out),
                      extra_datatypes_xml=_member_udt(udt_name, _mixed_members(dim)),
                      tags_xml=tag_xml("Mixed", udt_name)),
            out,
            f"CAM[{dim}] and CAM_PROFILE[{dim}] side by side in ONE UDT -- member for member the "
            f"real CamArray shape. Tests whether the two compose additively or whether sharing a "
            f"UDT changes either",
        )
    return n


def group_d_nested() -> int:
    n = 0
    inner = "CamArrayInner"
    for instances in (1, 5):
        outer = f"CamOuter{instances:02d}"
        members = [MemberSpec(f"Cams{i:02d}", inner, nested_members=tuple(_mixed_members(10)))
                   for i in range(instances)]
        out = f"camx_nested_i{instances:02d}"
        n += _write(
            build_l5x(
                target_name=_target(out),
                extra_datatypes_xml="\n".join([
                    _member_udt(inner, _mixed_members(10)),
                    _member_udt(outer, members),
                ]),
                tags_xml=tag_xml("Arbor", outer),
            ),
            out,
            f"Outer UDT holding {instances} instance(s) of a CAM[10]+CAM_PROFILE[10] UDT, reached "
            f"from a tag -- the real EdgerArbor -> SawCams -> CamArray depth. One instance against "
            f"five separates per-instance cost from the one-time definition",
        )
    return n


def group_e_array_of_mixed() -> int:
    udt_name = "CamArrayElem"
    out = "camx_udtarray_n05"
    return _write(
        build_l5x(target_name=_target(out),
                  extra_datatypes_xml=_member_udt(udt_name, _mixed_members(10)),
                  tags_xml=tag_xml("Bank", udt_name, dimensions=(5,))),
        out,
        "A 5-element ARRAY of a UDT that itself carries CAM[10] and CAM_PROFILE[10] -- "
        "array-of-UDT-containing-array-of-predefined, a nesting no test in this project covers",
    )


def group_f_multi_tag() -> int:
    n = 0
    for label, builder, type_name in (("cam", cam_tag_xml, "CAM"),
                                      ("prof", cam_profile_tag_xml, "CAM_PROFILE")):
        tags = "\n".join(builder(f"CamData{i:02d}", 10) for i in range(5))
        out = f"camx_multitag_{label}_t05"
        n += _write(
            build_l5x(target_name=_target(out), tags_xml=tags), out,
            f"FIVE separate {type_name}[10] tags. Against camx_tag_{label}_n010's single tag at "
            f"the same count, this separates per-tag overhead from per-element cost -- something "
            f"a one-tag-per-file sweep cannot do however many counts it walks",
        )
    return n


def group_g_scalar_probe() -> int:
    """Not legal as far as the corpus shows. A failure here IS the answer."""
    n = 0
    for label, type_name in (("cam", "CAM"), ("prof", "CAM_PROFILE")):
        udt_name = f"CamScalar{label.capitalize()}"
        out = f"camx_scalar_{label}"
        n += _write(
            build_l5x(target_name=_target(out),
                      extra_datatypes_xml=_member_udt(
                          udt_name, [MemberSpec("Single", type_name, dimension=0)]),
                      tags_xml=tag_xml("Scalar", udt_name)),
            out,
            f"A UDT with a SCALAR (Dimension=0) {type_name} member. No real program in the corpus "
            f"does this and the engine cannot size it, so the question is whether Logix even "
            f"accepts it. A conversion failure is a RESULT here -- it closes the scalar case as "
            f"not legal rather than leaving an unsized hole",
        )
    return n


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    total = 0
    for fn in (group_a_tag_sweep, group_b_udt_member, group_c_mixed, group_d_nested,
               group_e_array_of_mixed, group_f_multi_tag, group_g_scalar_probe):
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
