"""OQ-BOOLARRAY, OQ-UDTARRAYALIGN, OQ-ARRAYPACK -- three separate open
array/packing questions, all buildable with existing confirmed builders.

  A. group_boolarray -- array-of-BOOL tag at several sizes. The confirmed
     model treats a BOOL element like any other atomic (4 bytes/element,
     no packing) but that was only directly confirmed for STANDALONE scalar
     BOOL tags (OQ-BOOLPACK) -- an ARRAY of BOOL might pack differently
     (bit-per-element instead of 4-bytes-per-element), never isolated.
  B. group_udtarrayalign -- array of an already-8-byte-tight 2-member UDT
     (2x DINT, no padding needed even under strict alignment rules) at
     1/10/100 instances. If array elements get extra per-element padding
     beyond the scalar tight size, it'll show up as a per-element cost
     above the known-flat 8 bytes.
  C. group_arraypack -- array of a deliberately NOT-4-byte-aligned UDT (3x
     SINT = 3 bytes) at 1/10/100 instances. Does each array element get
     padded up to a 4-byte boundary (would show as 4 bytes/element instead
     of 3), i.e. does the whole UDT's size round up to a 32-bit boundary
     the way OQ-ARRAYPACK asks?

Run: python -m sample_gen.gen_arraypack_boolarray
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "tags", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_boolarray() -> None:
    for n in [8, 16, 32, 100, 1000, 5000]:
        tag = tag_xml("BoolArr", "BOOL", dimensions=(n,))
        l5x = build_l5x(target_name=f"BoolArrN{n}", tags_xml=tag)
        _write(l5x, f"boolarray_n{n:05d}", f"1 tag, array of {n} BOOL elements")


def group_udtarrayalign() -> None:
    members = [MemberSpec("A", "DINT"), MemberSpec("B", "DINT")]  # 8 bytes, already tight
    datatype = udt_xml("TightPair8B", members)
    for n in [1, 10, 100]:
        tag = tag_xml("TightArr", "TightPair8B", dimensions=(n,), udt_members=members)
        l5x = build_l5x(target_name=f"TightArrN{n}", tags_xml=tag, extra_datatypes_xml=datatype)
        _write(l5x, f"udtarrayalign_tight8b_n{n:05d}",
               f"Array of {n} instances of an already-8-byte-tight UDT (2x DINT) -- per-element padding check")


def group_arraypack() -> None:
    members = [MemberSpec("A", "SINT"), MemberSpec("B", "SINT"), MemberSpec("C", "SINT")]  # 3 bytes, not 4-aligned
    datatype = udt_xml("Odd3B", members)
    for n in [1, 10, 100]:
        tag = tag_xml("OddArr", "Odd3B", dimensions=(n,), udt_members=members)
        l5x = build_l5x(target_name=f"OddArrN{n}", tags_xml=tag, extra_datatypes_xml=datatype)
        _write(l5x, f"arraypack_odd3b_n{n:05d}",
               f"Array of {n} instances of a 3-byte (3x SINT) UDT -- does each element round up to 4 bytes?")


def main() -> None:
    group_boolarray()
    group_udtarrayalign()
    group_arraypack()
    print("\nDone. 12 files.")


if __name__ == "__main__":
    main()
