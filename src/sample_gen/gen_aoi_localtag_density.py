"""AOI LocalTag data space -- the definition cost ignores it entirely.

The 56 captured `aoistr_*` files say something that was never reconciled:
an AOI definition is charged a flat per-declared-item rate for each
LocalTag and NOTHING for what that LocalTag actually stores.

Differenced against `aoistr_predef_base_n00` (8 plain DINT LocalTags),
swapping n of those DINTs for another type, total member count held at 8:

    type                  n=1    n=8    slope   real size - DINT(4)
    TIMER                  -8    -64    8.00                      8
    COUNTER                -8    -64    8.00                      8
    MOTION_INSTRUCTION     -8    -96   12.57                      8
    STRING                -80   -672   84.57                     82

TIMER and COUNTER land exactly on "the LocalTag's own data size minus the
DINT it replaced", which is the obvious mechanism: the definition carries
its locals' storage and this model charges a flat rate instead.
MOTION_INSTRUCTION and STRING are close but not on it, and both miss by
about 4 at n=1 only -- the familiar small offset this project sees
everywhere, or a real per-type extra. Two points cannot tell those apart.

Dimensioned LocalTags are cleaner and unambiguous, from the same batch:

    aoistr_dim_local_atomic_d{008,064,512}   -24, -248, -2040   -4.00/element
    aoistr_dim_local_timer_d{008,064}         -88,  -760       -12.00/element

Exactly the element size, at every count, for both types -- an AOI
LocalTag ARRAY is charged nothing at all for its elements. By contrast
every InOut arm is flat zero (`aoistr_inout_n{00,04,16,48}` and
`aoistr_dim_inout_d{008,064,512}` all sit at the file's base offset), which
confirms the model is right to exclude InOut: it is a reference, not
storage.

This batch pins the scalar slopes with eight points each instead of two,
using the identical swap design so it differences directly against the
existing captures rather than starting a new baseline:

  A  aoilt_swap_<type>_n{01..08}   TIMER, COUNTER, MOTION_INSTRUCTION,
                                   STRING, REAL -- every count from 1 to 8,
                                   so the slope and its intercept separate.
  B  aoilt_dim_<type>_d{...}       DINT and TIMER arrays at more counts,
                                   to confirm the exact-element-size rule
                                   holds below 8 and above 512.

REAL is included as the control the original sweep lacked: it is 4 bytes,
exactly what a DINT is, so a swap must measure ZERO. If REAL comes back
non-zero the mechanism is not storage at all and the whole reading above
is wrong.
"""

from __future__ import annotations

from sample_gen.builders import MemberSpec, aoi_xml
from sample_gen.gen_aoi_structure import (
    AOI_TYPE,
    _def_only,
    _dint_locals,
    _member_name,
    _write,
)
from sample_gen.predefined_members import predef_array_member, predef_member

# Same total member count as aoistr_predef_base_n00, so this batch
# differences straight against that file and the existing n=1/n=8 points.
TOTAL_LOCALS = 8
SWAP_COUNTS = (1, 2, 3, 4, 5, 6, 7, 8)

SWAP_TYPES = (
    ("TIMER", "12 bytes; the existing 2 points already land exactly on size-minus-DINT"),
    ("COUNTER", "12 bytes; the other type that already lands exactly"),
    ("MOTION_INSTRUCTION", "12 bytes, but the 2 existing points imply 12.57/swap, not 8"),
    ("STRING", "86 bytes, but the 2 existing points imply 84.57/swap, not 82"),
    ("REAL", "4 bytes -- identical to the DINT it replaces, so this MUST measure zero"),
)

DIM_COUNTS = (2, 4, 16, 32, 128, 256, 1024)


def _swap_locals(type_name: str, n: int) -> list[MemberSpec]:
    swapped = [
        predef_member(_member_name("PdfMbr", i, 12), type_name)
        if type_name != "REAL"
        else MemberSpec(_member_name("PdfMbr", i, 12), "REAL")
        for i in range(n)
    ]
    return swapped + _dint_locals(TOTAL_LOCALS - n)


def main() -> None:
    for type_name, why in SWAP_TYPES:
        stem = type_name.split("_")[0][:6].title()
        for n in SWAP_COUNTS:
            definition, _ = aoi_xml(AOI_TYPE, local_tags=_swap_locals(type_name, n))
            _write(
                _def_only(definition, f"AoiLt{stem}{n:02d}"),
                f"aoilt_swap_{type_name.split('_')[0].lower()}_n{n:02d}",
                f"AOI definition only: {n} of the 8 DINT LocalTags in "
                f"aoistr_predef_base_n00 swapped for {type_name}, member count held "
                f"at {TOTAL_LOCALS}. Eight counts instead of the existing two, so the "
                f"per-swap slope separates from its intercept. {type_name}: {why}. "
                f"OQ-AOIDEFITEMIZE.",
            )

    for type_name in ("DINT", "TIMER"):
        for d in DIM_COUNTS:
            local = (
                MemberSpec(_member_name("ArrMbr", 0, 12), "DINT", dimension=d)
                if type_name == "DINT"
                else predef_array_member(_member_name("ArrMbr", 0, 12), "TIMER", d)
            )
            definition, _ = aoi_xml(
                AOI_TYPE, local_tags=[local] + _dint_locals(TOTAL_LOCALS - 1)
            )
            _write(
                _def_only(definition, f"AoiLtA{type_name[:3].title()}{d:04d}"),
                f"aoilt_dim_{type_name.lower()}_d{d:04d}",
                f"AOI definition only: one {type_name} LocalTag dimensioned to {d} "
                f"elements, member count held at {TOTAL_LOCALS}. The existing 3 DINT "
                f"and 2 TIMER points all sit at exactly the element size per element "
                f"({4} and {12}); these extend that below 8 and above 512 to confirm "
                f"the rule has no base term and no ceiling. OQ-AOIDEFITEMIZE.",
            )


if __name__ == "__main__":
    main()
