"""STRING closing batch, round 2 (James, 2026-08-26: "I want to close
strings. Make up the tests needed so I can l5x them now").

Array-of-STRING is now RESOLVED and wired (OQ-STRINGARRAYPAD, see
memory_model.yaml string_array) -- real data landed and fit cleanly:
builtin 6/6 points exact, custom-string 6/6 points exact on the per-
element rate. The one remaining loose end from that same analysis is the
custom-string type-NAME-length effect (already flagged in the `string:`
block as real but not characterized): 1-char name = -8, 9-char = 0,
32-char = +24, no clean formula fits 3 sparse points. This batch closes
that, plus two adjacent questions the same analysis surfaced:

  A. group_dense_namelen -- a genuinely dense standalone custom-string
     type-name-length sweep (maxlen=100 fixed, def_only shape only --
     the existing 3-point data already showed def_only and 1_instance
     track identically, so testing def_only alone is sufficient, not a
     shortcut). Lengths 1-16 (every integer, to find exactly where the
     -8->0 transition sits) plus 20/24/28/32/36/40 (to find the 0->+24
     transition and give headroom to Rockwell's real ~40-char type-name
     ceiling). 22 files total.
  B. group_udtmember_namelen_crosscheck -- the SAME 3 type names already
     tested standalone (1/9/32 chars) used instead as a UDT member, to
     answer a question the existing data can't: does nesting a custom
     string inside a UDT add its own cost on top of the name-length
     effect, or is the udtstring_custom100_n01/n10 real +8 residual
     already fully explained by name length alone (the type name used
     there, "CStrUdtMember100", is 16 chars -- if this cross-check's
     3 points fall on the SAME curve the standalone sweep in group A
     traces out, nesting adds nothing extra; if not, there's a real
     separate nesting term). 3 files.
  C. group_udtmember_maxlen_sweep -- holds a fixed SHORT type name (to
     stay out of the name-length effect's way) and varies maxlen instead
     (50/250/500/1000, matching the maxlens already confirmed clean for
     the scalar case) as a UDT member -- checks whether the UDT-nesting
     residual (if group B confirms one exists) depends on maxlen too, or
     is a flat per-nesting tax regardless of the string's own size.
     4 files.
  D. group_builtin_udtmember_scaling -- the builtin-STRING-as-UDT-member
     finding (udtstring_builtin_n01=-2, n10=-20, real slope=-2/instance,
     matching the already-confirmed scalar -2/tag correction exactly --
     strongly suggesting that correction just needs to apply once per
     builtin-STRING-member-containing tag instance, not only to
     standalone STRING-typed tags) only has 2 count points and no test of
     whether it's per-INSTANCE or per-MEMBER when a UDT has more than one
     STRING member. n=3/n=20 firm up the count-linearity; 2-member and
     3-member UDTs (at n=1 instance) test whether each additional STRING
     member in the SAME UDT gets its own -2. 4 files.

Run: python -m sample_gen.gen_string_close_out
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, custom_string_type_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

TAGS_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"
UDT_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "udt"


def _write(out_dir: Path, l5x: str, out_name: str, description: str, category: str) -> int:
    out_path = out_dir / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, category, out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 1


# ---------------------------------------------------------------------------
# A. Dense standalone type-name-length sweep, maxlen=100 fixed, def_only.
# ---------------------------------------------------------------------------

def _name_of_length(n: int) -> str:
    # Deterministic, readable names: "A", "AB", ... padded with digits
    # once the alphabet-only prefix isn't enough. Avoids the double-
    # underscore trap already fixed elsewhere in this project (no "_" at
    # all here, so it can't recur).
    base = "CStrLen"
    if n <= len(base):
        return base[:n]
    return (base + "X" * (n - len(base)))[:n]


def group_dense_namelen() -> int:
    n_files = 0
    maxlen = 100
    lengths = list(range(1, 17)) + [20, 24, 28, 32, 36, 40]
    for length in lengths:
        type_name = _name_of_length(length)
        assert len(type_name) == length
        datatype = custom_string_type_xml(type_name, maxlen)
        l5x = build_l5x(target_name=f"StrDenseLen{length:02d}Def", tags_xml="", extra_datatypes_xml=datatype)
        n_files += _write(
            TAGS_OUT, l5x, f"stringclose_densenamelen_n{length:02d}_def_only",
            f"Custom string type maxlen=100, type name '{type_name}' ({length} chars), 0 instances -- "
            f"dense type-name-length sweep point (real data shows -8/0/+24 at 1/9/32 chars, no clean "
            f"formula fits those 3 sparse points; this fills in every length 1-16 plus 20/24/28/32/36/40)",
            "string_tagoverhead",
        )
    return n_files


# ---------------------------------------------------------------------------
# B. UDT-member cross-check at the 3 ALREADY-tested standalone name lengths.
# ---------------------------------------------------------------------------

def group_udtmember_namelen_crosscheck() -> int:
    n_files = 0
    maxlen = 100
    names = {"short": "A", "medium": "CStr100Md", "long": "CStrTypeNameVeryLongIsolation100"}
    for label, type_name in names.items():
        datatype = custom_string_type_xml(type_name, maxlen)
        member = MemberSpec("S0", type_name)
        udt = udt_xml(f"UdtNameCheck{label.title()}", [member])
        tag = tag_xml("UNC0", f"UdtNameCheck{label.title()}", udt_members=[member])
        l5x = build_l5x(
            target_name=f"StrUdtNameCheck{label.title()}", tags_xml=tag,
            extra_datatypes_xml=datatype + "\n" + udt,
        )
        n_files += _write(
            UDT_OUT, l5x, f"stringclose_udtmember_namelen_{label}",
            f"UDT with 1 custom string member, type name '{type_name}' ({len(type_name)} chars, maxlen=100), "
            f"1 instance -- SAME type name already tested standalone (stringoverhead_typenamelen_{label}_*) "
            f"as a UDT member instead, isolates whether nesting adds its own cost on top of the "
            f"name-length effect or whether the effect is name-length-only",
            "udt",
        )
    return n_files


# ---------------------------------------------------------------------------
# C. UDT-member maxlen sweep, fixed SHORT type name.
# ---------------------------------------------------------------------------

def group_udtmember_maxlen_sweep() -> int:
    n_files = 0
    type_name = "CStrUM"  # 6 chars -- already-confirmed flat-0 zone for the standalone case
    for maxlen in [50, 250, 500, 1000]:
        datatype = custom_string_type_xml(type_name, maxlen)
        member = MemberSpec("S0", type_name)
        udt = udt_xml(f"UdtMaxlen{maxlen}", [member])
        tag = tag_xml("UM0", f"UdtMaxlen{maxlen}", udt_members=[member])
        l5x = build_l5x(
            target_name=f"StrUdtMaxlen{maxlen}", tags_xml=tag,
            extra_datatypes_xml=datatype + "\n" + udt,
        )
        n_files += _write(
            UDT_OUT, l5x, f"stringclose_udtmember_maxlen_{maxlen:04d}",
            f"UDT with 1 custom string member, maxlen={maxlen}, type name '{type_name}' (6 chars, "
            f"already-confirmed flat-0 zone), 1 instance -- checks whether the UDT-nesting residual "
            f"(if group B confirms one) depends on maxlen or is a flat per-nesting tax",
            "udt",
        )
    return n_files


# ---------------------------------------------------------------------------
# D. Builtin-STRING-as-UDT-member: more counts + multi-member.
# ---------------------------------------------------------------------------

def group_builtin_udtmember_scaling() -> int:
    n_files = 0
    single_member = [MemberSpec("S0", "STRING")]
    for instances in [3, 20]:
        udt = udt_xml("UdtBuiltinStrScale", single_member)
        tags = "\n".join(
            tag_xml(f"UBSS{i}", "UdtBuiltinStrScale", udt_members=single_member) for i in range(instances)
        )
        l5x = build_l5x(target_name=f"StrUdtBuiltinScaleN{instances}", tags_xml=tags, extra_datatypes_xml=udt)
        n_files += _write(
            UDT_OUT, l5x, f"stringclose_udtmember_builtin_n{instances:02d}",
            f"UDT with 1 built-in STRING member, {instances} instance(s) -- extends the existing n=1/n=10 "
            f"count sweep (real slope -2/instance, matches the confirmed scalar tag_overhead correction "
            f"exactly) to firm up linearity beyond 2 points",
            "udt",
        )

    for member_count in [2, 3]:
        members = [MemberSpec(f"S{i}", "STRING") for i in range(member_count)]
        udt = udt_xml(f"UdtBuiltinStr{member_count}Members", members)
        tag = tag_xml("UBSM0", f"UdtBuiltinStr{member_count}Members", udt_members=members)
        l5x = build_l5x(target_name=f"StrUdtBuiltin{member_count}MembersN1", tags_xml=tag, extra_datatypes_xml=udt)
        n_files += _write(
            UDT_OUT, l5x, f"stringclose_udtmember_builtin_{member_count}members_n01",
            f"UDT with {member_count} built-in STRING members, 1 instance -- tests whether the -2 "
            f"correction applies once per STRING MEMBER (total -{2*member_count}) or once per TAG "
            f"INSTANCE regardless of member count (still -2) -- the n=1/n=10 single-member sweep can't "
            f"distinguish these",
            "udt",
        )
    return n_files


# ---------------------------------------------------------------------------
# E. Builtin-STRING-as-UDT-member disentangle, round 2 (2026-08-26).
#
# Group D's own results came back with a 2-D surface, not a 1-D one:
#   correction(m, n=1) = 2m - 4  (m=1:-2, m=2:0, m=3:+2)
#   correction(m=1, n) = -2n    (n=1/3/10/20 all fit)
# Both slices only ever vary ONE axis while holding the other at 1 -- a
# bilinear model (correction = a*m*n + b*m + c*n + d) can't be told apart
# from an additive one (correction = f(m) + g(n)) without a point where
# BOTH m>1 AND n>1. These 2 files are exactly that: same 2-/3-member UDTs
# as group D, but now at 3 instances instead of 1, holding member count
# fixed at group D's values and moving n off of 1 for the first time.
# ---------------------------------------------------------------------------

def group_builtin_udtmember_disentangle() -> int:
    n_files = 0
    for member_count in [2, 3]:
        members = [MemberSpec(f"S{i}", "STRING") for i in range(member_count)]
        udt = udt_xml(f"UdtBuiltinStr{member_count}MembersN3", members)
        instances = 3
        tags = "\n".join(
            tag_xml(f"UBSM3_{i}", f"UdtBuiltinStr{member_count}MembersN3", udt_members=members)
            for i in range(instances)
        )
        l5x = build_l5x(
            target_name=f"StrUdtBuiltin{member_count}MembersN3", tags_xml=tags, extra_datatypes_xml=udt
        )
        n_files += _write(
            UDT_OUT, l5x, f"stringclose_udtmember_builtin_{member_count}members_n03",
            f"UDT with {member_count} built-in STRING members, {instances} instances -- disentangles "
            f"group D's two 1-D slices (correction(m,n=1)=2m-4, correction(m=1,n)=-2n): the first real "
            f"point with BOTH member count > 1 AND instance count > 1, needed to tell a bilinear "
            f"correction surface (a*m*n+b*m+c*n+d) apart from a simple additive one (f(m)+g(n))",
            "udt",
        )
    return n_files


if __name__ == "__main__":
    total = 0
    total += group_dense_namelen()
    total += group_udtmember_namelen_crosscheck()
    total += group_udtmember_maxlen_sweep()
    total += group_builtin_udtmember_scaling()
    total += group_builtin_udtmember_disentangle()
    print(f"\nTotal files: {total}")
