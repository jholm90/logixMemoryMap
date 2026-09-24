"""OQ-SERIESREAL: the extra-output discount in the rung shapes real ladder uses.

The -12-per-extra-writing-instruction law is exact on every generated shape built
so far -- series outputs, output-only branch legs, interleaved condition/output
pairs, MOV+OTE -- on an empty controller and on the realism floor. Applied to the
real programs it makes them worse. Surveying the real exports' rungs with two or
more writing instructions, by where the extra outputs sit:

    series, no branch                     27%   measured
    branch, output-only legs              12%   measured
    branch, legs with their own conditions 61%   NEVER BUILT

So this batch builds the dominant real shape and the variations around it. Every
file carries the same tag inventory (SrC/SrQ 1,600 BOOLs each, SrT 1,600 TIMERs,
SrD 400 DINTs, SrV), writes each output bit once, and sits on the realism floor.
The engine does not apply the discount, so each file's residual against
srsty_k01's (or srsty_ton_k01's, for the timer files) is the discount itself:
-12 x extra writers means it applies, 0 means it does not.

  srsty_k01                 XIC(c)OTE(q), 1,600 rungs                 control
  srsty_legs_k{02,04,08}    [XIC(c)OTE(q),XIC(c)OTE(q),...]           legs with own conditions
  srsty_prelegs_k{02,04}    XIC(c)[XIC(c)OTE(q),XIO(c)OTE(q),...]     shared + own conditions
  srsty_legs2_k04           [XIC(c)XIO(c)OTE(q),...]                  two conditions per leg
  srsty_nested_k04          [XIC(c)[OTE(q),OTE(q)],XIC(c)[OTE(q),OTE(q)]]
  srsty_mid_k03             XIC(c)OTE(q)[XIC(c)OTE(q),XIC(c)OTE(q)]   output mid-rung, then legs
  srsty_otl_k04             XIC(c)OTL(q)OTL(q)OTL(q)OTL(q)            series latches
  srsty_mixlegs_k04         [XIC OTE, XIC OTL, XIC MOV, XIC OTE]      mixed writers in legs
  srsty_ton_k01             XIC(c)TON(t,?,?), 1,600 rungs             timer control
  srsty_ton_k04             XIC(c)TON(t)TON(t)TON(t)TON(t)            timers are writers the
  srsty_tonlegs_k04         [XIC(c)TON(t),...]                        counter does not count

Run: python -m sample_gen.gen_series_styles
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml, timer_tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "srstyle"
CATEGORY = "series_style"
N = 1600  # outputs per file
N_DINT = 400


def _c(i: int) -> str:
    return f"SrC{i % N:04d}"


def _q(i: int) -> str:
    return f"SrQ{i:04d}"


def _t(i: int) -> str:
    return f"SrT{i:04d}"


def _inventory() -> str:
    tags = [tag_xml(f"SrC{i:04d}", "BOOL") for i in range(N)]
    tags += [tag_xml(_q(i), "BOOL") for i in range(N)]
    tags += [timer_tag_xml(_t(i)) for i in range(N)]
    tags += [tag_xml(f"SrD{i:04d}", "DINT") for i in range(N_DINT)]
    tags += [tag_xml("SrV", "DINT")]
    return "\n".join(tags)


def _legs(first: int, k: int, leg) -> str:
    return "[" + ",".join(leg(first + j) for j in range(k)) + "]"


def _shapes() -> dict[str, tuple[list[str], str]]:
    s: dict[str, tuple[list[str], str]] = {}
    s["k01"] = ([f"XIC({_c(i)})OTE({_q(i)});" for i in range(N)],
                "1,600 single-output rungs XIC(c)OTE(q): the control for every OTE/OTL/MOV file")
    for k in (2, 4, 8):
        s[f"legs_k{k:02d}"] = (
            [_legs(r * k, k, lambda i: f"XIC({_c(i)})OTE({_q(i)})") + ";" for r in range(N // k)],
            f"{N // k} rungs of {k} branch legs, each leg its own condition and output -- the "
            f"dominant real multi-output shape (61% of real extra outputs)")
    for k in (2, 4):
        s[f"prelegs_k{k:02d}"] = (
            [f"XIC({_c(r * k + N // 2)})"
             + _legs(r * k, k, lambda i: f"{'XIC' if i % 2 == 0 else 'XIO'}({_c(i)})OTE({_q(i)})") + ";"
             for r in range(N // k)],
            f"{N // k} rungs: a shared condition, then {k} legs each with its own XIC/XIO and output")
    s["legs2_k04"] = (
        [_legs(r * 4, 4, lambda i: f"XIC({_c(i)})XIO({_c(i + 1)})OTE({_q(i)})") + ";" for r in range(N // 4)],
        f"{N // 4} rungs of 4 legs, each leg two conditions then an output")
    s["nested_k04"] = (
        [f"[XIC({_c(r * 4)})[OTE({_q(r * 4)}),OTE({_q(r * 4 + 1)})],"
         f"XIC({_c(r * 4 + 2)})[OTE({_q(r * 4 + 2)}),OTE({_q(r * 4 + 3)})]];" for r in range(N // 4)],
        f"{N // 4} rungs: two conditioned legs, each branching again into two outputs")
    mid = [f"XIC({_c(r * 3)})OTE({_q(r * 3)})"
           f"[XIC({_c(r * 3 + 1)})OTE({_q(r * 3 + 1)}),XIC({_c(r * 3 + 2)})OTE({_q(r * 3 + 2)})];"
           for r in range(N // 3)]
    mid += [f"XIC({_c(i)})OTE({_q(i)});" for i in range((N // 3) * 3, N)]
    s["mid_k03"] = (mid, f"{N // 3} rungs: an output mid-rung, then two conditioned legs "
                         f"(plus {N % 3} single-output rung(s) so every output bit is written)")
    s["otl_k04"] = (
        [f"XIC({_c(r * 4)})" + "".join(f"OTL({_q(r * 4 + j)})" for j in range(4)) + ";" for r in range(N // 4)],
        f"{N // 4} rungs: one condition, then 4 latches in series")
    s["mixlegs_k04"] = (
        [f"[XIC({_c(r * 4)})OTE({_q(r * 4)}),XIC({_c(r * 4 + 1)})OTL({_q(r * 4 + 1)}),"
         f"XIC({_c(r * 4 + 2)})MOV(SrV,SrD{r:04d}),XIC({_c(r * 4 + 3)})OTE({_q(r * 4 + 3)})];"
         for r in range(N // 4)],
        f"{N // 4} rungs of 4 conditioned legs with mixed writers: OTE, OTL, MOV, OTE")
    s["ton_k01"] = ([f"XIC({_c(i)})TON({_t(i)},?,?);" for i in range(N)],
                    "1,600 single-timer rungs XIC(c)TON(t): the control for the timer files")
    s["ton_k04"] = (
        [f"XIC({_c(r * 4)})" + "".join(f"TON({_t(r * 4 + j)},?,?)" for j in range(4)) + ";" for r in range(N // 4)],
        f"{N // 4} rungs: one condition, then 4 timers in series")
    s["tonlegs_k04"] = (
        [_legs(r * 4, 4, lambda i: f"XIC({_c(i)})TON({_t(i)},?,?)") + ";" for r in range(N // 4)],
        f"{N // 4} rungs of 4 conditioned legs, one timer each")
    return s


def main() -> None:
    inventory = _inventory()
    for stem, (texts, what) in _shapes().items():
        sample_id = f"srsty_{stem}"
        control = "srsty_ton_k01" if "ton" in stem else "srsty_k01"
        out = OUT_ROOT / f"{sample_id}.L5X"
        rungs = "\n".join(rung_xml(i, t) for i, t in enumerate(texts))
        l5x = build_l5x(target_name="".join(p.capitalize() for p in sample_id.split("_")),
                        **with_baseline(tags_xml=inventory, extra_rungs_xml=rungs))
        predicted = write_sample(l5x, out)
        append_manifest_row(
            sample_id,
            f"OQ-SERIESREAL: {what}. Same tags in every srsty_* file, each output bit written once, "
            f"realism floor. The engine applies no extra-output discount, so the residual against "
            f"{control} is the discount: -12 per extra writer means it holds for this shape, 0 that "
            f"it does not." if stem not in ("k01", "ton_k01") else
            f"OQ-SERIESREAL control: {what}. Same tags in every srsty_* file, realism floor.",
            CATEGORY, out, predicted)
        print(f"Wrote {out} (predicted {predicted:,})")


if __name__ == "__main__":
    main()
