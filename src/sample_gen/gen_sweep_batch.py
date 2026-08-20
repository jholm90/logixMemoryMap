"""Large sweep batch (James, 2026-08-20: "why are you only doing batches of
2? i want the next sample to be >50 ... you need to get a large sample size
of data to ensure that tag structures are 100% confirmed"). One coherent
drop covering every remaining gap in OQ-TAGOVERHEAD's model instead of one
isolating pair at a time:

  A. Tag-name length, finer granularity (4..40 in steps of ~3) -- the
     earlier 2-point fit (4 vs 40 chars) had no coverage in between.
  B. All six atomic types, fixed name length/count -- confirms the flat
     per-tag overhead doesn't depend on the underlying data type.
  C. Tag count sweep (1..1000) -- confirms the per-tag rate is truly flat/
     linear, not bucketed at some count.
  D. DINT array element-count sweep (1..5000; 10000 already covered by
     dint_10k_array) -- confirms the flat per-array-tag overhead and the
     4 bytes/element rate hold across array sizes.
  E. UDT member-count sweep, all-DINT members, definition only (0
     instances) -- does DataType-definition cost scale with member count?
  F. UDT member-type sweep, fixed 4 members, definition only -- does
     DataType-definition cost depend on member type, not just count?

Run: python -m sample_gen.gen_sweep_batch
"""

from __future__ import annotations

from sample_gen.cli import main as cli_main

ATOMIC_TYPES = ["SINT", "INT", "DINT", "LINT", "REAL", "BOOL"]


def _run(argv: list[str]) -> None:
    rc = cli_main(argv)
    if rc != 0:
        raise RuntimeError(f"sample_gen.cli {argv} exited {rc}")


def group_a_name_length() -> int:
    n = 0
    for length in [4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40]:
        out = f"tagname_len{length:02d}_50dint"
        _run(["tags", "--type", "DINT", "--count", "50", "--name-prefix", "T",
              "--name-len", str(length), "--out", out])
        n += 1
    return n


def group_b_atomic_types() -> int:
    n = 0
    for t in ATOMIC_TYPES:
        out = f"type_{t.lower()}_50tag"
        _run(["tags", "--type", t, "--count", "50", "--name-prefix", "T",
              "--name-len", "8", "--out", out])
        n += 1
    return n


def group_c_tag_count() -> int:
    n = 0
    for count in [1, 2, 5, 10, 25, 50, 100, 250, 500, 1000]:
        out = f"count_{count:04d}_dint"
        _run(["tags", "--type", "DINT", "--count", str(count), "--name-prefix", "T",
              "--name-len", "8", "--out", out])
        n += 1
    return n


def group_d_array_size() -> int:
    n = 0
    for size in [1, 2, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]:
        out = f"array_dint_{size:05d}"
        _run(["tags", "--type", "DINT", "--dims", str(size), "--out", out])
        n += 1
    return n


def group_e_udt_member_count() -> int:
    n = 0
    for count in [1, 2, 4, 8, 16, 32]:
        out = f"udtmembers_n{count:02d}_dint"
        members = [f"M{i}:DINT" for i in range(count)]
        argv = ["udt", "--name", f"SweepN{count:02d}"]
        for m in members:
            argv += ["--member", m]
        argv += ["--instances", "0", "--out", out]
        _run(argv)
        n += 1
    return n


def group_f_udt_member_type() -> int:
    n = 0
    for t in ATOMIC_TYPES:
        out = f"udttype_{t.lower()}_n4"
        argv = ["udt", "--name", f"SweepType{t}"]
        for i in range(4):
            argv += ["--member", f"M{i}:{t}"]
        argv += ["--instances", "0", "--out", out]
        _run(argv)
        n += 1
    return n


def main() -> None:
    total = 0
    for group_fn in [
        group_a_name_length, group_b_atomic_types, group_c_tag_count,
        group_d_array_size, group_e_udt_member_count, group_f_udt_member_type,
    ]:
        count = group_fn()
        print(f"{group_fn.__name__}: {count} file(s)")
        total += count
    print(f"\nTotal: {total} sample(s) generated/updated.")


if __name__ == "__main__":
    main()
