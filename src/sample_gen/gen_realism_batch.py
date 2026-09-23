"""The first batch on the realism floor (sample_gen/realism.py).

Every file here carries the same baseline: RACK_1..RACK_5 (1734-AENTR/C with
four IB8 and four OB8 each) and a 1,280-station plant that alone predicts over
25% of a 1756-L81E, with every output bit written once. Each arm adds its own
rungs to MainProgram/MainRoutine and its own controller tags, and declares the
SAME tags in every file of the arm, so a pair differs only in rung text.

OQ-REALISMFLOOR -- does the model still hold on a full controller?
  realism_base_f25   the baseline alone (~26% of an L81E)
  realism_base_f50   the plant doubled (~51%)
  Every instruction in the plant has an isolation-confirmed weight, measured on
  near-empty controllers with ten reused BOOLs. If the real set's ~3% under-
  prediction is a fill or address-range effect, it shows here, and f25 against
  f50 says whether it scales with fill.

OQ-SERIESREAL -- the series-output law with no duplicated bits, on a full
controller. 1,600 outputs in every file, each a distinct BOOL written once,
each rung behind its own distinct condition BOOL:
  realism_srout_series_k{01,02,04,08}   1600/k rungs of XIC then k OTEs
  realism_srout_branch_k{02,08}         the same k OTEs in parallel legs
  realism_srout_inter_k{02,08}          k (XIC, OTE) pairs in series per rung
  The generated law is -12 per extra output; the real set rejects it. `inter`
  holds the instruction list of k01 exactly and moves only the rung count, so
  it separates "outputs in series" from "fewer rungs".

OQ-PIOADDR -- does a POINT I/O address cost what a controller BOOL costs?
  realism_pio_{bool,addr,alias}_n{080,160}   n rungs of XIC(in)OTE(out)
  bool:  controller BOOL tags PioDi### / PioDo###
  addr:  the rack-optimized points RACK_n:slot:I.b / RACK_n:slot:O.b directly
  alias: alias tags PioAi### / PioAo### whose AliasFor is those points
  All 320 BOOLs and all 320 aliases are declared in all six files. 160 is
  every point the five racks have. Differenced within a count across the arms,
  and n080 against n160 for the per-rung slope.

1756-L81E at firmware 35.

Run: python -m sample_gen.gen_realism_batch
"""

from __future__ import annotations

from pathlib import Path

from sample_gen import realism
from sample_gen.builders import alias_tag_xml, rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "realism"
CATEGORY = "realism"

SERIES_OUTPUTS = 1600
SERIES_K = (1, 2, 4, 8)
BRANCH_K = (2, 8)
INTER_K = (2, 8)
PIO_COUNTS = (80, 160)

_BASE_NOTE = ("Built on the realism baseline: RACK_1..RACK_5 POINT I/O (AENTR/C + 4 IB8 + 4 OB8), "
              f"a {realism.STATIONS}-station plant over 25% of the controller, every output bit written once.")


def _write(name: str, description: str, stations: int = realism.STATIONS, **arm) -> int:
    l5x = build_l5x(target_name=f"Realism_{name}"[:40], **realism.with_baseline(stations, **arm))
    out = OUT_ROOT / f"realism_{name}.L5X"
    predicted = write_sample(l5x, out)
    append_manifest_row(f"realism_{name}", f"{description} {_BASE_NOTE}", CATEGORY, out, predicted)
    print(f"Wrote {out.name} (predicted {predicted:,})")
    return 1


def _rungs(texts: list[str]) -> str:
    return "\n".join(rung_xml(i, t) for i, t in enumerate(texts))


def group_base() -> int:
    n = _write("base_f25",
               "OQ-REALISMFLOOR: the realism baseline alone, MainRoutine a single NOP. Every "
               "instruction in the plant has an isolation-confirmed weight; differenced against "
               "realism_base_f50 and against its own prediction.", tags_xml="")
    n += _write("base_f50",
                f"OQ-REALISMFLOOR: the baseline with the plant doubled to {2 * realism.STATIONS} "
                f"stations (~51% of the controller). Differenced against realism_base_f25: does "
                f"the per-station residual move with fill?", stations=2 * realism.STATIONS, tags_xml="")
    return n


def _series_tags() -> str:
    return "\n".join([tag_xml(f"SrC{i:04d}", "BOOL") for i in range(SERIES_OUTPUTS)]
                     + [tag_xml(f"SrQ{i:04d}", "BOOL") for i in range(SERIES_OUTPUTS)])


def group_series() -> int:
    tags = _series_tags()
    n = 0
    for k in SERIES_K:
        texts = ["XIC(SrC{:04d})".format(r) + "".join(f"OTE(SrQ{r * k + j:04d})" for j in range(k)) + ";"
                 for r in range(SERIES_OUTPUTS // k)]
        n += _write(f"srout_series_k{k:02d}",
                    f"OQ-SERIESREAL: {SERIES_OUTPUTS // k} rungs of one XIC then {k} OTE(s) in series; "
                    f"{SERIES_OUTPUTS} distinct output BOOLs each written once, a distinct condition per "
                    f"rung. Same tags in every realism_srout_* file. Differenced against "
                    f"realism_srout_series_k01: the generated law is -12 per extra series output, which "
                    f"the real set rejects.", tags_xml=tags, extra_rungs_xml=_rungs(texts))
    for k in BRANCH_K:
        texts = [f"XIC(SrC{r:04d})[" + ",".join(f"OTE(SrQ{r * k + j:04d})" for j in range(k)) + "];"
                 for r in range(SERIES_OUTPUTS // k)]
        n += _write(f"srout_branch_k{k:02d}",
                    f"OQ-SERIESREAL: {SERIES_OUTPUTS // k} rungs of one XIC then {k} OTEs in PARALLEL "
                    f"branch legs; the same outputs as realism_srout_series_k{k:02d}, which it "
                    f"differences against.", tags_xml=tags, extra_rungs_xml=_rungs(texts))
    for k in INTER_K:
        texts = ["".join(f"XIC(SrC{r * k + j:04d})OTE(SrQ{r * k + j:04d})" for j in range(k)) + ";"
                 for r in range(SERIES_OUTPUTS // k)]
        n += _write(f"srout_inter_k{k:02d}",
                    f"OQ-SERIESREAL: {SERIES_OUTPUTS // k} rungs of {k} (XIC, OTE) pairs in series -- "
                    f"exactly the instructions and operands of realism_srout_series_k01 packed {k} to a "
                    f"rung, so the pair differs only in rung count and in outputs following a "
                    f"condition mid-rung.", tags_xml=tags, extra_rungs_xml=_rungs(texts))
    return n


def _pio_tags() -> str:
    ins, outs = realism.input_points(), realism.output_points()
    parts = [tag_xml(f"PioDi{i:03d}", "BOOL") for i in range(len(ins))]
    parts += [tag_xml(f"PioDo{i:03d}", "BOOL") for i in range(len(outs))]
    parts += [alias_tag_xml(f"PioAi{i:03d}", p) for i, p in enumerate(ins)]
    parts += [alias_tag_xml(f"PioAo{i:03d}", p) for i, p in enumerate(outs)]
    return "\n".join(parts)


def group_pio() -> int:
    tags = _pio_tags()
    ins, outs = realism.input_points(), realism.output_points()
    operands = {
        "bool": (lambda i: f"PioDi{i:03d}", lambda i: f"PioDo{i:03d}",
                 "controller BOOL tags PioDi###/PioDo###"),
        "addr": (lambda i: ins[i], lambda i: outs[i],
                 "the rack-optimized POINT I/O points directly (RACK_n:slot:I.b / RACK_n:slot:O.b)"),
        "alias": (lambda i: f"PioAi{i:03d}", lambda i: f"PioAo{i:03d}",
                  "alias tags PioAi###/PioAo### whose AliasFor is those POINT I/O points"),
    }
    n = 0
    for count in PIO_COUNTS:
        for arm, (src, dst, what) in operands.items():
            texts = [f"XIC({src(i)})OTE({dst(i)});" for i in range(count)]
            others = ", ".join(f"realism_pio_{a}_n{count:03d}" for a in operands if a != arm)
            n += _write(f"pio_{arm}_n{count:03d}",
                        f"OQ-PIOADDR: {count} rungs of XIC(in)OTE(out) addressing {what}. All 320 "
                        f"BOOLs and all 320 aliases are declared in every realism_pio_* file, so only "
                        f"the operands move. Differenced against {others}, and against its own other "
                        f"count for the per-rung slope.", tags_xml=tags, extra_rungs_xml=_rungs(texts))
    return n


def main() -> None:
    n = group_base() + group_series() + group_pio()
    print(f"\nDone. {n} files.")


if __name__ == "__main__":
    main()
