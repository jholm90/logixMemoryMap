"""Close array-of-custom-string for ANY type name at ANY array size.

Every other term in a custom-string array is already KNOWN:

  element size      4 + nearest8(maxlen)   9/9 real maxlens, 49->1000
  per-element       +4/element             6/6 points, two type names
  definition cost   step fn of name length 22 real points

The one term that is not is the ONE-TIME array-level base, and the reason
is thin evidence on a real axis rather than noise. Exactly two type names
have ever been measured, and they disagree:

    "CStrArrTest"   (11 chars) -> array_base = 4
    "CStrArrCsTest" (13 chars) -> array_base = 12

Two points cannot distinguish a step from a slope. Worse, neither of the
obvious 8-char bucket shapes that explain the SCALAR definition cost can
produce that pair -- floor(11/8) == floor(13/8) and ceil(11/8) ==
ceil(13/8), so both predict the two names cost the SAME, and they do not.
Whatever this axis is, it is not the bucket the scalar side uses, and it
cannot be guessed. It has to be swept.

This batch sweeps it, and closes the two other places where the array
formula is being applied outside the range anything was measured over.

GROUP A -- csarrbase_lenNN_n010 (28 files)
    The axis itself. One 10-element array of a custom string type, maxlen
    held at 100, tag name and every other variable held identical, and
    ONLY the type-NAME length varying: every length 1..24, then 28/32/36/
    40 (40 is the Logix identifier limit). Dense at the low end because
    that is where a bucket boundary would show up, and because the two
    known points sit at 11 and 13.

GROUP B -- csarrbase_ctl_lenNN_scalar (8 files)
    The definition cost is ALSO a function of type-name length, so a raw
    Group A residual mixes two effects. These are the subtraction
    controls: one SCALAR tag of the same type at eight of the same
    lengths. array_base(L) = arr10(L) - scalar(L) - known per-element
    terms, with the definition cost cancelling in the difference.
    Deliberately a subset, not one per length: the scalar definition-cost
    formula is already KNOWN against 22 real points, so these spot-check
    that it still holds rather than re-deriving it.

GROUP C -- csarrcount_len13_nNNNN (18 files)
    Array size, at the better-measured name length. Consecutive n=1..8
    first: the AOI-array packing model looked exact for months on
    n=1/10/25 and turned out to follow 8*ceil(n/2) -- an odd-n array
    costing 4 bytes more than an even-n one -- which no sparse count
    ladder can see. Then 16/25/50/100/161/200/255/400/512/1000, which
    carries the ladder past the real corpus's largest custom-string
    array instead of stopping at 100 and extrapolating.

GROUP D -- csarrcount_len11_nNNNN (5 files)
    The falsification test. If array_base is genuinely a ONE-TIME term,
    the gap between an 11-char name and a 13-char name must be the SAME
    constant at n=1 and at n=512. If that gap grows with n, it is not a
    base at all, it is a per-element effect, and the current model is
    wrong in a way no amount of fitting the base will fix.

GROUP E -- csarrmaxlen_mNNNN_n010 (11 files)
    The nearest-8 DATA padding rule is KNOWN for a SCALAR custom string
    and has never once been checked INSIDE an array. maxlen chosen to hit
    every mod-8 remainder that mattered in the scalar derivation --
    49/50/51 (the byte-identical trio), 100 (the round-DOWN tie), 101
    (already 0-mod-8), plus 82/128/200/255/500/1000.

GROUP F -- strarrcount_nNNNN (7 files)
    Array-of-BUILT-IN-STRING at large n. This constant is currently
    stamped KNOWN off six points that stop at n=100, while real programs
    run past it -- Elmsdale declares STRING[200], MurrayBros STRING[255].
    Applying a formula 2.5x beyond its evidence and calling it certain is
    the same mistake as the one above, and this is where it is most
    likely to be costing real accuracy: in those two files the predicted
    STRING bytes are 88% and 121% of the entire under-prediction.

Held constant everywhere unless it is the variable under test: 1756-L81E,
v35 (the development baseline), maxlen 100, tag name `CsArr`, one
controller-scope tag, no logic.

The XML shape comes from the existing string_array_tag_xml builder,
deliberately unchanged. Its DATA member carries the wrong DataType, but
every file it has produced converts cleanly, and these points must be
fitted alongside the already-captured stringarray_custom100* rows --
changing the emitted shape mid-fit would confound the axis being
isolated. That is a separate cleanup, not this batch's job.

Run: python -m sample_gen.gen_custom_string_array_closure
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import custom_string_type_xml, string_array_tag_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

TAGS_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"

# Logix caps an identifier at 40 characters.
MAX_IDENTIFIER_CHARS = 40
# Held constant so the type-name axis is the only thing moving in Group A.
BASE_MAX_LEN = 100
BASE_ARRAY_COUNT = 10
CATEGORY = "string_array"


def _write(l5x: str, out_name: str, description: str) -> int:
    out_path = TAGS_OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, CATEGORY, out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 1


def type_name_of_length(length: int) -> str:
    """A valid Logix identifier of EXACTLY `length` characters.

    Must start with a letter and carry no trailing or doubled underscore,
    so this is a leading "Cs" padded with a single repeated letter. The
    padding character never changes across the sweep -- only the count of
    them does -- so nothing but length varies between two Group A files.
    """
    if length < 1 or length > MAX_IDENTIFIER_CHARS:
        raise ValueError(f"type name length {length} outside Logix's 1..{MAX_IDENTIFIER_CHARS}")
    if length == 1:
        return "C"
    return "Cs" + "a" * (length - 2)


def group_a_name_length_sweep() -> int:
    """The unknown axis, dense where a bucket boundary would show."""
    n = 0
    lengths = list(range(1, 25)) + [28, 32, 36, 40]
    for length in lengths:
        type_name = type_name_of_length(length)
        l5x = build_l5x(
            target_name=f"CsArrBaseLen{length:02d}",
            tags_xml=string_array_tag_xml(
                "CsArr", BASE_ARRAY_COUNT, max_len=BASE_MAX_LEN, data_type=type_name
            ),
            extra_datatypes_xml=custom_string_type_xml(type_name, BASE_MAX_LEN),
        )
        n += _write(
            l5x, f"csarrbase_len{length:02d}_n010",
            f"ONE {BASE_ARRAY_COUNT}-element array of a custom string type whose NAME is "
            f"{length} characters, maxlen {BASE_MAX_LEN} -- the type-name-length axis of the "
            f"array-level base, the only term in a custom-string array that is not already "
            f"KNOWN. Two prior points (11 chars -> 4, 13 chars -> 12) disagree and rule out "
            f"both 8-char bucket shapes, so this sweeps the axis densely rather than fitting "
            f"a formula through two points",
        )
    return n


def group_b_definition_cost_controls() -> int:
    """Scalar controls so the definition cost cancels out of Group A."""
    n = 0
    for length in [4, 8, 11, 13, 16, 24, 32, 40]:
        type_name = type_name_of_length(length)
        l5x = build_l5x(
            target_name=f"CsArrCtlLen{length:02d}",
            tags_xml=tag_xml("CsScalar", type_name, string_max_len=BASE_MAX_LEN),
            extra_datatypes_xml=custom_string_type_xml(type_name, BASE_MAX_LEN),
        )
        n += _write(
            l5x, f"csarrbase_ctl_len{length:02d}_scalar",
            f"ONE SCALAR tag of a custom string type whose NAME is {length} characters, "
            f"maxlen {BASE_MAX_LEN} -- subtraction control for csarrbase_len{length:02d}_n010. "
            f"The definition cost is a function of name length too, so a raw array residual "
            f"mixes two effects; differencing against this isolates the array-level base. "
            f"Also spot-checks that the already-KNOWN scalar definition-cost step still holds",
        )
    return n


def group_c_count_sweep_len13() -> int:
    """Array size at the better-measured name length, incl. consecutive n."""
    n = 0
    type_name = type_name_of_length(13)
    counts = list(range(1, 9)) + [16, 25, 50, 100, 161, 200, 255, 400, 512, 1000]
    for count in counts:
        l5x = build_l5x(
            target_name=f"CsArrCountN{count}",
            tags_xml=string_array_tag_xml(
                "CsArr", count, max_len=BASE_MAX_LEN, data_type=type_name
            ),
            extra_datatypes_xml=custom_string_type_xml(type_name, BASE_MAX_LEN),
        )
        n += _write(
            l5x, f"csarrcount_len13_n{count:04d}",
            f"ONE {count}-element array of a 13-character-named custom string type, maxlen "
            f"{BASE_MAX_LEN} -- array-size axis. n=1..8 are consecutive on purpose: the AOI "
            f"array model looked exact on a sparse n=1/10/25 ladder for months and actually "
            f"follows 8*ceil(n/2), an odd/even split no sparse ladder can see. The large "
            f"points carry the ladder past the real corpus instead of extrapolating from 100",
        )
    return n


def group_d_count_sweep_len11() -> int:
    """Falsification: is the name-length gap really n-independent?"""
    n = 0
    type_name = type_name_of_length(11)
    # Every count here MUST also exist in group C, or the pair has no twin
    # to difference against and the falsification test cannot run at all.
    for count in [1, 16, 100, 255, 512]:
        l5x = build_l5x(
            target_name=f"CsArrLen11N{count}",
            tags_xml=string_array_tag_xml(
                "CsArr", count, max_len=BASE_MAX_LEN, data_type=type_name
            ),
            extra_datatypes_xml=custom_string_type_xml(type_name, BASE_MAX_LEN),
        )
        n += _write(
            l5x, f"csarrcount_len11_n{count:04d}",
            f"ONE {count}-element array of an 11-character-named custom string type, maxlen "
            f"{BASE_MAX_LEN} -- pairs with csarrcount_len13_n{count:04d} to falsify the "
            f"one-time assumption. If the array-level base is genuinely one-time, the 11-vs-13 "
            f"gap must be the SAME constant at n=1 and n=512; if it grows with n it is a "
            f"per-element effect and fitting a base will never make it right",
        )
    return n


def group_e_maxlen_inside_array() -> int:
    """The nearest-8 padding rule, never once checked inside an array."""
    n = 0
    type_name = type_name_of_length(13)
    for max_len in [49, 50, 51, 82, 100, 101, 128, 200, 255, 500, 1000]:
        l5x = build_l5x(
            target_name=f"CsArrMaxLen{max_len}",
            tags_xml=string_array_tag_xml(
                "CsArr", BASE_ARRAY_COUNT, max_len=max_len, data_type=type_name
            ),
            extra_datatypes_xml=custom_string_type_xml(type_name, max_len),
        )
        n += _write(
            l5x, f"csarrmaxlen_m{max_len:04d}_n010",
            f"ONE {BASE_ARRAY_COUNT}-element array of a custom string type with maxlen "
            f"{max_len}, 13-character type name -- the nearest-8 DATA padding rule is KNOWN "
            f"for a SCALAR custom string and has never been checked INSIDE an array. maxlens "
            f"chosen to hit the remainders that mattered in the scalar derivation: 49/50/51 "
            f"measured byte-identical, 100 is the round-DOWN tie, 101 is already 0-mod-8",
        )
    return n


def group_f_builtin_string_array_large_n() -> int:
    """Built-in STRING array past n=100, where it is currently extrapolating."""
    n = 0
    for count in [128, 161, 200, 255, 400, 512, 1000]:
        l5x = build_l5x(
            target_name=f"StrArrCountN{count}",
            tags_xml=string_array_tag_xml("StrArr", count, max_len=82),
            extra_datatypes_xml="",
        )
        n += _write(
            l5x, f"strarrcount_n{count:04d}",
            f"ONE {count}-element array of built-in STRING -- the array-of-STRING constant is "
            f"stamped KNOWN off six points that stop at n=100, and real programs run past it "
            f"(Elmsdale declares STRING[200], MurrayBros STRING[255]). In those two files the "
            f"predicted STRING bytes are 88% and 121% of the entire under-prediction, so this "
            f"is where the extrapolation is most likely to be costing real accuracy",
        )
    return n


def main() -> None:
    total = 0
    for fn in [group_a_name_length_sweep, group_b_definition_cost_controls,
               group_c_count_sweep_len13, group_d_count_sweep_len11,
               group_e_maxlen_inside_array, group_f_builtin_string_array_large_n]:
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
