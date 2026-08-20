"""Comment/description-length sweep (James, 2026-08-20: "comment length in
the tag vs comment length in the udt element vs udt description vs udt tag
description"). Four distinct places a human-readable comment can live in
real L5X, tested independently with everything else held constant:

  G. Tag-level Description on a plain atomic (DINT) tag.
  H. Member-level Description on one DataType Member ("udt element").
  I. DataType-level Description (the UDT's own top-level comment).
  J. Tag-level Description on a tag whose type is a UDT ("udt tag
     description" -- same XML field as G, but on a UDT-typed instance
     specifically, in case that differs from the atomic-tag case).

Every group uses lengths [0, 10, 25, 50, 100, 200] and, for the UDT
groups, a fixed single-DINT-member UDT with 0 or 1 instances so only the
one comment field under test varies.

Run: python -m sample_gen.gen_comment_sweep
"""

from __future__ import annotations

from sample_gen.cli import main as cli_main

LENGTHS = [0, 10, 25, 50, 100, 200]


def _run(argv: list[str]) -> None:
    rc = cli_main(argv)
    if rc != 0:
        raise RuntimeError(f"sample_gen.cli {argv} exited {rc}")


def group_g_tag_comment() -> int:
    n = 0
    for length in LENGTHS:
        out = f"tagcomment_len{length:03d}"
        _run(["tags", "--type", "DINT", "--count", "1", "--desc-len", str(length), "--out", out])
        n += 1
    return n


def group_h_udt_member_comment() -> int:
    n = 0
    for length in LENGTHS:
        out = f"udtmembercomment_len{length:03d}"
        _run(["udt", "--name", "CommentH", "--member", "M0:DINT",
              "--member-desc-len", str(length), "--instances", "0", "--out", out])
        n += 1
    return n


def group_i_udt_type_comment() -> int:
    n = 0
    for length in LENGTHS:
        out = f"udttypecomment_len{length:03d}"
        _run(["udt", "--name", "CommentI", "--member", "M0:DINT",
              "--type-desc-len", str(length), "--instances", "0", "--out", out])
        n += 1
    return n


def group_j_udt_tag_comment() -> int:
    n = 0
    for length in LENGTHS:
        out = f"udttagcomment_len{length:03d}"
        _run(["udt", "--name", "CommentJ", "--member", "M0:DINT",
              "--tag-desc-len", str(length), "--instances", "1", "--out", out])
        n += 1
    return n


def main() -> None:
    total = 0
    for group_fn in [group_g_tag_comment, group_h_udt_member_comment,
                      group_i_udt_type_comment, group_j_udt_tag_comment]:
        count = group_fn()
        print(f"{group_fn.__name__}: {count} file(s)")
        total += count
    print(f"\nTotal: {total} sample(s) generated/updated.")


if __name__ == "__main__":
    main()
