"""OQ-STREAL: Structured Text on the realism floor.

ST routine pricing was measured on near-empty files (`realscale_st_*` and the ST sizing
families). The seventeen real programs carry ~40 ST routines, ~1,510 lines -- likely below the
floor, so this batch is small: the same JSR-called ST routine on the realism floor, sized by
its own content, to confirm the near-empty rates hold on a full controller.

  st_n00        one ST routine of one assignment, called by one JSR -- control
  st_assign400  400 DINT assignments  `StD[i] := StD[i] + 1;`
  st_if100      100 IF / THEN / END_IF blocks, one assignment each
  st_mixed400   400 REAL assignments from a DINT and an integer literal `StR[i] := StD[i] * 2;`

1756-L81E at v35.

Run: python -m sample_gen.gen_st_realism
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml
from sample_gen.gen_st_sizing import _st_routine
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "streal"
CATEGORY = "st_realism"
N = 400


def main() -> None:
    tags = "\n".join([tag_xml("StD", "DINT", (N,)), tag_xml("StR", "REAL", (N,)), tag_xml("StB", "BOOL", (N,))])
    files = {
        "n00": (["StD[0] := StD[0] + 1;"], "control: one ST assignment"),
        "assign400": ([f"StD[{i}] := StD[{i}] + 1;" for i in range(N)], "400 DINT assignments"),
        "if100": ([ln for i in range(100) for ln in (f"IF StB[{i}] THEN", f"    StD[{i}] := StD[{i}] + 1;", "END_IF;")],
                  "100 IF/THEN/END_IF blocks, one assignment each (300 lines)"),
        "mixed400": ([f"StR[{i}] := StD[{i}] * 2;" for i in range(N)],
                     "400 REAL assignments from a DINT times an integer literal"),
    }
    for key, (lines, what) in files.items():
        sample_id = f"streal_{key}"
        out = OUT_ROOT / f"{sample_id}.L5X"
        target = "".join(p.capitalize() for p in sample_id.split("_"))
        l5x = build_l5x(target_name=target, **with_baseline(
            tags_xml=tags, extra_rungs_xml=rung_xml(0, "JSR(StTarget,0);"),
            extra_routines_xml=_st_routine("StTarget", lines)))
        predicted = write_sample(l5x, out)
        append_manifest_row(sample_id, f"OQ-STREAL: {what}, one JSR-called ST routine. Same tags in every "
                                       f"streal_* file, realism floor; differenced against streal_n00.",
                            CATEGORY, out, predicted)
        print(f"Wrote {out.name} (predicted {predicted:,})")


if __name__ == "__main__":
    main()
