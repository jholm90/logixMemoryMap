# Open Questions

**One: OQ-REALUNDER.** Closed 2026-10-24 on the capture of batches B and C and the 1769
batch (RESOLVED_QUESTIONS, "Closed 2026-10-24"): OQ-UDTLAYOUT (wired: the aligned layout
predicted all twelve STRING-holding UDT files blind), OQ-STRSHAPE (every shape exact),
OQ-MODREPEAT (zero-connection catalogs wired; the packed 5069 card under the floor),
OQ-SAFETYLOGICIO (Output parameters, safety AOI call operands and slot-path reads wired;
RS-02 / RS-03 / RS-17 read −0.7 / −1.7 / −0.7% safety), OQ-UDTMEMBERNAME (measured, under the
floor) and OQ-CGL1769 (the 1769 programs inside 5% in both partitions). The nineteen standard
programs read **mean 1.158%, worst −2.66%, 18/19 inside 2%** (engine of 2026-10-24).

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

| question | state | answered by |
|---|---|---|
| **OQ-REALUNDER** | **1.158% mean, −2.66% worst, 8/19 inside 1%, 18/19 inside 2%** on the nineteen (2026-10-24, after the UDT layout); stopping rule NOT MET. Section 1. | the residual census below; `docs/REAL_PROGRAM_REPORT.md` |

---

## 1. OQ-REALUNDER — the residual itself

**Now 0.97% mean, 2.57% worst, 10/17 inside 1%** (2026-10-04) after the 92-file batch: InOut operands in AOI logic (+8 per instruction), AOI REAL arguments, AOI scan-mode routines (+268 each), a nested AOI call (+264 per calling definition), the motion literal law on MAJ/MAPC/MCCP/MAG. Worst: export 27 2.57%, export 16 2.23%, export 06 1.70%. Sum-weighted still +0.95%: the set still under-predicts. History below.

**Now 0.77% mean, 3.87% worst on eighteen programs** (export 43 added, with its reading, as a fitting input). The drop from 1.79% came from OQ-INDIRECTUDT (a member, BOOL or STRING element behind a tag-driven index costs 40 / 20 / 108 more than the calibrated 84) and OQ-MIXEDTYPE (DINT↔REAL and DINT↔INT conversions inside one call), both measured on the realism floor and wired with no generated exact row moving. Before that: 1.66% after operand spelling ("Spelling, not cost" below), and 2.86% in the history that follows.

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

### Spelling, not cost — 2.86% → 1.66% with no constant changed

Two measured costs were being charged only when the operand was spelled one way.

1. **The operand-type surcharge** (SINT/INT/REAL/STRING, `operand_type_surcharge`)
   resolved only a BARE controller tag name. A member path (`Stn.Pv`), an array
   element (`Arr[i].Cnt`), an alias, a program-scope tag and an AOI parameter inside
   the AOI's own logic all resolved to nothing and paid DINT rate. Half of all real
   operands are member paths, and OQ-OPERANDSHAPE had already measured a member path
   costing exactly what a plain tag costs. `sizing/operand_types.py` now follows every
   spelling to its type. Real set: 2.86% / 5.42% → **1.98% / 4.89%**, 17 of 17 files
   toward zero, 11–119 KB per file.
2. **The tag-driven index** (84, or 108 with an offset) matched only a bare index tag,
   so `Arr[Stn.Idx]` and `Arr[Stn.Idx+1]` — 2,700 real occurrences — were free. Same
   mechanism, spelled as a member. Real set → **1.66% / 4.83%**, 16 of 17 better;
   exports 18 and 10 land at +23 and −96 bytes (0.00%).

Full census on both changes: all 3,234 captured generated rows **unchanged** (no
calibration file uses either spelling), 18 real rows moved, the only one worse is
export 13, a safety processor excluded from accuracy. Pinned by
`tests/test_operand_types.py`.

**So the calibration corpus's defining habit — bare tag names — hid the gap, not a
wrong constant.** The same audit applies to every other rule keyed on operand text;
the four questions below are the shapes real programs use and no file has measured.

**Leads not yet a mechanism.** After the two fixes, CONCAT count alone fits the
remaining residual at LOO 0.99% (0.82% without export 33) — but at ~900 bytes per
CONCAT, ten times CONCAT's own measured weight, and 1,640 of 1,850 real CONCATs are
plain `STRING` in the calibrated shape. It is a proxy for something string-heavy,
most likely STRING MOV (OQ-STRINGMOV) or string-typed tag content, not a cost.
Export 33 (4.83%) is dominated by 39 source-protected routines the engine cannot see.

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

### Re-scored 2026-10-23: nineteen standard programs, mean 1.262%, worst −2.83%

Every standard-processor program with a reading on disk (the owner's capture of 2026-10-23, read
by the capture tool from the L5X), engine of 2026-10-23, `scripts/quick_eval.py --real-only`:
**mean 1.262%, worst −2.83% (realprog_44), 7/19 inside 1%, 15/19 inside 2%, sum-weighted
−1.29%.** Stopping rule NOT MET. realprog_33 (39 source-protected routines) excluded: −2.97%.
realprog_07, _25, _26, _29, _30 and _31 and _43 had a reading and no file on disk: their records are
deleted (owner, 2026-10-23: the current engine is the only basis, and a reading with no file to
price is no reference). realprog_37 to _42 are the safety-controller programs RS-08, RS-01, RS-10,
RS-05, RS-04 and RS-16 (the last by platform: the only 1769-L33ERMS v32.13 file). Every figure is
also in `docs/REAL_PROGRAM_REPORT.md`, regenerated by `scripts/real_program_report.py`. Labels
key to the git-ignored `samples/local/aliases.csv`; realprog_44 to _47 are new and arrived with their readings (fitting
inputs, not blind).

| label | platform | engine | with the hostlast UDT layout (OQ-UDTLAYOUT, not wired) | |
|---|---|---:|---:|---|
| realprog_44 | 1756-L82E | -2.83% | -2.66% | new 2026-10-23 |
| realprog_16 | 1756-L82E | -2.06% | -1.98% |  |
| realprog_27 | 1756-L81E | -2.04% | -1.98% | re-read -20,456 against the reading on file |
| realprog_46 | 1756-L83E | -2.04% | -1.93% | new 2026-10-23 |
| realprog_36 | 1756-L83E | -1.67% | -1.55% |  |
| realprog_09 | 1756-L83E | -1.51% | -1.33% |  |
| realprog_01 | 1756-L83E | -1.43% | -0.74% |  |
| realprog_06 | 1756-L82E | -1.41% | -0.77% | re-read -19,928 against the reading on file |
| realprog_47 | 1756-L83E | -1.38% | -1.16% | new 2026-10-23 |
| realprog_45 | 1756-L83E | -1.34% | -1.19% | new 2026-10-23 |
| realprog_32 | 1756-L83E | -1.24% | -0.89% |  |
| realprog_35 | 1756-L83E | -1.16% | -0.89% |  |
| realprog_17 | 1756-L81E | -0.88% | -0.82% |  |
| realprog_34 | 1756-L83E | -0.76% | -0.51% |  |
| realprog_08 | 5069-L330ERM | -0.18% | -0.05% | re-read -21,440 against the reading on file |
| realprog_28 | 1756-L81E | +0.24% | +0.34% | re-read -20,936 against the reading on file |
| realprog_14 | 1756-L81E | +0.27% | +0.73% | re-read -728 against the reading on file |
| realprog_10 | 1756-L81E | +0.73% | +0.81% | re-read -24,896 against the reading on file |
| realprog_18 | 1756-L81E | +0.81% | +1.14% | re-read -19,392 against the reading on file |

**Six earlier exports re-read about 20 KB lower** than the reading on file (−19,392 to −24,896;
realprog_14 −728), across programs of 0.9 to 5.2 MB, while ten others re-read to the byte. The
readings on file for those six were not taken by the capture tool from an L5X-built ACD; the new
ones were, as every generated file is. Which one the model should predict is the owner's to
settle (TASKS 0zh); the table uses the new readings.

**What the deep dive found (2026-10-23):**

- **The common shortfall is tag data, and it is UDT layout** (OQ-UDTLAYOUT, Section 6). Scaling
  one category at a time, fitted on the real set as a diagnostic only, `controller_tag` by 2%
  gives the best worst case of any category (LOO 0.74%, max 1.72%). The engine sizes a UDT as the
  plain sum of its members. The one realistic mixed UDT ever captured reads 240 an array element
  against 216 priced, exactly a naturally aligned layout. A layout that also keeps every packed
  capture exact (below) takes the set to **1.130% / −2.66%**, full natural alignment to
  **0.970% / −2.32%**.
- **The scalar AOI law (OQ-AOIBOOLINST) took 0.16 points of mean** (1.099% without it): it
  lowered every program 1 to 40 KB. It is right on 22 isolation files and moved 70 of 75 AOI
  captures closer; it uncovered a shortfall rather than causing one.
- **ST is realprog_44's own extra, not the common term.** realprog_44 carries 3,051 ST
  statements (308 KB priced), the other three over 2% almost none. Its ST is mostly copies
  (DINT 1,100, BOOL 275, INT 234, a custom string 89) through deep member paths with a tag index
  on an array that is itself a member, 1,244 times, a shape no file has measured; at ~45 more a
  site it would carry the program's excess over the common shortfall. Its four unsized
  encoder-diagnostic tags are under 1 KB.
- **Zero-connection modules** on the flat 2,344: realprog_16 carries four peer controllers,
  realprog_47 five, realprog_35 four; batch C's `zcm_*` prices them, in the over-prediction
  direction.
- **Eliminated on these nineteen:** event tasks, periodic tasks, AOI definitions, parameters and
  locals, alarm conditions, documentation volume (rung comments, descriptions, member comments;
  every program downloads its documentation), MSG, aliases, SBR / RET, COP / FLL — none beats a
  uniform size scaling under leave-one-out (0.777% / 2.20%), which is itself a fit on the real set
  and not wired.

### The standard figure on real safety-controller programs — not counted toward accuracy

Safety processors are excluded from accuracy (CLAUDE.md), but their standard Capacity is the
quantity the model predicts, so they are evidence of direction. Engine of 2026-10-23 (unchanged
since 2026-10-21), prediction minus reading: RS-02 −1.89%, RS-03 −0.27%, RS-04u −0.61% (locked
−2.80%), RS-05 −2.38%, RS-06 / RS-09 +1.65% / +1.66%, RS-07 +0.25%, RS-08 −2.45%, RS-10 −2.01%,
RS-17 −0.26%: **mean 1.34%, worst −2.45% on the ten.** RS-01 (−8.19%) stays uncounted: it
carries SFC, which is out of scope.

Where the rest points (2026-10-23):

- **STRINGs held in UDTs.** RS-05 / RS-08 / RS-10 hold 35 to 49% of their predicted bytes in
  scalar tags of UDTs that hold STRINGs, most of them in arrays nested one level down, against 3
  to 5% in RS-02 / RS-03 / RS-07. A STRING member at 88 rather than 86 is worth about 0.6 / 0.35 /
  0.9 points on the three, a custom string at 48 rather than 44 about 0.2 / 0.6 / 0.1 more
  (OQ-STRSHAPE; batch B `strm_*`, batch C `strn_*`).
- **Zero-connection modules on the flat rate**, the other way: RS-07 carries seven (16,408
  bytes at 2,344 each), RS-05 two, RS-10 one; every zero-connection catalog measured costs 320 to
  625 (OQ-MODREPEAT; batch C `zcm_*`). If these read like the others, RS-07 moves to about −0.9%.
- **RS-06 / RS-09's +1.65%** is content priced at v32 (batch B, `safe_base_5069l320_v32`).

A standard array tag's +4 on the realism plant: closed 2026-10-23, BOUNDED (RESOLVED_QUESTIONS,
OQ-ARRAYTAG4).

---
