"""What the array-LocalTag sweep left open, after wiring what it settled.

Written 2026-09-11. The 27-file `aoi_arraylocal_*` sweep (built 2026-09-03)
had been captured and never reconciled. Reconciled now, it says an AOI's
array-dimensioned declared member costs its own DATA SPACE on top of the flat
per-declared-item rate, which counts it once regardless of dimension:

    DINT dim   10    50   100    250    500   1000
    deficit   -41  -201  -401  -1001  -2001  -4001     = -(4 x dim + 1)

Exactly 4 bytes per DINT element at six of seven dimensions, with SINT at
1.0/element and DINT and REAL at 4.0/element at dimension 50. That is now
wired (`compute_aoi_definition_cost`, via `compute_array_size` so the
predefined ARRAY structures keep their own base + per_element shape). It took
the 27 rows from -41..-4001 to inside +-4 on 20 of them.

FOUR THINGS THE SWEEP CANNOT ANSWER, which is what these 20 files are for.
The whole category is worth about 17 KB across the sixteen real programs --
0.036% -- so this batch is deliberately small. It exists because the rows that
do not fit are unexplained, not because the bytes are large: an unexplained
residual sitting inside a category that otherwise measures exactly is how a
wrong constant gets adopted.

1. BOOL. `BOOL[50]` measured -13 where neither the 7-byte packed size nor an
   8-byte two-word rounding fits, so BOOL arrays are deliberately left
   unpriced rather than approximated. `albool_*` walks the packing boundaries
   at 1, 8, 16, 32, 33, 50, 64 and 65 elements. Real programs do declare BOOL
   array LocalTags (2 of them, 64 elements), so this is not hypothetical.

2. The per-EXTRA-array term. Multiplicity 1/2/3 arrays of 50 DINT measured
   200/392/592, not 200/400/600 -- 196 per array after the first, an 8-byte
   discount that only shows up with more than one array in a definition.
   Two points cannot say whether that is linear, so `almult_*` adds 4, 6 and
   8 arrays. After wiring, n02 and n03 sit at +8 each, which is the whole of
   the discrepancy.

3. STRUCTURE element types. The sweep tested five atomics and nothing else.
   Real programs declare array LocalTags of MOTION_INSTRUCTION (16 arrays,
   112 elements), CAM_PROFILE (10 arrays, 100 elements), STRING (4) and TIMER
   (2) -- two thirds of the real exposure is in types the sweep never
   touched, and CAM_PROFILE crashed the engine outright the first time the
   wiring above met a real file, because it is a predefined ARRAY structure
   with no scalar element size at all. `altype_*` prices one array of each at
   dimension 10. Real shape confirmed first: a dimensioned STRUCTURE LocalTag
   carries no Radix attribute and no data body, unlike a dimensioned atomic
   one which keeps `Radix="Decimal"` (checked against the real exports'
   own `CAM_PROFILE Dimensions="10"` and `COUNTER Dimensions="2"` LocalTags).

4. The dim=25 outlier. Every other dimension lands at -1 after wiring; 25
   lands at +3, four bytes -- exactly one element -- off the line through 10
   and 50. The file's XML was checked and does declare `Dimensions="25"`, so
   it is not a generator bug. `aldim_n000{24,25,26}` re-measures it with its
   immediate neighbours under fresh sample_ids: either it reproduces and
   there is a real granularity effect near there, or the original row was a
   capture artefact and it goes away.

Run: python -m sample_gen.gen_aoi_arraylocaltag2
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"

BOOL_DIMS = (1, 8, 16, 32, 33, 50, 64, 65)
MULT_COUNTS = (4, 6, 8)
NEIGHBOUR_DIMS = (24, 25, 26)

# Real corpus array-LocalTag structure types, largest real exposure first.
# `raw_default_data=""` is what gives a dimensioned STRUCTURE LocalTag its
# real shape -- no Radix attribute and no data body. A dimensioned ATOMIC
# LocalTag keeps Radix="Decimal"; both shapes are taken verbatim from the real
# exports rather than assumed.
STRUCT_TYPES = ("MOTION_INSTRUCTION", "CAM_PROFILE", "STRING", "TIMER", "COUNTER", "CONTROL")


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi", out_path, bytes_)


def _def_only(aoi_name: str, locals_: list[MemberSpec]) -> str:
    definition, _storage = aoi_xml(aoi_name, [], [], [], locals_)
    return build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)


def group_bool_packing() -> int:
    for dim in BOOL_DIMS:
        name = f"ArrLocBoolN{dim}AOI"
        _write(
            _def_only(name, [MemberSpec("Buffer", "BOOL", dimension=dim)]),
            f"albool_n{dim:05d}_def_only",
            f"AOI with a {dim}-element BOOL array LocalTag, 0 instances. BOOL is the one element "
            f"type left unpriced after the aoi_arraylocal_* wiring: BOOL[50] measured -13, which "
            f"is neither the 7-byte packed size nor an 8-byte two-word rounding, so pricing it at "
            f"a guessed rate would bury a known discrepancy in a category that otherwise measures "
            f"exactly. This sweep walks the packing boundaries (1, 8, 16, 32, 33, 50, 64, 65) so "
            f"the rounding unit is read directly. OQ-AOIARRAYLOCALTAG.",
        )
    return len(BOOL_DIMS)


def group_multiplicity() -> int:
    for count in MULT_COUNTS:
        name = f"ArrLocMult{count}AOI"
        _write(
            _def_only(name, [MemberSpec(f"Buffer{i}", "DINT", dimension=50)
                             for i in range(count)]),
            f"almult_n{count:02d}_def_only",
            f"AOI with {count} independent 50-element DINT array LocalTags, 0 instances. The "
            f"captured 1/2/3 points measured 200/392/592, not 200/400/600 -- 196 bytes per array "
            f"after the first, an 8-byte discount that only appears once a definition holds more "
            f"than one array. Two points cannot say whether that is linear or a one-off; 4, 6 and "
            f"8 arrays settle it. OQ-AOIARRAYLOCALTAG.",
        )
    return len(MULT_COUNTS)


def group_struct_types() -> int:
    for type_name in STRUCT_TYPES:
        name = f"ArrLoc{type_name.title().replace('_', '')[:12]}AOI"
        _write(
            _def_only(name, [MemberSpec("Buffer", type_name, dimension=10,
                                        raw_default_data="")]),
            f"altype_{type_name.lower()}_n00010_def_only",
            f"AOI with a 10-element {type_name} array LocalTag, 0 instances. The original sweep "
            f"tested five atomics and nothing else, while two thirds of the real array-LocalTag "
            f"exposure is in structure types the corpus has never priced -- MOTION_INSTRUCTION "
            f"(16 arrays / 112 elements across the real programs), CAM_PROFILE (10 / 100), STRING "
            f"(4) and TIMER (2). CAM_PROFILE is the pointed case: it is a predefined ARRAY "
            f"structure with no scalar element size, and it raised UnknownDataTypeError the first "
            f"time the newly wired term met a real file. Dimensioned-structure LocalTag shape "
            f"(no Radix, no data body) taken verbatim from the real exports. "
            f"OQ-AOIARRAYLOCALTAG.",
        )
    return len(STRUCT_TYPES)


def group_dim_neighbours() -> int:
    for dim in NEIGHBOUR_DIMS:
        name = f"ArrLocNbrN{dim}AOI"
        _write(
            _def_only(name, [MemberSpec("Buffer", "DINT", dimension=dim)]),
            f"aldim_n{dim:05d}_def_only",
            f"AOI with a {dim}-element DINT array LocalTag, 0 instances. Re-measures the one "
            f"dimension that does not fit: after wiring, every dimension in the captured sweep "
            f"lands at -1 except 25, which lands at +3 -- four bytes, exactly one element, off "
            f"the line through 10 and 50. The file's XML was checked and does declare "
            f"Dimensions=\\\"25\\\", so it is not a generator bug. Its immediate neighbours 24 and 26 "
            f"say whether there is a real granularity effect there or whether the original row "
            f"was a capture artefact. OQ-AOIARRAYLOCALTAG.",
        )
    return len(NEIGHBOUR_DIMS)


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    b = group_bool_packing()
    m = group_multiplicity()
    s = group_struct_types()
    d = group_dim_neighbours()
    print(f"BOOL packing boundaries:      {b}")
    print(f"Array multiplicity 4/6/8:     {m}")
    print(f"Structure element types:      {s}")
    print(f"dim=25 and its neighbours:    {d}")
    print(f"Total: {b + m + s + d}")


if __name__ == "__main__":
    main()
