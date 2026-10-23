"""OQ-STRSHAPE: which string member a UDT array pays 4 more for.

`strx_n00` reads 4 an element above the engine on arrays of a UDT holding two STRINGs, a
40-character custom string, a DINT and a REAL (224 priced, 228 real). Either each STRING
member is 88 rather than 86 (two of them, +2 each, as a STRING array's element already is),
or the custom string is 48 rather than 44. The real programs say which matters: the three
safety-controller programs the standard figure reads 2.0 to 2.45% low carry 2,744 to
12,677 STRING members inside their UDT tags. Each file below is one array of 400 of one
UDT on the realism plant, priced against the engine (with the plant's own -1,794):

  strm_s2_400   {S1, S2 STRING}           engine 172 an element; 176 if a STRING member is 88
  strm_c2_400   {C1, C2 StrM40}           engine 88; 96 if the custom string is 48
  strm_sc_400   {S STRING, C StrM40}      engine 132 (130 rounded); 136 only if the custom string is 48
  strm_sd_400   {S STRING, D DINT}        engine 92 (90 rounded) under either: the null check

The real programs hold most of those STRINGs one level down: a scalar tag of a UDT whose member
is an array of the STRING-holding UDT (35 to 49% of the three programs' predicted bytes). Each
`strn_*` file carries its `strm_*` twin's 400 elements as that member, `Items`, of one scalar tag
of `StrnOut<key>`, so the pair says whether what the twin finds holds in the nested shape:

  strn_s2_400 / strn_c2_400 / strn_sd_400   against strm_s2_400 / strm_c2_400 / strm_sd_400

1756-L81E v35, realism floor.

Run: python -m sample_gen.gen_string_members [--only REGEX]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from sample_gen.builders import MemberSpec, custom_string_type_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "strx"
CATEGORY = "string_shape"
OQ = "OQ-STRSHAPE"
N = 400
CUSTOM = "StrM40"

SHAPES = {
    "s2": ([MemberSpec("S1", "STRING"), MemberSpec("S2", "STRING")], "two STRINGs: 172 priced, 176 if a STRING member is 88"),
    "c2": ([MemberSpec("C1", CUSTOM), MemberSpec("C2", CUSTOM)], "two 40-character custom strings: 88 priced, 96 if one is 48"),
    "sc": ([MemberSpec("S", "STRING"), MemberSpec("C", CUSTOM)], "a STRING and a custom string: 132 priced, 136 only if the "
                                                                    "custom string is 48"),
    "sd": ([MemberSpec("S", "STRING"), MemberSpec("D", "DINT")], "a STRING and a DINT: 92 priced either way, the null check"),
}


def make(key: str) -> str:
    members, _ = SHAPES[key]
    udt = f"StrM{key.capitalize()}"
    target = f"StrmMembers{key.capitalize()}"
    return build_l5x(target_name=target, **with_baseline(
        tags_xml=tag_xml(f"StrmArr{key.capitalize()}", udt, (N,), udt_members=members),
        extra_datatypes_xml=custom_string_type_xml(CUSTOM, 40) + "\n" + udt_xml(udt, members)))


def make_nested(key: str) -> str:
    members, _ = SHAPES[key]
    inner = f"StrM{key.capitalize()}"
    outer = f"StrnOut{key.capitalize()}"
    items = [MemberSpec("Items", inner, N, nested_members=tuple(members))]
    return build_l5x(target_name=f"StrnMembers{key.capitalize()}", **with_baseline(
        tags_xml=tag_xml(f"StrnTag{key.capitalize()}", outer, udt_members=items),
        extra_datatypes_xml="\n".join((custom_string_type_xml(CUSTOM, 40), udt_xml(inner, members),
                                        udt_xml(outer, items)))))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX", help="build only the sample_ids this matches")
    args = ap.parse_args([] if argv is None else argv)
    for key, (_members, what) in SHAPES.items():
        sample_id = f"strm_{key}_{N}"
        if args.only and not re.search(args.only, sample_id):
            continue
        out = OUT_ROOT / f"{sample_id}.L5X"
        predicted = write_sample(make(key), out)
        append_manifest_row(sample_id, f"{OQ}: one array of {N} of a UDT holding {what}; realism floor, 1756-L81E v35, "
                                       f"against the engine with the plant's own -1,794.", CATEGORY, out, predicted)
        print(f"Wrote {out.name} (predicted {predicted:,})")
    for key, (_members, what) in SHAPES.items():
        sample_id = f"strn_{key}_{N}"
        if args.only and not re.search(args.only, sample_id):
            continue
        out = OUT_ROOT / f"{sample_id}.L5X"
        predicted = write_sample(make_nested(key), out)
        append_manifest_row(sample_id, f"{OQ}: strm_{key}_{N}'s {N} elements of a UDT holding {what}, as one array "
                                       f"member of a scalar UDT tag (the nested shape real programs hold most "
                                       f"STRINGs in); realism floor, 1756-L81E v35, against strm_{key}_{N} and "
                                       f"the engine with the plant's own -1,794.", CATEGORY, out, predicted)
        print(f"Wrote {out.name} (predicted {predicted:,})")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
