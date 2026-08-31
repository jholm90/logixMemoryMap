"""James, 2026-08-31: "If you were to take that udt and stand alone
generate it in a new program I wonder if you would get a different
result." Direct empirical answer to that question.

The UDT and array size below are copied VERBATIM (member names, types,
declared order, array dimension) from the real, confidential AccuTally
project's `srt_SmallBoard` type and its `SmBoardQ` tag (samples/local/
_confidential_tmp/, not committed, never named beyond this generic
description in a public file) -- the single largest contributor to that
file's predicted total (1,040,092 of 5,167,778 bytes, 20.1%). Deliberately
the SIMPLEST of AccuTally's large real structures to isolate first: 22
flat atomic-scalar members (5 DINT + 13 INT + 4 SINT, in that declared
order), no BOOL, no nesting, no STRING -- if this doesn't reproduce
identically, alignment/padding math itself is wrong even at the simplest
possible shape; if it DOES reproduce identically, the real gap lives
elsewhere (see gen_jsr_target_content_scale.py for the leading
alternative candidate, or a genuine interaction effect only visible in
the full real file, per OQ-COMPOSITESCALE).

Single file: one controller tag, array of 20,000 real-shape instances,
nothing else in the project -- isolates this one structure completely
from every other real AccuTally content that could be confounding it.

Run: python -m sample_gen.gen_udt_realworld_isolation
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "udt"

# Verbatim member list/order from the real srt_SmallBoard UDT.
_MEMBERS = [
    MemberSpec("RTCDint", "DINT"), MemberSpec("Sort", "DINT"), MemberSpec("PackID", "DINT"),
    MemberSpec("ProductID", "DINT"), MemberSpec("Reciever", "DINT"),
    MemberSpec("BoardID", "INT"), MemberSpec("LengthIn", "INT"), MemberSpec("LengthOut", "INT"),
    MemberSpec("NomLengthIn", "INT"), MemberSpec("NomLengthOut", "INT"),
    MemberSpec("ThicknessOut", "INT"), MemberSpec("NomThicknessOut", "INT"),
    MemberSpec("WidthOut", "INT"), MemberSpec("NomWidthOut", "INT"),
    MemberSpec("VolumeIn", "INT"), MemberSpec("VolumeOut", "INT"),
    MemberSpec("Moisture", "INT"), MemberSpec("MSG", "INT"),
    MemberSpec("Grader", "SINT"), MemberSpec("Bin", "SINT"),
    MemberSpec("Color", "SINT"), MemberSpec("Grade", "SINT"),
]

ARRAY_LEN = 20000


def main() -> None:
    udt_name = "RealWorldFlatBoard22Member"
    definition = udt_xml(udt_name, _MEMBERS)
    tag = tag_xml("RealWorldFlatBoardArray", udt_name, dimensions=(ARRAY_LEN,), udt_members=_MEMBERS)
    l5x = build_l5x(
        target_name="UdtRealWorldIsolation", tags_xml=tag, extra_datatypes_xml=definition,
    )
    out_path = OUT_ROOT / "udt_realworld_flatboard_isolation.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(
        "udt_realworld_flatboard_isolation",
        f"A real 22-member flat-atomic-scalar UDT (5 DINT + 13 INT + 4 SINT, verbatim member "
        f"names/types/order from a real confidential project's largest single tag, not "
        f"committed/named), array of {ARRAY_LEN} instances, isolated in an otherwise-empty "
        f"project -- James, 2026-08-31: direct test of whether this exact real structure "
        f"reproduces the same predicted total in isolation as it does inside the full real "
        f"file, or whether something about real project context/scale changes it.",
        "udt", out_path, bytes_,
    )
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


if __name__ == "__main__":
    main()
