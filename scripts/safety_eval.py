"""Reconcile the safe_* batch (OQ-SAFETYPARTITION): what safety content costs in each partition.

Every safe_* file is read twice on the Capacity tab, standard used memory (actual_bytes)
and safety used memory (safety_bytes). Each sweep is differenced against its own control
in both columns, and per-tag / per-rung costs come out of the differences:

  tags         safe_tag_<type>_<n> - safe_n00, per tag; slopes between counts
  name length  safe_tag_dint_50_len<k> - safe_tag_dint_50 (12-character names), per tag,
               beside the standard-side hypothesis 56 + 8 * floor(len / 8)
  scope        safe_tag_dint_50_prog - safe_tag_dint_50
  instruction  safe_<mn>_tags_<n> - safe_n00 per backing tag; safe_<mn>_<n> -
               safe_<mn>_tags_<n> per rung; the slope across counts where there are three
  ordinary     safe_std_<x>_r2 - safe_std_ctl_r2 per rung, beside the engine's standard weight
  reference    safe_ref_<n> - safe_ref_ctl per rung

A row that captured with build errors, or carries a capture flag, is listed and left out of
every figure: suspect, not wrong (CLAUDE.md, step 3).

  python scripts/safety_eval.py            # text report
  python scripts/safety_eval.py --engine   # also price both partitions live (files on disk)
                                           # and report every file's residual in each
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from sample_gen.manifest_store import load_manifest  # noqa: E402

FLAGS = re.compile(r"WINDOW TITLE MISMATCH|ZERO CAPACITY|COUNTER NOT NUMERIC|SAFETY NOT READ|PROCTYPE-UNREAD")


def readings(rows: list[dict]) -> tuple[dict[str, tuple[int, int | None]], list[tuple[str, str]]]:
    """sample_id -> (standard, safety) for clean safe_* captures, and the suspect rows."""
    good: dict[str, tuple[int, int | None]] = {}
    suspect: list[tuple[str, str]] = []
    for r in rows:
        sid = r["sample_id"]
        if not sid.startswith("safe_") or not r.get("actual_bytes"):
            continue
        why = []
        if (r.get("error_count") or "") != "0":
            why.append(f"error_count={r.get('error_count') or 'blank'}")
        if FLAGS.search(r.get("notes") or ""):
            why.append(FLAGS.search(r["notes"]).group(0))
        if why:
            suspect.append((sid, ", ".join(why)))
            continue
        safety = r.get("safety_bytes") or ""
        good[sid] = (int(r["actual_bytes"]), int(safety) if safety.isdigit() else None)
    return good, suspect


def diff(good: dict, a: str, b: str) -> tuple[int, int | None] | None:
    """a - b in both partitions, None if either reading is missing."""
    if a not in good or b not in good:
        return None
    (sa, fa), (sb, fb) = good[a], good[b]
    return sa - sb, (fa - fb if fa is not None and fb is not None else None)


def _per(d: tuple[int, int | None] | None, n: int) -> str:
    if d is None:
        return "not captured"
    std, saf = d
    s = f"std {std:+,} ({std / n:+.2f}/each)"
    s += f", safety {saf:+,} ({saf / n:+.2f}/each)" if saf is not None else ", safety n/a"
    return s


def report(rows: list[dict], engine: dict[str, tuple[int, int]] | None = None) -> str:
    good, suspect = readings(rows)
    out: list[str] = []
    p = out.append
    p(f"safe_* clean captures: {len(good)}; suspect (left out): {len(suspect)}")
    for sid, why in suspect:
        p(f"  SUSPECT {sid}: {why}")

    if "safe_n00" in good:
        std, saf = good["safe_n00"]
        line = f"\ncontrol safe_n00: standard {std:,}, safety {saf if saf is not None else 'n/a'}"
        if engine and "safe_n00" in engine:
            line += f" | engine standard {engine['safe_n00'][0]:,} (residual {std - engine['safe_n00'][0]:+,})"
        p(line + "  [v34 seed File > New safety: 1,394]")

    p("\nsafety tags, controller scope, against safe_n00:")
    for typ, counts in (("bool", (10, 50, 200)), ("dint", (10, 50, 200)), ("real", (50,)), ("int", (50,)), ("sint", (50,))):
        for n in counts:
            p(f"  {typ:4} x{n:<3} {_per(diff(good, f'safe_tag_{typ}_{n}', 'safe_n00'), n)}")
        if len(counts) == 3:
            p(f"  {typ:4} slope 50->200: {_per(diff(good, f'safe_tag_{typ}_200', f'safe_tag_{typ}_50'), 150)}")

    p("\nname length (50 DINTs) against the 12-character names; standard hypothesis 56 + 8*floor(len/8):")
    for length in (4, 20, 40):
        hyp = 8 * (length // 8) - 8 * (12 // 8)
        p(f"  len {length:2}: {_per(diff(good, f'safe_tag_dint_50_len{length}', 'safe_tag_dint_50'), 50)}"
          f"  [hypothesis std {hyp:+}/each]")
    p(f"  program scope vs controller scope: {_per(diff(good, 'safe_tag_dint_50_prog', 'safe_tag_dint_50'), 50)}")

    p("\ninstructions: backing tags against safe_n00, rungs against their own tags-only file:")
    mnemonics = sorted({m.group(1) for sid in good for m in [re.match(r"safe_([a-z0-9]+)_tags_(\d+)$", sid)] if m})
    for mn in mnemonics:
        counts = sorted({int(m.group(1)) for sid in good for m in [re.match(rf"safe_{mn}_tags_(\d+)$", sid)] if m})
        for n in counts:
            p(f"  {mn.upper():6} x{n:<3} tags {_per(diff(good, f'safe_{mn}_tags_{n}', 'safe_n00'), n)}")
            p(f"  {'':6} {'':4} rungs {_per(diff(good, f'safe_{mn}_{n}', f'safe_{mn}_tags_{n}'), n)}")
        if counts == [10, 50, 200]:
            a = diff(good, f"safe_{mn}_200", f"safe_{mn}_tags_200")
            b = diff(good, f"safe_{mn}_10", f"safe_{mn}_tags_10")
            if a and b:
                p(f"  {'':6} rung slope 10->200: {_per((a[0] - b[0], (a[1] - b[1]) if a[1] is not None and b[1] is not None else None), 190)}")

    p("\nordinary instructions in the safety routine, against safe_std_ctl_r2:")
    for sid in sorted(s for s in good if re.match(r"safe_std_.+_\d+_r2$", s)):
        n = int(sid.rsplit("_", 2)[1])
        p(f"  {sid[9:-3]:11} {_per(diff(good, sid, 'safe_std_ctl_r2'), n)}")

    p("\nstandard logic reading safety BOOLs, against safe_ref_ctl:")
    for n in (10, 50, 200):
        p(f"  x{n:<3} {_per(diff(good, f'safe_ref_{n}', 'safe_ref_ctl'), n)}")

    p("\nround 2 (TASKS 0u), per unit, against its control:")
    for label, a, b, n in ROUND2_DIFFS:
        if a in good and b in good:
            p(f"  {label:34} {_per(diff(good, a, b), n)}")
    comp = [r for r in rows if r["sample_id"].startswith("safe_comp_") and r["sample_id"] in good]
    for r in comp:
        m = re.search(r"standard ([\d,]+), safety ([\d,]+)", r.get("description") or "")
        if m:
            ps, pf = (int(x.replace(",", "")) for x in m.groups())
            a_std, a_saf = good[r["sample_id"]]
            line = f"  BLIND {r['sample_id']}: standard {a_std:,} vs {ps:,} ({(a_std - ps) / a_std * 100:+.2f}%)"
            if a_saf is not None:
                line += f", safety {a_saf:,} vs {pf:,} ({(a_saf - pf) / a_saf * 100:+.2f}%)"
            p(line)

    if engine:
        p("\nengine against every clean capture (actual - engine), standard | safety:")
        std_res: dict[int, list[str]] = {}
        saf_res: dict[int, list[str]] = {}
        for sid in sorted(good):
            if sid not in engine:
                continue
            (a_std, a_saf), (e_std, e_saf) = good[sid], engine[sid]
            std_res.setdefault(a_std - e_std, []).append(sid)
            if a_saf is not None:
                saf_res.setdefault(a_saf - e_saf, []).append(sid)
        for label, res in (("standard", std_res), ("safety", saf_res)):
            for r, sids in sorted(res.items(), key=lambda kv: -len(kv[1])):
                p(f"  {label:8} {r:+7,}: {len(sids):3} file(s)" + ("" if len(sids) > 6 else f"  {', '.join(sids)}"))
    return "\n".join(out)


def _round2_diffs() -> list[tuple[str, str, str, int]]:
    """(label, file, control, units) for every round-2 difference."""
    out = [(f"prog DINT name len {k}", f"safe_ptag_dint_50_len{k}", "safe_n00", 50) for k in (4, 8, 16, 24, 40)]
    for shape in ("dint2", "dint3", "dint64", "int3", "sint10", "real10", "bool64", "bool96", "dint4x4", "timer4"):
        out += [(f"array {shape} {sc}", f"safe_arr_{shape}_{sc}", "safe_n00", 20) for sc in ("ctl", "prog")]
    for typ in ("timer", "counter", "control", "lint"):
        out += [(f"{typ} {sc}", f"safe_struct_{typ}_{sc}", "safe_n00", 20) for sc in ("ctl", "prog")]
    for size in ("s", "l"):
        out += [(f"udt {size} definition", f"safe_udt_{size}_def", "safe_n00", 1),
                (f"udt {size} ctl tag", f"safe_udt_{size}_ctl20", f"safe_udt_{size}_def", 20),
                (f"udt {size} prog tag", f"safe_udt_{size}_prog20", f"safe_udt_{size}_def", 20)]
    out += [("alias ctl -> ctl", "safe_alias_tctl_actl", "safe_alias_tctl", 20),
            ("alias prog -> ctl", "safe_alias_tctl_aprog", "safe_alias_tctl", 20),
            ("alias prog -> prog", "safe_alias_tprog_aprog", "safe_alias_tprog", 20)]
    out += [(f"JSR'd subroutines x{n}", f"safe_rtn_jsr_{n}", "safe_n00", n) for n in (1, 2, 5, 10)]
    out += [(f"uncalled routines x{n}", f"safe_rtn_idle_{n}", "safe_n00", n) for n in (1, 5)]
    out += [(f"safety programs x{n} (per extra)", f"safe_prg_{n}", "safe_n00", n - 1) for n in (2, 3, 5)]
    out += [("2nd program name 40 vs 11", "safe_prg_2_len40", "safe_prg_2", 1),
            ("DINT in 2nd program", "safe_prg_2_tags50", "safe_prg_2", 50)]
    for form in ("estop_opprog", "estop_opctl", "estop_oparr", "estop_bctl", "rin_bctl"):
        out += [(f"{form} tags", f"safe_{form}_tags_20", "safe_n00", 20),
                (f"{form} rung", f"safe_{form}_20", f"safe_{form}_tags_20", 20)]
    out += [(f"standard rung, {w}", f"safe_sref_{w}_50", "safe_sref_ctl", 50) for w in ("two", "scalar", "mov", "std")]
    return out


ROUND2_DIFFS = _round2_diffs()


def engine_predictions() -> dict[str, tuple[int, int]]:
    """The current engine's (standard, safety) prediction for every safe_* file on disk."""
    import xml.etree.ElementTree as ET

    from l5x_memory_analyzer.sizing.constants import load_memory_model
    from l5x_memory_analyzer.sizing.report import build_report
    from l5x_memory_analyzer.sizing.safety import build_safety_report
    model = load_memory_model()
    out = {}
    for path in sorted((REPO / "samples" / "generated" / "safety").glob("safe_*.L5X")):
        root = ET.parse(path).getroot()
        out[path.stem] = (sum(e.bytes for e in build_report(root, model)[0]),
                          sum(e.bytes for e in build_safety_report(root, model)[0]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--engine", action="store_true", help="price the standard side live from the files on disk")
    args = ap.parse_args()
    print(report(load_manifest(), engine_predictions() if args.engine else None))


if __name__ == "__main__":
    main()
