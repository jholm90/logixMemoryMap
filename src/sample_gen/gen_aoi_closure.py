"""Small, targeted AOI additions (James, 2026-08-25, after the 64-file
generalization batch: "If there are additional testing you think of for
the aoi please process it" -- paired with his "don't just fill up the
minimum 60 test roster with filler work" instruction from the same
session, so this stays small and answers real, currently-open questions
only, not padded to any target count.

  A. group_boolpack_nonatomic_type -- the confirmed BOOL-packing formula
     (124 - 4*bool_count, see AOI_KNOWLEDGE_MAP.md) was derived entirely
     from BOOL+DINT ratio mixes. Never tested whether the "-4/bool" rate
     depends on what the OTHER (non-BOOL) member type is -- a BOOL+REAL
     or BOOL+SINT mix could plausibly pack differently if the mechanism
     has anything to do with word alignment of the non-BOOL members.
     Fixed member_count=30 (matching the original confirmation), 2 ratio
     points (10:20 and 20:10 split, mirroring 2 of the original 6 real
     ratios) x 2 non-BOOL types (REAL, SINT) x 2 instance counts.

  B. group_aoi_constant_flag -- James's Constant="true" question (raised
     for STRING/custom-string tags) applies just as naturally to an
     AOI-instance tag -- never tested for any UDT/AOI-typed tag in this
     project before. A simple AOI instance, Constant=true vs false.

Run: python -m sample_gen.gen_aoi_closure
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


def group_boolpack_nonatomic_type() -> int:
    n = 0
    for atomic_type in ["REAL", "SINT"]:
        for n_bool, n_atomic in [(10, 20), (20, 10)]:
            aoi_name = f"AoiBpNonAtomic{atomic_type}{n_bool:02d}b{n_atomic:02d}a"
            inputs = ([MemberSpec(f"InB{i}", "BOOL") for i in range(n_bool)]
                      + [MemberSpec(f"InA{i}", atomic_type) for i in range(n_atomic)])
            definition, storage = aoi_xml(aoi_name, inputs, [], [], [])
            out_prefix = f"aoipack_nonatomic_{atomic_type.lower()}_{n_bool:02d}b{n_atomic:02d}a"
            for count in [1, 25]:
                tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(count,), udt_members=storage)
                l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
                n += _write(l5x, f"{out_prefix}_array_n{count:02d}",
                            f"AOI, {n_bool} BOOL + {n_atomic} {atomic_type} Input params (ratio "
                            f"{n_bool}:{n_atomic} of 30), array of {count} instances -- does the "
                            f"confirmed BOOL-packing rate (124-4*bool_count) depend on the non-BOOL "
                            f"member type, tested so far only with DINT",
                            "aoi_array_packing")
    return n


def group_aoi_constant_flag() -> int:
    n = 0
    aoi_name = "AoiConstTest"
    inputs = [MemberSpec("P0", "DINT"), MemberSpec("P1", "BOOL")]
    definition, storage = aoi_xml(aoi_name, inputs, [], [], [])
    for const_label, const in [("const", True), ("nonconst", False)]:
        tag = tag_xml("TestInstance", aoi_name, udt_members=storage, constant=const)
        l5x = build_l5x(target_name=f"AoiConst{const_label.title()}", tags_xml=tag, extra_aoi_xml=definition)
        n += _write(l5x, f"aoiconst_{const_label}",
                    f"1 AOI instance tag (2 Input params: DINT, BOOL), Constant={const} -- James's "
                    f"Constant-flag question (raised for STRING) extended to AOI-instance tags, never "
                    f"tested for any UDT/AOI-typed tag in this project",
                    "aoi")
    return n


def main() -> None:
    total = 0
    for fn in [group_boolpack_nonatomic_type, group_aoi_constant_flag]:
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
