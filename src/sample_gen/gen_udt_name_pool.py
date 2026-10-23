"""OQ-UDTMEMBERNAME: the form of a UDT definition's member-name pool.

The wired pool, 8 * ceil(sum(len + 1) / 8) a definition, does not fit its own sweeps re-priced
live: four BOOL members read a flat -8 at lengths 2 to 32, four DINT members -16 / -8 / -16 /
-16 at lengths 2, 7, 16 and 32, and the safety rounds' short-named UDTs (members D, R, B1, B2
and D0..D9) read a pool of 0 where 16 and 32 are charged. The candidate
8 * ceil(sum(max(0, len - 2)) / 8), names of up to two characters free, fits the DINT arm and
both safety UDTs and misses the BOOL arm by 8. The earlier sweeps share residues mod 8 at the
lengths that would tell the forms apart; these do not.

Each file is the realism plant plus ONE UDT definition, `PoolUdtA`, used by no tag (a
definition is charged whether or not a tag uses it), every member name of one length (a
letter, then `x` to the length), against realism_base_f25:

  udtpool_dint_n4_len{01,02,03,04,08,12}   four DINT members
  udtpool_dint_n8_len{01,02,04,12}         eight DINT members
  udtpool_bool_n4_len{01,02,03,04,08,12}   four BOOL members: one run, one hidden backing SINT

1756-L81E v35, realism floor.

Run: python -m sample_gen.gen_udt_name_pool [--only REGEX]
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

from sample_gen.builders import MemberSpec, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "udt"
CATEGORY = "udt"
OQ = "OQ-UDTMEMBERNAME"
UDT = "PoolUdtA"
ARMS = (("dint", 4, (1, 2, 3, 4, 8, 12)), ("dint", 8, (1, 2, 4, 12)), ("bool", 4, (1, 2, 3, 4, 8, 12)))


def member_names(count: int, length: int) -> list[str]:
    return [chr(ord("A") + i) + "x" * (length - 1) for i in range(count)]


def wired_pool(names: list[str]) -> int:
    return 8 * math.ceil(sum(len(n) + 1 for n in names) / 8)


def candidate_pool(names: list[str]) -> int:
    return 8 * math.ceil(sum(max(0, len(n) - 2) for n in names) / 8)


def plan() -> list[tuple[str, list[MemberSpec]]]:
    files = []
    for kind, count, lengths in ARMS:
        for length in lengths:
            names = member_names(count, length)
            files.append((f"udtpool_{kind}_n{count}_len{length:02d}",
                          [MemberSpec(n, kind.upper()) for n in names]))
    return files


def make(sample_id: str, members: list[MemberSpec]) -> str:
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    return build_l5x(target_name=target, **with_baseline(tags_xml="", extra_datatypes_xml=udt_xml(UDT, members)))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX", help="build only the sample_ids this matches")
    args = ap.parse_args([] if argv is None else argv)
    for sample_id, members in plan():
        if args.only and not re.search(args.only, sample_id):
            continue
        names = [m.name for m in members]
        wired, candidate = wired_pool(names), candidate_pool(names)
        out = OUT_ROOT / f"{sample_id}.L5X"
        predicted = write_sample(make(sample_id, members), out)
        append_manifest_row(
            sample_id,
            f"{OQ}: the realism plant plus one UDT definition ({UDT}, used by no tag) of {len(members)} "
            f"{members[0].data_type} members named {len(names[0])} characters each; 1756-L81E v35, against "
            f"realism_base_f25. Member-name pool {wired} as wired, {candidate} under the candidate "
            f"(names of up to two characters free): the reading is the engine's less the plant's 1,794 "
            f"if the wired form holds, {wired - candidate} less again under the candidate.",
            CATEGORY, out, predicted)
        print(f"Wrote {out.name} (predicted {predicted:,}; pool {wired} wired, {candidate} candidate)")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
