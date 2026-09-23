"""OQ-JSRPARAMCOST: how many CALLER routines the JSR base cost is charged to.

The engine carries two per-routine bases: `fixed_base_per_routine` at 4,816
for an ordinary routine and `jsr_fixed_base_per_routine` at 5,096 for a
routine containing a JSR. The 280-byte difference is exactly the residual on
every clean 0-parameter JSR row in the corpus -- flat at 1 through 50 calls
and at every target name length -- while the no-JSR `subrtn_shell` control
predicts at 0.000% at 1, 5, 25 and 100 routines.

`jsr_fixed_base_per_routine` is charged ONCE PER CALLER ROUTINE, not once per
file. Every JSR file in the corpus has exactly ONE caller routine, so
"280 once per file" and "280 per caller routine" fit all of them identically
and no arithmetic separates them. That matters far beyond 280 bytes: a real
export has 60 caller routines, where the two readings differ by roughly
300,000 bytes. The 86 captured files that do have several callers are all
multi-megabyte composites whose residuals run from 10,000 to 94,000 bytes
from unrelated defects, so none of them isolates it either.

This family moves the caller count and NOTHING else.

Total JSR calls is held at 20 and distinct 0-parameter targets at 20 in every
file. Only the distribution changes: with K callers, MainRoutine takes 20/K
calls and K-1 extra caller routines take 20/K each. K runs over the divisors
of 20 -- 1, 2, 4, 5, 10, 20 -- so every caller issues a whole number of calls
and no file carries a remainder routine the others lack.

Across the family the rung text multiset, the instruction inventory, the tag
inventory (empty) and the target set are byte-identical. The only profile
dimension that moves is the routine count, which is the variable itself:
extra caller routines cannot be added without adding routines. A plain extra
routine is separately priced at exactly 280 bytes by `subrtn_shell`, measured
at four counts with zero residual, so that component is already known and
subtracts cleanly.

K=1 reproduces the existing `jsr_multi_distinct_targets_n20` shape, including
its target names, and so is differenced against a capture already in hand as
well as against its own neighbours.

What the slope says:

  ~280 per caller   -- the base is per caller routine, and the engine is
                       over-charging every real program by 280 times its
                       caller count.
  ~0 per caller     -- the base is per file, and the correction is a single
                       flat 280 regardless of how many routines call.

Nothing else in the model distinguishes them, and no refit of the existing
corpus can.

Files are named jsrcallers_k{01..20}. An earlier build of the identical
family was named jsr_callerdist_k*; it never reached the converter and was
renamed so the conversion and capture tooling, which skip any name they have
already seen, treat it as new work.

Run: python -m sample_gen.gen_jsr_caller_distribution
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

# Total JSR calls and total distinct targets, held fixed across the family.
TOTAL_CALLS = 20
# Divisors of TOTAL_CALLS, so every caller issues the same whole number of
# calls and no file carries an odd remainder routine the others lack.
CALLER_COUNTS = (1, 2, 4, 5, 10, 20)
# Every identifier in the family is exactly this long. Target-routine name
# length is a real per-target cost (1 byte/char above 8), so letting it drift
# would put a second dimension into the difference.
NAME_LENGTH = 16


def _padded_name(prefix: str, i: int, total_length: int, index_width: int) -> str:
    # Valid Logix identifier, padded to an exact total length. The zero-padded
    # index is kept intact so names stay distinct at any length.
    idx = str(i).zfill(index_width)
    fill_len = max(total_length - len(prefix) - len(idx), 0)
    name = f"{prefix}{'X' * fill_len}{idx}"
    if len(name) > total_length:
        keep = max(total_length - len(idx), 1)
        name = f"{prefix[:keep]}{idx}"
    return name


def _target_xml(name: str) -> str:
    # 0-param leaf target, no SBR/RET -- the real-corpus norm for 0-param
    # targets. Same shape gen_jsr_multi_distinct_targets_scale.py uses.
    return (
        f'<Routine Name="{name}" Type="RLL">'
        f"<RLLContent>{rung_xml(0, 'NOP();')}</RLLContent>"
        "</Routine>"
    )


def _caller_xml(name: str, targets: list[str]) -> str:
    rungs = "\n".join(rung_xml(i, f"JSR({t},0);") for i, t in enumerate(targets))
    return f'<Routine Name="{name}" Type="RLL"><RLLContent>{rungs}</RLLContent></Routine>'


def group_caller_distribution() -> None:
    # Identical to gen_jsr_multi_distinct_targets_scale.py's names, so K=1
    # differences against the captured jsr_multi_distinct_targets_n20 too.
    target_names = [
        _padded_name("JsrScaleTgt", i, NAME_LENGTH, index_width=2)
        for i in range(TOTAL_CALLS)
    ]
    targets_xml = "\n".join(_target_xml(t) for t in target_names)

    for k in CALLER_COUNTS:
        per_caller = TOTAL_CALLS // k
        chunks = [
            target_names[i * per_caller:(i + 1) * per_caller] for i in range(k)
        ]
        # MainRoutine is always the first caller, so it holds rungs in every
        # file rather than being empty in some and not others.
        main_rungs = "\n".join(
            rung_xml(i, f"JSR({t},0);") for i, t in enumerate(chunks[0])
        )
        extra_callers = "\n".join(
            _caller_xml(_padded_name("JsrCallerRtn", j, NAME_LENGTH, index_width=2), chunk)
            for j, chunk in enumerate(chunks[1:], start=1)
        )
        l5x = build_l5x(
            target_name=f"JsrCallDist{k:02d}",
            tags_xml="",
            extra_rungs_xml=main_rungs,
            extra_routines_xml="\n".join(x for x in (extra_callers, targets_xml) if x),
        )
        out_name = f"jsrcallers_k{k:02d}"
        out_path = OUT_ROOT / f"{out_name}.L5X"
        bytes_ = write_sample(l5x, out_path)
        append_manifest_row(
            out_name,
            f"OQ-JSRCALLERBASE caller-count isolation: {TOTAL_CALLS} JSR calls to {TOTAL_CALLS} "
            f"distinct 0-param leaf targets, distributed across {k} CALLER routine(s) at "
            f"{per_caller} call(s) each (MainRoutine is caller 1). Total calls, total targets, "
            f"rung text, instruction inventory and tag inventory are identical across the whole "
            f"family; the only dimension that moves is the number of routines containing a JSR. "
            f"Separates jsr_fixed_base_per_routine charged PER CALLER ROUTINE from the same cost "
            f"charged ONCE PER FILE -- indistinguishable in every existing capture because every "
            f"JSR file in the corpus has exactly one caller. A plain extra routine is separately "
            f"priced at exactly 280 bytes by subrtn_shell, so the routine-count component "
            f"subtracts cleanly. k=1 reproduces jsr_multi_distinct_targets_n20's shape and names.",
            "jsr_sbr_ret",
            out_path,
            bytes_,
        )
        print(f"Wrote {out_path}  ({k} caller(s) x {per_caller} call(s), predicted {bytes_} bytes)")


def main() -> None:
    group_caller_distribution()
    print(f"\nDone. {len(CALLER_COUNTS)} files.")


if __name__ == "__main__":
    main()
