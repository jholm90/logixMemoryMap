"""The -23 on 263 captured files, and which tag it belongs to.

Written 2026-09-12 from a residual census over every clean generated capture.
Of 2,563 such files, 844 (32.9%) predict EXACTLY right and **263 (10.3%) sit at
exactly -23** -- by far the largest non-zero bucket, and 23 is an odd number,
which a memory allocation essentially never is.

Narrowing it down, in order:

  - 258 of the 263 are files that contain REAL ladder rungs, so it looked like a
    logic term. It is not: the -23 is identical at 1 rung and at 27,267 rungs
    (`randommix_00_n00609rungs` and `instr_*_n00010` alike), so nothing about it
    scales with logic.
  - It is not "any file with logic" either. Among real-rung files 25.6% are at
    -23 and 20.2% are at exactly 0, so something separates the two groups.
  - What separates them is the TAG POOL, not the logic. Every -23 family
    (`instr_*` 234 files, `shellscale_*`, `randommix_*`, `lbljmp_*`) shares one
    pool: 4 DINT, 6 REAL, 3 BOOL, a DINT[20], a CONTROL, a 2-element STRING
    array and two STRING(82) tags. Every real-rung family at exactly 0
    (`cmpcpt_*`, `cptmix_*`) uses a pool of only DINTs, REALs and BOOLs.

So the 23 is a TAG-SIZING error, not a logic one. That matters twice over: the
instruction weights derived from those files are unaffected, because a constant
pool cancels in every difference between counts -- but every absolute prediction
that includes this pool is 23 bytes low.

WHAT IS ALREADY RULED OUT. The string shapes are exact: all 8 `customstring_*`
files and all `stringarray_*` files (built-in and custom, n=1 to 100) predict to
the byte. So the 23 is not in the STRING or string-array tags, which leaves the
CONTROL tag as the prime suspect -- the one pool member with no isolation probe
anywhere in the corpus -- with the DINT[20] array next.

THE BATCH, 9 files, no logic in any of them except where stated:

    pool23_dint04     4 DINT, alone
    pool23_real06     6 REAL, alone
    pool23_bool03     3 BOOL, alone
    pool23_arr20      one DINT[20], alone
    pool23_control    one CONTROL tag, alone     <- prime suspect
    pool23_strarr02   one 2-element STRING array, alone
    pool23_str82x2    two STRING(82), alone
    pool23_full       the whole pool, no logic   <- must read -23 if the pool
                                                   is the cause
    pool23_full_rungs the whole pool + 10 XIC/OTE rungs, which pins the 23 as
                      pool-borne rather than logic-borne: it must read the SAME
                      -23 as pool23_full

Differencing the seven single-shape files against `pool23_full` says which
member carries it, and `pool23_full` against `pool23_full_rungs` says the logic
has nothing to do with it. Every file predicts a value the engine computes from
constants it already claims to know, so any deviation is a measurement of a
wrong constant rather than of an unmodelled quantity.

Run: python -m sample_gen.gen_pool_residual
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import (
    control_tag_xml,
    rungs_xml,
    string_array_tag_xml,
    tag_xml,
)
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"

# Each piece of the pool the -23 families share, verbatim from
# gen_unweighted_instructions._POOL so the difference against those 263 captured
# files is exact.
_PIECES = {
    "dint04": ("\n".join(tag_xml(f"D{i}", "DINT") for i in range(4)),
               "4 DINT tags"),
    "real06": ("\n".join(tag_xml(f"R{i}", "REAL") for i in range(6)),
               "6 REAL tags"),
    "bool03": ("\n".join(tag_xml(f"B{i}", "BOOL") for i in range(3)),
               "3 BOOL tags"),
    "arr20": (tag_xml("ARR0", "DINT", dimensions=(20,)),
              "one 20-element DINT array"),
    "control": (control_tag_xml("CTRL0", length=12, position=0),
                "one CONTROL tag -- the prime suspect, and the only member of "
                "this pool with no isolation probe anywhere in the corpus"),
    "strarr02": (string_array_tag_xml("STRPOOL", 2),
                 "one 2-element STRING array"),
    "str82x2": ("\n".join(tag_xml(f"STR{i}", "STRING", string_max_len=82)
                          for i in range(2)),
                "two STRING(82) tags"),
}


def _full_pool() -> str:
    return "\n".join(xml for xml, _why in _PIECES.values())


_WHY = (
    "Of 2,563 clean generated captures, 263 sit at EXACTLY -23 -- the largest non-zero residual "
    "bucket, on an odd number, which a memory allocation essentially never is. It is identical at "
    "1 rung and at 27,267, so it does not scale with logic; and among real-rung files 25.6% are at "
    "-23 while 20.2% are at 0, so logic is not the discriminator either. What separates the two "
    "groups is the TAG POOL: every -23 family (instr_* 234 files, shellscale_*, randommix_*, "
    "lbljmp_*) shares this pool, and every real-rung family at exactly 0 (cmpcpt_*, cptmix_*) uses "
    "only DINTs, REALs and BOOLs. The string shapes are already ruled out -- all 8 customstring_* "
    "and every stringarray_* file predicts to the byte -- which leaves CONTROL and the DINT array. "
    "The instruction weights fitted from those 263 files are unaffected, since a constant pool "
    "cancels in every count difference, but every absolute prediction carrying this pool is 23 low."
)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    for key, (tags_xml, what) in _PIECES.items():
        name = f"pool23_{key}"
        l5x = build_l5x(target_name=f"Pool23{key.title()}"[:24], tags_xml=tags_xml)
        out = OUT / f"{name}.L5X"
        bytes_ = write_sample(l5x, out)
        append_manifest_row(
            name,
            f"{what}, alone, with no logic. Differences against pool23_full to say which member of "
            f"the shared pool carries the 23. {_WHY} OQ-SHELLCONST.",
            "tags", out, bytes_,
        )
        written += 1

    full = _full_pool()
    l5x = build_l5x(target_name="Pool23Full", tags_xml=full)
    out = OUT / "pool23_full.L5X"
    bytes_ = write_sample(l5x, out)
    append_manifest_row(
        "pool23_full",
        f"The ENTIRE shared pool -- 4 DINT, 6 REAL, 3 BOOL, a DINT[20], a CONTROL, a 2-element "
        f"STRING array and two STRING(82) -- with NO logic at all. Must read -23 if the pool is the "
        f"cause; if it reads 0 then the 23 is not in the tags after all and the seven single-shape "
        f"files say so together. {_WHY} OQ-SHELLCONST.",
        "tags", out, bytes_,
    )
    written += 1

    l5x = build_l5x(target_name="Pool23FullRungs", tags_xml=full,
                    extra_rungs_xml=rungs_xml(10, lambda _i: "XIC(B0)OTE(B1);"))
    out = OUT / "pool23_full_rungs.L5X"
    bytes_ = write_sample(l5x, out)
    append_manifest_row(
        "pool23_full_rungs",
        f"The entire shared pool PLUS 10 XIC/OTE rungs -- the same shape shellscale_routines_n001 "
        f"has. Pins the 23 as pool-borne rather than logic-borne: it must read the SAME residual as "
        f"pool23_full, and if it does not then the two interact and neither reading alone is "
        f"trustworthy. {_WHY} OQ-SHELLCONST.",
        "tags", out, bytes_,
    )
    written += 1
    print(f"Total: {written}")


if __name__ == "__main__":
    main()
