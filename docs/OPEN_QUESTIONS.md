# Open Questions

**Five.** OQ-OPERANDSHAPE closed negative in the latest batch; three opened with the realism floor (REALISMFLOOR, SERIESREAL, PIOADDR). Closed questions and their reasoning trails are in
`RESOLVED_QUESTIONS.md`; the capture batch after the blind set closed five at once
(JSRCALLERBASE, RUNGSHAPE, ALARMCONDREAL, BUILDFAIL-OPEN, MODULENAMELEN).

## The bar for opening a new one

**State, before any file is built, how many percentage points it should move on the
seventeen real programs and by what mechanism.**

If the mechanism is a category scale, it is already answered: an eight-parameter
per-category fit, fitted directly on the held-out real programs — cheating, an upper
bound no honest procedure can beat — reaches mean 1.01% / max 2.59% and **still
fails** the stopping rule. Under leave-one-out it is worth **0.007 percentage
points**, with half the files getting worse.

So **every question whose mechanism was "a cost constant is slightly wrong" has a
measured maximum payoff of approximately zero**, however cleanly it would answer.
That is why thirty-four closed at once; a thirty-fifth, literal operands, closed on its real-program exposure.

## What is left

| question | state |
|---|---|
| **OQ-REALUNDER** | The real residual: **2.86% mean, 5.42% worst** on the seventeen standard-processor real programs present, after a compensating error was removed. |
| **OQ-PROGSCOPESTRUCT** | Program-scoped UDT and array tags — in 14 of 17 real programs, densest in the three worst, never built. 12 files built, rebuilt on the realism baseline, awaiting capture. |
| **OQ-REALISMFLOOR** | Does the model still hold on a controller that is a quarter full, with I/O, and with every output bit written once? 2 files awaiting capture. |
| **OQ-SERIESREAL** | The −12-per-extra-series-output law, re-measured with no duplicated bits on a full controller. 8 files awaiting capture. |
| **OQ-PIOADDR** | A POINT I/O address vs a controller BOOL vs an alias as a rung operand. 6 files awaiting capture. |

---

## 1. OQ-REALUNDER — the residual itself

**Standard processors only: mean 2.86%, worst 5.42% (after protected-content pricing), every one of the seventeen
standard-processor real programs present under-predicting.** Safety processors are
excluded from accuracy (CLAUDE.md, Platform scope). Including export 13, the one
safety program in the original set: mean 3.12%, worst 6.0% (sum-weighted +3.20%). That is worse than the 1.74% it read before
this batch, and the difference is a correction, not a regression:

- The per-caller `jsr_fixed_base_per_routine` (5,096) had only ever been measured on
  files with ONE caller routine, and was charged to every caller in real programs —
  10 to 87 of them. `jsrcallers_k*` proved a caller costs what any routine costs
  (OQ-JSRCALLERBASE). Removing the over-charge took the real set from 1.74% to 3.40%.
- The AOI argument cost (input references at 28, not 16) moved it back to 3.12%.
- The 2198 family repeat discount moved it to 3.13% — right on the Kinetix files,
  slightly wrong-way on real programs that carry many drives.
- The one-time 264 an RLL file with AOI calls carries moved it to 3.12%.
- Excluding safety processors from accuracy, and pricing structured JSR arguments as
  COP-style copies, leave the standard-processor figure at 3.07%.
- Pricing source-protected AOIs and routines at a minimum brought it to **2.86%**.

So about **3% of every real program is still unexplained**, and the old 1.7% figure was
that 3% partly cancelled by an error. This is CLAUDE.md failure mode 3 exactly, and the
right response is the same: keep the correct term, find the real one.

**What it tracks.** Everything size-like — programs (r = 0.92), routines (0.90),
rungs (0.86), tags (0.85) — and it is about 20% of the engine's `routine_logic` bytes.
No single count explains it under leave-one-out (best single term: JSR calls, LOO mean
1.16%, worst 4.9%), and a term fitted on the real set is not an answer anyway.

**The worst 25 generated files** — every clean standard-processor capture (3,130
rows) recomputed against the current engine, worst by |%|:

| # | file | error | what it is |
|---:|---|---:|---|
| 1–2 | `srout_ote_k08`, `sroutc_c01_k08` | +126% | 1,000 rungs of one XIC then 8 OTEs in a row |
| 3, 5 | `sroutc_c02_k08`, `sroutc_c04_k08` | +118%, +106% | the same with 2 or 4 conditions before the outputs |
| 4, 6, 8 | `srout_ote_k07/k06/k05` | +115% / +102% / +88% | 7, 6, 5 OTEs in a row |
| 7 | `bridge_placeholder_ten` | +95% | 10 ETHERNET-BRIDGE modules, no connections |
| 9 | `srout_branch_k08` | +82% | 8 OTEs in parallel branch legs under one condition |
| 10–14 | `srout_ote_k04`, `srout_same_k04`, `sroutc_*_k04` | +57% to +71% | 4 outputs in a row, same or repeated types |
| 15 | `pioconn_enhanced_n16` | +53% | POINT I/O adapter + 16 1734-IB8 cards, Enhanced (non-rack) connection |
| 16 | `srout_ote_k03` | +52% | 3 OTEs in a row |
| 17 | `srout_branch_k04` | +51% | 4 OTEs in parallel legs |
| 18 | `litop_form_floatform` | −51% | 1,000 `MOV(5.0, DINT)` — float-written literal into an integer |
| 19 | `prodcons_produced` | −49% | 20 Produced tags (force-closed below the noise floor) |
| 20 | `cptnar_j3of6` | −44% | `CPT` into a DINT from REAL operands (known narrowing defect) |
| 21 | `pioconn_enhdata_n16` | +35% | POINT I/O, one InputData connection per card |
| 22 | `srout_mixed_k04` | +33% | OTE, MOV, ADD, CLR in a row |
| 23 | `cptnar_j5of6` | −32% | CPT narrowing again |
| 24 | `closeout_cptmix_ddintoreal_m1` | −32% | CPT into a DINT mixing REAL and DINT operands |
| 25 | `addit_dn_lh` (and 5 more `addit_*_lh`) | +31% | 4,000 rungs of `XIC MOV ADD OTE` — three outputs in a row |

(+ is over-prediction.)

**What they say.** 18 of the 25 are one thing: **series outputs.** Every output after
the first in a rung measures exactly 12 bytes cheaper than its own weight, over 16+
files, and the engine does not apply it because real programs rejected it. Real
programs carry 1,900–11,800 such extra outputs each (0.5–1.5% of their bytes), so
applying the discount would push the real set to ~4% under. The generated corpus and
the real set therefore disagree about multi-output rungs, and the disagreement is the
same order as the gap. Restricting the discount to outputs with no condition between
them still covers ~60% of real extras, so no rewording of the rule fixes it — real
multi-output rungs need to be measured in a real shape.

Nearly every other large miss is an **over**-prediction too (bridge placeholders,
POINT I/O Enhanced cards), while the real set is **under**-predicted. Fixing the
generated corpus's worst rows moves real programs the wrong way: the real gap is
content the generated corpus does not contain, not a mispriced rule it does.

**Eliminated in the latest batch:**

- **Operand shape.** Member paths (`U.Bit`, `U.Sub.Bit`, `UA[2].Bit`, `U.Val`) cost
  exactly what plain tags cost on XIC, OTE and MOV — all 26 `opshape_*` files exact.
- **Trends.** 92 trend definitions across 11 of the 17 programs, unpriced, but the
  residual correlates *negatively* with trend and pen count (r = −0.23).
- **JSR.** Every case now measured and wired; 79 JSR files at 0.02% mean.

**Source-protected content — now priced at a minimum and flagged.** Export 33 carries 39
protected routines (~305,000 encrypted characters) that the engine cannot see; the
engine now lists them as an unpriced gap instead of charging zero silently. It is the
second-worst file, so part of its 5.6% is this, but no calibration from ciphertext to
compiled size exists.

**What distinguishes real programs from the generated files that fit.** The
multi-program composites (`composite_realistic_v3/v4`, `v3abl_*`: 7–11 programs,
JSR callers and targets, AOIs, modules) land within ±1% on the corrected engine. The
largest structural difference between them and real programs is **operand shape** —
see OQ-OPERANDSHAPE.

**Second blind set — exports 37–42, predicted before any reading existed:**

| export | controller | actual | predicted before the reading | error | inside the pre-written range |
|---|---|---:|---:|---:|---|
| 37 | 5069-L330ERMS2 | 1,572,161 | 1,495,547 | −4.87% | yes |
| 38 | 1756-L81ES | 2,007,604 | 1,832,104 | −8.74% | no (below) |
| 39 | 5069-L340ERS2 | 2,935,942 | 2,811,103 | −4.25% | yes |
| 40 | 5069-L320ERMS2 | 1,279,555 | 1,211,456 | −5.32% | yes |
| 41 | 5069-L310ERS2 | 511,973 | 481,589 | −5.93% | no (below) |
| 42 | 1769-L33ERMS | 884,640 | 840,245 | −5.02% | yes — dead architecture, excluded from accuracy |

All six under-predict, by 4.2% to 8.7%; four of six inside the range written down in
advance. **None counts toward accuracy**: five are safety processors and one is a 1769,
both out of scope. They are recorded as evidence of direction only. On the five in scope the mean is 5.82%. Five are safety controllers, but their
safety content is small — one safety program, 2–8% of rungs — and does not explain it.

**Safety memory is a separate partition.** A safety controller keeps safety tags and
safety logic in its own memory, which does not count toward the standard memory that
Capacity reports for standard logic and data. Non-safety tags may not be used in a
safety program; safety tags MAY be used in standard programs, where they cost standard
**logic** (the reference) but not standard **tag** memory. The engine still sizes safety
routine logic (Class="Safety" programs) and Class="Safety" controller tags into the
standard total — 6.7 KB to 22.8 KB on the seven safety files with readings. The measured
296-byte safety task/program shell stays: it was fitted against real standard-memory
readings. Excluding the rest is the correct model and moves those files 0.7 to 1.9
points further under, so it is not the source of the gap.

**The confidence display is not calibrated to real error.** With the Subroutine
Overhead line gone, file confidence reads 97–99% on most real programs (export 07:
99.2%), while their real error is 2–6% (export 27: 98.5% confident, 6.0% wrong). The
bands describe how well each *component* is measured on isolation files; they say
nothing about the unexplained real residual. Until that residual is explained, the
file-level figure must carry it.

### What has been eliminated

Each of these was tested and failed. The full table is in `ROADMAP.md`; the
load-bearing ones:

- **Any per-routine, per-rung, per-program or per-tag constant.** All four are
  collinear with size, so each moves the bias and leaves the spread. **The remaining
  error is not a missing per-unit cost.**
- **Any flat per-file constant.** Swept from 2,000 to 10,000 bytes; every value made
  the mean worse, monotonically. A per-file term moves all files equally, so bias
  improves and spread does not.
- **A global `routine_logic` scale-up.** Ruled out twice — by 578 instruction rows,
  and by direct measurement in both directions on real programs.
- **Tag data space.** Every real tag shape is covered; the untested ones total a few
  thousand bytes. The name-length term is cleared by 88 clean rows at mean 0.12%.

**So both remaining shapes are eliminated: the residual is CONTENT-DEPENDENT.**
Neither counting structural units nor charging every file the same can reach it.

### Not available

Attribution by subtraction from a real export is dead by the read-only rule. The
Studio-side substitute — delete a category in Logix Designer, read Capacity twice — is
declined: each reading costs a bench session. A residual model fitted on the real
programs is judged by leave-one-out only and must beat 0.007 points.

---

## 2. OQ-PROGSCOPESTRUCT — does a UDT or array tag cost the same at program scope?

Program-scoped DINT tags are exact (`tagscope_*`, 10 to 1,000 tags). A program-scoped
**UDT or array** tag has never been built: an element sweep over the seventeen
standard-processor real programs found `Program/Tags/Tag/Data/Structure` and `/Array`
in 14 of them and in no generated file that captured clean. They are densest in the
three worst-predicted programs — exports 27, 06 and 33 carry 102, 118 and 157.

| | |
|---|---|
| **Mechanism** | a per-program tag table, or a per-tag cost for structured program tags, the engine does not charge |
| **Expected movement** | unknown until read; the three worst files carry the most of them |
| **Batch built** | 12 files, `gen_program_scope_struct.py`: the identical UDT tags (7 members) and DINT[20] arrays at controller scope vs program scope, at 10, 50 and 200 tags. 1756-L81E fw35, lint and confound clean. Rebuilt on the realism baseline, identical in all twelve |

---

## 3. OQ-REALISMFLOOR — does the model hold on a full controller?

Every instruction weight was fitted on files that are almost empty: typically under 5%
of the controller, no I/O, and ten BOOLs reused thousands of times
(`gen_logic_sweep._b(i)` is `B{i % 10}`). Real programs fill 16–94%, every standard one
has at least 5 Ethernet I/O nodes, and they reference thousands of distinct tags. If
operand encoding depends on where a tag sits in the data table or how many distinct tags
a routine touches, no calibration file could have seen it.

| | |
|---|---|
| **Mechanism** | an operand or instruction cost that depends on controller fill, data-table offset or distinct-tag count |
| **Expected movement** | up to the whole residual (~2.9 points) if the plant under-predicts at real fill; zero, and the hypothesis eliminated, if it lands exact |
| **Batch built** | `realism_base_f25` (baseline alone, 821,698 predicted, 26% of an L81E) and `realism_base_f50` (plant doubled, 1,591,746). Plant = 1,280 stations, each a UDT instance, a TIMER and ten rungs (seal-in branch, TON and its DN, GRT, ONS+ADD, EQU+OTL, OTU, MOV, LES), all isolation-confirmed instructions, every output bit written once. f25→f50 is a count sweep of a composite unit, so the confound gate flags it; it is read as residual per station, not as one cost |

## 4. OQ-SERIESREAL — the series-output law with no duplicated bits

`OQ-SERIESOUTPUT` measured −12 per output after the first, exactly, on 16+ files —
every one near-empty and, bar the three `srout_oteuniq` files, writing the same bits in
every rung. Applying it to the real set makes every real file worse. 18 of the 25 worst
generated files are this one law.

| | |
|---|---|
| **Mechanism** | the discount belongs to the calibration shape (empty controller, repeated bits), not to series outputs as real ladder has them |
| **Expected movement** | none directly — the law is not wired. If it vanishes here, the engine is right to leave it out and the contradiction is closed; if it holds, real programs carry 0.5–1.5% of bytes the model over-charges, and the true residual is that much larger |
| **Batch built** | 1,600 distinct output BOOLs, each written once, a distinct condition per rung, identical tags in all 8: `realism_srout_series_k{01,02,04,08}` (1600/k rungs of XIC then k OTEs), `_branch_k{02,08}` (parallel legs), `_inter_k{02,08}` (k XIC-OTE pairs per rung — the instruction list of k01 exactly, only rung packing moves) |

**Does the compiler simplify ladder, so that it should be simplified before sizing?**
No. The corpus says it translates what is written, with small local effects only:

- 5,000 byte-identical rungs cost exactly 5,000 × one rung (`instr_mov_n05000`), and
  files writing the same ten BOOLs thousands of times are exactly linear. No duplicate
  or redundant logic is removed.
- `rungpack_xic_k40` puts 40 XICs in series in front of a NOP, which is logic with no
  effect at all, and every XIC is charged at full weight. The files are exact. A
  simplifier would have removed the whole rung.
- The local effects that do exist are peephole-sized. One is this question's −12 per
  output that follows another output: the rung condition is already evaluated. The
  others are the literal-operand differences and CPT's cost following its expression
  tree rather than its text.
- The real set is **under**-predicted. Simplifying before sizing lowers every
  prediction, which is the wrong direction.

**Ten ADDs on one rung vs the same ADDs on separate rungs.** A rung boundary itself
costs nothing measurable: `OQ-RUNGSHAPE` packed 4,000 non-output instructions 1 to 40
per rung and all twelve files were exact. On the calibration files, every output
instruction after the first on a rung is 12 bytes cheaper, whatever its type.
`srout_mixed_k04` (OTE, MOV, ADD, CLR) and four OTEs both read −36. So ten ADDs in
series on one rung measured 9 × 12 = 108 bytes less than ten ADDs on ten rungs. The
real set rejects that rebate, and this question exists to find out why.

## 5. OQ-PIOADDR — POINT I/O address vs controller BOOL vs alias

Real standard programs use 100–1,700 direct module-tag operands each
(`RACK:slot:I.b` is the commonest POINT I/O form: 1,108 input and 510 output uses), and
up to 3,350 alias tags onto I/O. No generated file has ever put a module tag in a rung.

| | |
|---|---|
| **Mechanism** | a module-tag operand resolves through the adapter's rack-optimized connection image, and an alias adds a level; either could cost more than a plain BOOL reference |
| **Expected movement** | per-operand delta × real count: at +8 per operand, 1,500 operands is 12 KB, ~0.2–0.5% on a mid-size program |
| **Batch built** | `realism_pio_{bool,addr,alias}_n{080,160}`: n rungs of `XIC(in)OTE(out)`; controller BOOLs, the RACK_n:slot:I.b / O.b points directly, or alias tags onto them. All 320 BOOLs and 320 aliases declared in all six. 160 is every point the five racks have |
